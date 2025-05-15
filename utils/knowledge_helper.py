"""
Knowledge Base Helper - Self-learning mechanism for Nous AI.
This module handles embedding generation, storage, and semantic search.
"""

import os
import json
import logging
import numpy as np
import requests
from datetime import datetime
from openai import OpenAI
from sqlalchemy import desc
from utils.cache_helper import cache_result, get_cached_embedding, cache_embedding

# Import db and models within functions to avoid circular imports
# These will be imported when needed

# Initialize OpenAI client with key directly from .env file
env_path = '.env'
openai_api_key = ""
openrouter_api_key = ""

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY='):
                openai_api_key = line.strip().split('=', 1)[1]
                logging.info("Found OpenAI API key in .env file")
            elif line.strip().startswith('OPENROUTER_API_KEY='):
                openrouter_api_key = line.strip().split('=', 1)[1]
                logging.info("Found OpenRouter API key in .env file")

if openai_api_key:
    logging.info(f"Using OpenAI API key (first 8 chars): {openai_api_key[:8]}")
    # Set in environment for other modules
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    logging.warning("OpenAI API key not found in .env file")

if openrouter_api_key:
    logging.info(f"Using OpenRouter API key (first 8 chars): {openrouter_api_key[:8]}")
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
else:
    logging.warning("OpenRouter API key not found in .env file")

openai = OpenAI(api_key=openai_api_key)

# Cache the model in memory
_embedding_dimension = 1536  # Default for text-embedding-ada-002

# OpenRouter API endpoints
OPENROUTER_BASE_URL = "https://openrouter.ai/api"  # OpenRouter API base URL
OPENROUTER_EMBEDDING_URL = f"{OPENROUTER_BASE_URL}/v1/embeddings"
OPENROUTER_CHAT_COMPLETION_URL = f"{OPENROUTER_BASE_URL}/v1/chat/completions"

def get_embedding_via_openrouter(text):
    """
    Generate embedding using OpenRouter as a fallback service.
    
    Args:
        text (str): The text to embed
        
    Returns:
        numpy.ndarray or None: The embedding vector, or None on failure
    """
    if not openrouter_api_key:
        logging.error("No OpenRouter API key available for fallback")
        return None
    
    try:
        logging.info("Attempting to use OpenRouter for embeddings as fallback")
        
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nous.replit.app/",  # Add proper referer for OpenRouter
            "X-Title": "Nous AI Assistant"  # Add a title for tracking in OpenRouter
        }
        
        payload = {
            "model": "openai/text-embedding-ada-002",  # Compatible model
            "input": text
        }
        
        response = requests.post(
            OPENROUTER_EMBEDDING_URL,
            headers=headers,
            json=payload,
            timeout=30  # Add a reasonable timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
                embedding = result["data"][0]["embedding"]
                logging.info(f"Successfully generated embedding via OpenRouter (size: {len(embedding)})")
                return np.array(embedding, dtype=np.float32)
        
        logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logging.error(f"Error using OpenRouter for embeddings: {str(e)}")
        return None


def get_embedding_for_text(text):
    """
    Generate an embedding for the given text using OpenAI's embedding model.
    With caching to reduce API calls and OpenRouter fallback.
    
    Args:
        text (str): The text to embed
        
    Returns:
        numpy.ndarray: The embedding vector
    """
    # Check if we have a cached embedding for this text
    cached_embedding = get_cached_embedding(text)
    if cached_embedding is not None:
        logging.debug("Using cached embedding")
        return cached_embedding
    
    # Clean and truncate text if needed (API has token limits)
    cleaned_text = text.replace("\n", " ")
    if len(cleaned_text) > 8000:
        logging.warning(f"Truncating text from {len(cleaned_text)} to 8000 chars")
        cleaned_text = cleaned_text[:8000]
    
    # First try OpenAI
    try:
        if openai_api_key:
            logging.info("Generating embedding using OpenAI API")
            
            # Use OpenAI API to generate the embedding
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=cleaned_text
            )
            
            # Extract and convert the embedding
            embedding = response.data[0].embedding
            logging.info(f"Successfully generated embedding of size {len(embedding)}")
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Cache the embedding for future use (24 hour TTL)
            cache_embedding(text, embedding_array, ttl_seconds=86400)
            
            return embedding_array
    except Exception as e:
        logging.error(f"Error generating embedding with OpenAI: {str(e)}")
        
        # If it's a quota error, try OpenRouter
        if "quota" in str(e).lower() or "rate limit" in str(e).lower():
            logging.warning("OpenAI quota exceeded, trying OpenRouter as fallback")
            openrouter_embedding = get_embedding_via_openrouter(cleaned_text)
            if openrouter_embedding is not None:
                # Cache the OpenRouter embedding
                cache_embedding(text, openrouter_embedding, ttl_seconds=86400)
                return openrouter_embedding
    
    # If we get here, both OpenAI and OpenRouter failed (or weren't available)
    # Create a deterministic fallback embedding as last resort
    try:
        logging.warning("Using local fallback embedding generation")
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Use hash to create a deterministic embedding
        expanded = np.resize(np.frombuffer(hash_bytes, dtype=np.uint8), (_embedding_dimension,))
        
        # Normalize to unit length like real embeddings
        norm = np.linalg.norm(expanded)
        fallback_embedding = expanded / norm if norm > 0 else expanded
        
        # Cache the fallback embedding (but with shorter TTL)
        cache_embedding(text, fallback_embedding, ttl_seconds=3600)  # 1 hour TTL for fallbacks
        
        return fallback_embedding
    except:
        # Absolute last resort - zero vector
        return np.zeros(_embedding_dimension, dtype=np.float32)

def add_to_knowledge_base(content, user_id=None, source="conversation"):
    """
    Add new knowledge to the database.
    
    Args:
        content (str): The content to add
        user_id (str, optional): User ID if this is user-specific knowledge
        source (str, optional): Source of the knowledge (conversation, training, reflection)
        
    Returns:
        KnowledgeBase: The newly created knowledge entry
    """
    # Import here to avoid circular imports
    from app import db
    from models import KnowledgeBase
    
    try:
        # Check for duplicates before generating embedding (to save resources)
        existing = KnowledgeBase.query.filter_by(content=content).first()
        if existing:
            logging.info("Duplicate content found, skipping addition to knowledge base")
            return existing
        
        # Generate embedding (will use cached embedding if available)
        embedding = get_embedding_for_text(content)
        
        # Create new knowledge entry
        entry = KnowledgeBase()
        entry.user_id = user_id
        entry.content = content
        entry.source = source
        entry.relevance_score = 1.0  # Start with max relevance
        entry.set_embedding_array(embedding)
        
        # Save to database
        db.session.add(entry)
        db.session.commit()
        
        logging.info(f"Added new knowledge: {content[:50]}...")
        return entry
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding to knowledge base: {str(e)}")
        return None

# Cache knowledge base queries for 15 minutes
@cache_result(ttl_seconds=900)
def query_knowledge_base(question, user_id=None, top_k=3, similarity_threshold=0.75, page=1, batch_size=100):
    """
    Search the knowledge base for entries similar to the question.
    Uses caching to reduce repeated computations and supports pagination for large knowledge bases.
    
    Args:
        question (str): The query
        user_id (str, optional): Limit search to specific user's knowledge
        top_k (int): Number of results to return
        similarity_threshold (float): Minimum similarity score (0-1)
        page (int): Page number for pagination (starts at 1)
        batch_size (int): Number of entries to process per batch
        
    Returns:
        list: List of (entry, similarity) tuples for matching entries
    """
    try:
        # Import here to avoid circular imports
        from app import db
        from models import KnowledgeBase
        
        # Use asynchronous processing for background tasks
        from utils.async_processor import run_async
        
        # Generate query embedding (will use cached embedding if available)
        query_embedding = get_embedding_for_text(question)
        
        # Optimize database query: get only IDs first to reduce data transfer
        query = KnowledgeBase.query.with_entities(KnowledgeBase.id)
        if user_id:
            # Include both user-specific and global knowledge
            query = query.filter((KnowledgeBase.user_id == user_id) | (KnowledgeBase.user_id == None))
        
        # Count total entries for pagination info
        total_entries = query.count()
        
        # Paginate the query for better performance with large databases
        offset = (page - 1) * batch_size
        limited_query = query.order_by(KnowledgeBase.id).offset(offset).limit(batch_size)
        
        entry_ids = [id for (id,) in limited_query.all()]
        if not entry_ids:
            return []
            
        # Batch fetch entries to reduce database load
        entries = KnowledgeBase.query.filter(KnowledgeBase.id.in_(entry_ids)).all()
        
        # Function to compute similarity efficiently
        def compute_similarity(vec1, vec2):
            # Ensure embeddings are non-zero
            if np.all(np.isclose(vec1, 0)) or np.all(np.isclose(vec2, 0)):
                return 0.0
                
            # Calculate norms safely
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            similarity = dot_product / (norm1 * norm2)
            
            # Handle NaN or infinite values
            if np.isnan(similarity) or np.isinf(similarity):
                return 0.0
                
            return float(similarity)
        
        # Compute similarity for each entry
        results = []
        for entry in entries:
            try:
                entry_embedding = entry.get_embedding_array()
                similarity = compute_similarity(query_embedding, entry_embedding)
                
                # For demo purposes, lower the threshold
                effective_threshold = 0.1  # Lower threshold for pseudo-embeddings
                if similarity >= effective_threshold:
                    results.append((entry, similarity))
                    
            except Exception as e:
                logging.error(f"Error computing similarity for entry {entry.id}: {str(e)}")
                continue
        
        # Sort by similarity and get top_k
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:top_k]
        
        # Update access metrics asynchronously to avoid blocking
        @run_async
        def update_access_metrics(entry_ids):
            try:
                from app import app, db
                from models import KnowledgeBase
                
                with app.app_context():
                    entries = KnowledgeBase.query.filter(KnowledgeBase.id.in_(entry_ids)).all()
                    for entry in entries:
                        entry.increment_access()
                    db.session.commit()
                    logging.info(f"Updated access metrics for {len(entries)} knowledge entries")
            except Exception as e:
                logging.error(f"Error updating access metrics: {str(e)}")
                try:
                    db.session.rollback()
                except:
                    pass
        
        # Only update metrics for top results to save resources
        top_entry_ids = [entry.id for entry, _ in top_results]
        if top_entry_ids:
            update_access_metrics(top_entry_ids)
        
        return top_results
    except Exception as e:
        from app import db
        try:
            db.session.rollback()
        except:
            pass
        logging.error(f"Error querying knowledge base: {str(e)}")
        return []

def get_completion_via_openrouter(messages, max_tokens=1000, temperature=0.7):
    """
    Get a completion from OpenRouter as a fallback when OpenAI is unavailable.
    
    Args:
        messages: The messages to send
        max_tokens: Maximum tokens in the response
        temperature: Creativity parameter
        
    Returns:
        str or None: The generated text, or None if failed
    """
    if not openrouter_api_key:
        logging.error("No OpenRouter API key available for fallback")
        return None
    
    try:
        logging.info("Attempting to use OpenRouter for chat completion as fallback")
        
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nous.replit.app/",  # Add proper referer for OpenRouter
            "X-Title": "Nous AI Assistant"  # Add a title for tracking in OpenRouter
        }
        
        # Format messages to be compatible with OpenRouter
        formatted_messages = []
        for message in messages:
            if isinstance(message, dict) and "role" in message and "content" in message:
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            else:
                logging.error(f"Improperly formatted message: {message}")
                return None
        
        payload = {
            "model": "openai/gpt-3.5-turbo",  # More widely available model
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            OPENROUTER_CHAT_COMPLETION_URL,
            headers=headers,
            json=payload,
            timeout=60  # Longer timeout for completions
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                    content = result["choices"][0]["message"]["content"]
                    logging.info("Successfully generated completion via OpenRouter")
                    return content
        
        logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logging.error(f"Error using OpenRouter for completion: {str(e)}")
        return None


def run_self_reflection(user_id=None, max_prompts=3, run_async=False):
    """
    Run the self-reflection routine to improve the knowledge base.
    Can be run asynchronously for better performance.
    
    Args:
        user_id (str, optional): User ID to run reflection for
        max_prompts (int): Maximum number of reflection prompts to process
        run_async (bool): Whether to run the reflection in the background
        
    Returns:
        list or None: List of new knowledge entries added during reflection,
                     or None if running asynchronously
    """
    # Import here to avoid circular imports
    from app import app, db
    from models import ReflectionPrompt
    
    # Function to actually perform the reflection
    def perform_reflection(user_id, max_prompts):
        with app.app_context():
            try:
                # Get reflection prompts that haven't been used recently
                prompts = ReflectionPrompt.query.filter_by(enabled=True).order_by(
                    ReflectionPrompt.last_used.asc()
                ).limit(max_prompts).all()
                
                if not prompts:
                    # Initialize with default prompts if none exist
                    initialize_reflection_prompts()
                    prompts = ReflectionPrompt.query.filter_by(enabled=True).limit(max_prompts).all()
                
                # Track new entries
                new_entries = []
                
                # Process each prompt
                for prompt in prompts:
                    reflection_prompt = f"""You are Nous, a self-learning AI assistant. 
                    Review your knowledge base critically and respond to this prompt:
                    
                    {prompt.prompt}
                    
                    Format your answer as focused knowledge points that will be useful for future interactions.
                    Each knowledge point should be significant and worth remembering.
                    """
                    
                    try:
                        # Create message list
                        messages = [
                            {"role": "system", "content": "You are Nous, an AI personal assistant with self-learning capabilities."},
                            {"role": "user", "content": reflection_prompt}
                        ]
                        
                        reflection_text = None
                        
                        # First try OpenAI
                        if openai_api_key:
                            try:
                                response = openai.chat.completions.create(
                                    model="gpt-4o",  # Use the latest model
                                    messages=messages,
                                    temperature=0.7,
                                    max_tokens=1000
                                )
                                
                                if response.choices and response.choices[0].message:
                                    reflection_text = response.choices[0].message.content
                            except Exception as e:
                                logging.error(f"OpenAI API error: {str(e)}")
                                
                                # If it's a quota error, try OpenRouter
                                if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                                    logging.warning("OpenAI quota exceeded, trying OpenRouter as fallback")
                                    reflection_text = get_completion_via_openrouter(messages)
                        else:
                            # If no OpenAI key, try directly with OpenRouter
                            reflection_text = get_completion_via_openrouter(messages)
                        
                        # Process the response if we got one
                        if reflection_text:
                            reflection_text = reflection_text.strip()
                            
                            # Add reflection to knowledge base
                            entry = add_to_knowledge_base(
                                content=reflection_text,
                                user_id=user_id,
                                source="reflection"
                            )
                            
                            if entry:
                                new_entries.append(entry)
                                
                                # Update prompt usage metrics only if successful
                                prompt.last_used = datetime.utcnow()
                                prompt.use_count += 1
                                db.session.commit()
                        
                    except Exception as e:
                        logging.error(f"Error during reflection for prompt {prompt.prompt[:30]}...: {str(e)}")
                        try:
                            db.session.rollback()
                        except:
                            pass
                        continue
                        
                return new_entries
                
            except Exception as e:
                try:
                    db.session.rollback()
                except:
                    pass
                logging.error(f"Error running self-reflection: {str(e)}")
                return []
    
    # Run asynchronously if requested
    if run_async:
        from utils.async_processor import queue_background_task
        queue_background_task(perform_reflection, user_id, max_prompts)
        logging.info(f"Queued self-reflection task for user {user_id or 'global'}")
        return None
    else:
        # Run synchronously
        return perform_reflection(user_id, max_prompts)

def initialize_reflection_prompts():
    """Initialize default reflection prompts if none exist"""
    default_prompts = [
        {
            "prompt": "What topics or areas in your knowledge base currently have gaps or insufficient detail?",
            "description": "Identifies knowledge gaps",
            "category": "gap-finding"
        },
        {
            "prompt": "Review recent user interactions and identify patterns of questions that were challenging to answer well.",
            "description": "Identifies difficult questions",
            "category": "improvement"
        },
        {
            "prompt": "Are there any inconsistencies or contradictions in your current knowledge? If so, what corrections would resolve them?",
            "description": "Finds knowledge inconsistencies",
            "category": "consistency"
        },
        {
            "prompt": "What are the most important concepts you should understand better to provide more helpful responses?",
            "description": "Identifies key concepts",
            "category": "education"
        },
        {
            "prompt": "What emerging topics or events might require fresh knowledge to provide up-to-date responses?",
            "description": "Identifies trending topics",
            "category": "timeliness"
        }
    ]
    
    try:
        for p in default_prompts:
            prompt = ReflectionPrompt(
                prompt=p["prompt"],
                description=p["description"],
                category=p["category"]
            )
            db.session.add(prompt)
        
        db.session.commit()
        logging.info("Initialized default reflection prompts")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initializing reflection prompts: {str(e)}")

def prune_knowledge_base(user_id=None, max_entries=1000, min_relevance=0.3, run_async=False):
    """
    Prune the knowledge base to prevent it from growing too large.
    Removes the least relevant/accessed entries.
    Can be run asynchronously for better performance.
    
    Args:
        user_id (str, optional): User ID to prune knowledge for
        max_entries (int): Maximum number of entries to keep
        min_relevance (float): Minimum relevance score to keep
        run_async (bool): Whether to run pruning in the background
        
    Returns:
        int or None: Number of entries removed, or None if running asynchronously
    """
    # Import here to avoid circular imports
    from app import app, db
    from models import KnowledgeBase
    
    # Function to actually perform the pruning
    def perform_pruning(user_id, max_entries, min_relevance):
        with app.app_context():
            try:
                # Count entries for this user
                query = KnowledgeBase.query
                if user_id:
                    query = query.filter_by(user_id=user_id)
                
                count = query.count()
                logging.info(f"Knowledge base has {count} entries for user {user_id or 'global'}")
                
                removed_count = 0
                
                # If under the limit, only remove very low relevance entries
                if count <= max_entries:
                    # First get the IDs to delete
                    to_delete_ids = [
                        id for (id,) in query.filter(KnowledgeBase.relevance_score < min_relevance)
                        .with_entities(KnowledgeBase.id).all()
                    ]
                    
                    if to_delete_ids:
                        # Delete in batches to avoid timeout issues
                        batch_size = 100
                        for i in range(0, len(to_delete_ids), batch_size):
                            batch = to_delete_ids[i:i+batch_size]
                            KnowledgeBase.query.filter(KnowledgeBase.id.in_(batch)).delete(synchronize_session=False)
                            db.session.commit()
                            removed_count += len(batch)
                            
                        logging.info(f"Removed {removed_count} low relevance entries (relevance < {min_relevance})")
                else:
                    # Otherwise, remove least valuable entries to get down to max_entries
                    to_remove = count - max_entries
                    
                    # Get entry IDs sorted by relevance and access metrics
                    to_delete_ids = [
                        id for (id,) in query.order_by(
                            KnowledgeBase.relevance_score.asc(),
                            KnowledgeBase.access_count.asc(),
                            KnowledgeBase.last_accessed.asc()
                        ).with_entities(KnowledgeBase.id).limit(to_remove).all()
                    ]
                    
                    if to_delete_ids:
                        # Delete in batches
                        batch_size = 100
                        for i in range(0, len(to_delete_ids), batch_size):
                            batch = to_delete_ids[i:i+batch_size]
                            KnowledgeBase.query.filter(KnowledgeBase.id.in_(batch)).delete(synchronize_session=False)
                            db.session.commit()
                            removed_count += len(batch)
                            
                        logging.info(f"Removed {removed_count} least valuable entries to stay under {max_entries} limit")
                
                return removed_count
                
            except Exception as e:
                try:
                    db.session.rollback()
                except:
                    pass
                logging.error(f"Error pruning knowledge base: {str(e)}")
                return 0
    
    # Run asynchronously if requested
    if run_async:
        from utils.async_processor import queue_background_task
        queue_background_task(perform_pruning, user_id, max_entries, min_relevance)
        logging.info(f"Queued knowledge base pruning task for user {user_id or 'global'}")
        return None
    else:
        # Run synchronously
        return perform_pruning(user_id, max_entries, min_relevance)