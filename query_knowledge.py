#!/usr/bin/env python
"""
Utility script to query the knowledge base.
"""

import sys
import logging
from app import app
from utils.knowledge_helper import query_knowledge_base

logging.basicConfig(level=logging.INFO)

def search_knowledge_base(query, user_id=None, top_k=3, threshold=0.7):
    """Search the knowledge base for entries similar to the query."""
    with app.app_context():
        results = query_knowledge_base(
            query, 
            user_id=user_id, 
            top_k=top_k, 
            similarity_threshold=threshold
        )
        
        if not results:
            print("No relevant knowledge found.")
            return False
            
        print(f"Found {len(results)} relevant knowledge entries:")
        for i, (entry, similarity) in enumerate(results, 1):
            relevance = int(similarity * 100)
            print(f"\n{i}. Relevance: {relevance}%")
            print(f"   Content: {entry.content[:200]}...")
            print(f"   ID: {entry.id}, Source: {entry.source}, Created: {entry.created_at}")
            
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_knowledge.py \"Query to search for\" [user_id] [top_k] [threshold]")
        sys.exit(1)
    
    query = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else None
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
    
    print(f"Searching knowledge base for user: {user_id or 'all users'}")
    print(f"Query: \"{query}\"")
    success = search_knowledge_base(query, user_id, top_k, threshold)
    sys.exit(0 if success else 1)