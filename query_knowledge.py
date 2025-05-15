#!/usr/bin/env python
"""
Utility script to test querying the knowledge base.
"""

import sys
import logging
from app import app
from utils.knowledge_helper import query_knowledge_base

logging.basicConfig(level=logging.INFO)

def search_knowledge_base(query, user_id=None):
    """Search for relevant knowledge in the database."""
    with app.app_context():
        # Debug - print all knowledge entries first
        from models import KnowledgeBase
        all_entries = KnowledgeBase.query.all()
        print(f"\nAll knowledge entries ({len(all_entries)}):")
        for entry in all_entries:
            print(f"ID {entry.id}: {entry.content[:50]}...")
        
        print("\nSearching for relevant entries with very low threshold...")
        
        # Use an extremely low threshold for testing purposes
        results = query_knowledge_base(query, user_id, similarity_threshold=0.001, top_k=5)
        if results:
            print(f"\n✅ Found {len(results)} relevant entries:\n")
            for i, (entry, similarity) in enumerate(results, 1):
                print(f"\n--- Result {i} (Similarity: {similarity:.2f}) ---")
                print(f"ID: {entry.id}")
                print(f"Content: {entry.content}")
                print(f"Source: {entry.source}")
                print(f"Created: {entry.created_at}")
                print(f"User ID: {entry.user_id or 'global'}")
                print("-" * 40)
            return True
        else:
            print("❌ No relevant knowledge found in the database")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_knowledge.py \"Query text to search for\"")
        sys.exit(1)
    
    query = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Searching knowledge base for: '{query}'")
    if user_id:
        print(f"Limiting to user: {user_id}")
    
    success = search_knowledge_base(query, user_id)
    sys.exit(0 if success else 1)