#!/usr/bin/env python
"""
Debug utility to check embeddings in the knowledge base.
"""

import sys
import logging
import numpy as np
from app import app, db
from models import KnowledgeBase

logging.basicConfig(level=logging.INFO)

def check_knowledge_embeddings():
    """Check embeddings for all knowledge entries."""
    with app.app_context():
        entries = KnowledgeBase.query.all()
        
        print(f"\nFound {len(entries)} knowledge entries in the database")
        
        for entry in entries:
            print(f"\n\n--- Entry {entry.id} ---")
            print(f"Content: {entry.content[:100]}...")
            
            # Get the embedding as a NumPy array
            try:
                embedding = entry.get_embedding_array()
                norm = np.linalg.norm(embedding)
                
                print(f"Embedding shape: {embedding.shape}")
                print(f"Embedding type: {embedding.dtype}")
                print(f"Embedding norm: {norm}")
                print(f"Is all zeros: {np.allclose(embedding, 0)}")
                
                # Show some stats about the embedding
                print(f"Mean: {np.mean(embedding)}")
                print(f"Std: {np.std(embedding)}")
                print(f"Min: {np.min(embedding)}")
                print(f"Max: {np.max(embedding)}")
                
                # Show first few values
                print(f"First 5 values: {embedding[:5]}")
                
                # Update embedding if it's all zeros
                if np.allclose(embedding, 0):
                    print("\nThis embedding is all zeros. Generating a new pseudo-embedding...")
                    
                    # Create a deterministic pseudo-embedding based on content hash
                    import hashlib
                    import random
                    
                    hash_obj = hashlib.md5(entry.content.encode())
                    hash_bytes = hash_obj.digest()
                    random.seed(hash_bytes)
                    
                    # Generate a pseudo-embedding
                    pseudo_embedding = np.array([random.uniform(-1, 1) for _ in range(1536)], dtype=np.float32)
                    # Normalize to unit length
                    pseudo_embedding = pseudo_embedding / np.linalg.norm(pseudo_embedding)
                    
                    # Update the entry
                    entry.set_embedding_array(pseudo_embedding)
                    db.session.commit()
                    
                    print("Updated with new pseudo-embedding")
                    
            except Exception as e:
                print(f"Error processing embedding: {str(e)}")

if __name__ == "__main__":
    check_knowledge_embeddings()