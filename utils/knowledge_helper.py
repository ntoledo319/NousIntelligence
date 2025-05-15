"""
Knowledge Base Helper - Self-learning mechanism for Nous AI.
This module handles embedding generation, storage, and semantic search.
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from openai import OpenAI
from app import db
from models import KnowledgeBase, ReflectionPrompt, User
from sqlalchemy import desc

# Initialize OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY", "")
if openai_api_key:
    logging.info(f"Using OpenAI API key (first 8 chars): {openai_api_key[:8]}")
else:
    logging.warning("OpenAI API key not found")
    
# Make sure we're using the key from the environment
openai = OpenAI(api_key=openai_api_key)

# Cache the model in memory
_embedding_dimension = 1536  # Default for text-embedding-ada-002

def get_embedding_for_text(text):
    """
    Generate an embedding for the given text using OpenAI's embedding model.
    
    Args:
        text (str): The text to embed
        
    Returns:
        numpy.ndarray: The embedding vector
    """
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        logging.error(f"Error generating embedding: {str(e)}")
        # Return a zero vector as fallback
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
    try:
        # Generate embedding
        embedding = get_embedding_for_text(content)
        
        # Create new knowledge entry
        entry = KnowledgeBase(
            user_id=user_id,
            content=content,
            source=source,
            relevance_score=1.0  # Start with max relevance
        )
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

def query_knowledge_base(question, user_id=None, top_k=3, similarity_threshold=0.75):
    """
    Search the knowledge base for entries similar to the question.
    
    Args:
        question (str): The query
        user_id (str, optional): Limit search to specific user's knowledge
        top_k (int): Number of results to return
        similarity_threshold (float): Minimum similarity score (0-1)
        
    Returns:
        list: List of (entry, similarity) tuples for matching entries
    """
    try:
        # Generate query embedding
        query_embedding = get_embedding_for_text(question)
        
        # Get all knowledge entries (could be optimized with an index)
        query = KnowledgeBase.query
        if user_id:
            # Include both user-specific and global knowledge
            query = query.filter((KnowledgeBase.user_id == user_id) | (KnowledgeBase.user_id == None))
        
        entries = query.all()
        if not entries:
            return []
            
        # Compute similarity for each entry
        results = []
        for entry in entries:
            entry_embedding = entry.get_embedding_array()
            # Compute cosine similarity
            similarity = np.dot(query_embedding, entry_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(entry_embedding)
            )
            
            if similarity >= similarity_threshold:
                results.append((entry, float(similarity)))
                # Update access metrics
                entry.increment_access()
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Commit the access metric updates
        db.session.commit()
        
        return results[:top_k]
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error querying knowledge base: {str(e)}")
        return []

def run_self_reflection(user_id=None, max_prompts=3):
    """
    Run the self-reflection routine to improve the knowledge base.
    
    Args:
        user_id (str, optional): User ID to run reflection for
        max_prompts (int): Maximum number of reflection prompts to process
        
    Returns:
        list: List of new knowledge entries added during reflection
    """
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
        
        # Query OpenAI for each prompt
        for prompt in prompts:
            reflection_prompt = f"""You are Nous, a self-learning AI assistant. 
            Review your knowledge base critically and respond to this prompt:
            
            {prompt.prompt}
            
            Format your answer as focused knowledge points that will be useful for future interactions.
            Each knowledge point should be significant and worth remembering.
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",  # Use the latest model
                    messages=[
                        {"role": "system", "content": "You are Nous, an AI personal assistant with self-learning capabilities."},
                        {"role": "user", "content": reflection_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                reflection_text = response.choices[0].message.content.strip()
                
                # Add reflection to knowledge base
                entry = add_to_knowledge_base(
                    content=reflection_text,
                    user_id=user_id,
                    source="reflection"
                )
                
                if entry:
                    new_entries.append(entry)
                
                # Update prompt usage metrics
                prompt.last_used = datetime.utcnow()
                prompt.use_count += 1
                db.session.commit()
                
            except Exception as e:
                logging.error(f"Error during reflection for prompt {prompt.id}: {str(e)}")
                continue
                
        return new_entries
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error running self-reflection: {str(e)}")
        return []

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

def prune_knowledge_base(user_id=None, max_entries=1000, min_relevance=0.3):
    """
    Prune the knowledge base to prevent it from growing too large.
    Removes the least relevant/accessed entries.
    
    Args:
        user_id (str, optional): User ID to prune knowledge for
        max_entries (int): Maximum number of entries to keep
        min_relevance (float): Minimum relevance score to keep
        
    Returns:
        int: Number of entries removed
    """
    try:
        # Count entries for this user
        query = KnowledgeBase.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        count = query.count()
        
        # If under the limit, only remove very low relevance entries
        if count <= max_entries:
            result = query.filter(KnowledgeBase.relevance_score < min_relevance).delete()
            db.session.commit()
            return result
            
        # Otherwise, remove least valuable entries to get down to max_entries
        to_remove = count - max_entries
        
        # Get entries sorted by relevance and access metrics
        entries = query.order_by(
            KnowledgeBase.relevance_score.asc(),
            KnowledgeBase.access_count.asc(),
            KnowledgeBase.last_accessed.asc()
        ).limit(to_remove).all()
        
        # Delete entries
        for entry in entries:
            db.session.delete(entry)
            
        db.session.commit()
        return len(entries)
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error pruning knowledge base: {str(e)}")
        return 0