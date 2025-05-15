#!/usr/bin/env python
"""
Demonstration script to show how the knowledge base is integrated into Nous.
This simulates the entire knowledge retrieval and AI response process.
"""

import os
import sys
import logging
import json
from app import app, db
from models import KnowledgeBase
import numpy as np
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client with key directly from .env file
env_path = '.env'
openai_api_key = ""
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY='):
                openai_api_key = line.strip().split('=', 1)[1]
                break

if openai_api_key:
    logging.info(f"Using OpenAI API key (first 8 chars): {openai_api_key[:8]}")
else:
    logging.warning("OpenAI API key not found in .env file")

openai = OpenAI(api_key=openai_api_key)

def compute_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    # Handle zero vectors
    if np.all(np.isclose(vec1, 0)) or np.all(np.isclose(vec2, 0)):
        return 0
        
    # Calculate norms safely
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
        
    # Compute similarity
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
    
    # Handle NaN
    if np.isnan(similarity) or np.isinf(similarity):
        return 0
        
    return similarity

def get_pseudo_embedding(text):
    """Create a deterministic pseudo-embedding based on text hash."""
    import hashlib
    import random
    
    # Create a deterministic hash
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Use hash to seed a random generator
    random.seed(hash_bytes)
    
    # Generate a pseudo-embedding
    embedding = np.array([random.uniform(-1, 1) for _ in range(1536)], dtype=np.float32)
    
    # Normalize to unit length
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding

def query_knowledge_base_direct(query, threshold=0.00001):
    """Directly query the knowledge base with a user question. 
    Using very low threshold for demo purposes."""
    with app.app_context():
        # Generate query embedding
        query_embedding = get_pseudo_embedding(query)
        
        # Fetch all knowledge entries
        entries = KnowledgeBase.query.all()
        if not entries:
            print("No knowledge entries found in database")
            return []
            
        # Compute similarity and collect results
        results = []
        for entry in entries:
            try:
                # Get entry embedding
                entry_embedding = entry.get_embedding_array()
                
                # Compute similarity score
                similarity = compute_similarity(query_embedding, entry_embedding)
                
                # For demo, use a much lower threshold
                if similarity >= threshold:
                    results.append((entry, float(similarity)))
                    
            except Exception as e:
                logging.error(f"Error processing entry {entry.id}: {str(e)}")
                continue
                
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:3]  # Return top 3

def simulate_ai_response(query, knowledge):
    """Simulate generating an AI response with knowledge context."""
    try:
        # If we have relevant knowledge
        if knowledge:
            # Format knowledge context
            context = "\n\n".join([f"[Context {i+1}] {entry.content}" 
                                 for i, (entry, _) in enumerate(knowledge)])
            
            # Simply print what would be sent to OpenAI
            print("\n--- In a real scenario, this would be sent to OpenAI: ---")
            prompt = f"""You are Nous, an AI personal assistant with a self-learning knowledge base. 
            Use the following relevant information from your knowledge base to help answer the user's question.
            
            {context}
            
            User question: {query}
            
            Based on the above context from your knowledge base, provide a helpful response to the user's question.
            Your response should feel natural and not explicitly reference the knowledge base."""
            
            print(prompt)
            print("--- End of prompt ---\n")
            
            # In a real scenario, we would call OpenAI API, but for demo purposes
            # we'll construct a simulated response
            print("Simulated AI Response:")
            print("="*50)
            print(f"Based on my knowledge, Nous (that's me!) learns from conversations by storing important information in a self-learning knowledge base. This allows me to remember key details from our interactions and use them to provide more personalized and accurate responses over time.")
            print("="*50)
        else:
            print("\nNo relevant knowledge found, would fall back to standard AI response without context")
    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")

def run_demo(query):
    """Run the knowledge base demo with the given query."""
    print(f"Demo query: '{query}'")
    
    # Query the knowledge base
    print("\nSearching knowledge base...")
    results = query_knowledge_base_direct(query)
    
    # Display results
    if results:
        print(f"\n✅ Found {len(results)} relevant entries:\n")
        for i, (entry, similarity) in enumerate(results, 1):
            print(f"--- Knowledge entry {i} (Similarity: {similarity:.2f}) ---")
            print(f"ID: {entry.id}")
            print(f"Content: {entry.content}")
            print("-" * 40)
    else:
        print("❌ No relevant knowledge found")
    
    # Generate a simulated AI response
    print("\nGenerating AI response...")
    simulate_ai_response(query, results)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_knowledge_base.py \"Your question about Nous\"")
        sys.exit(1)
    
    query = sys.argv[1]
    run_demo(query)