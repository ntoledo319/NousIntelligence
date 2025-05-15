#!/usr/bin/env python
"""
Utility script to manually add knowledge entries to the knowledge base.
"""

import sys
import os
import logging
import numpy as np
from app import app, db
from models import KnowledgeBase
from datetime import datetime
from openai import OpenAI

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY", "")
if openai_api_key:
    logging.info(f"Using OpenAI API key (first 8 chars): {openai_api_key[:8]}")
else:
    logging.warning("OpenAI API key not found")
openai = OpenAI(api_key=openai_api_key)

def get_embedding_for_text(text):
    """Generate embedding for text using OpenAI API"""
    try:
        logging.info(f"Generating embedding using OpenAI API (API key starts with: {openai_api_key[:8]}...)")
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response.data[0].embedding
        logging.info(f"Successfully generated embedding of size {len(embedding)}")
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        logging.error(f"Error generating embedding: {str(e)}")
        # Return a zero vector as fallback (size 1536 for ada-002)
        return np.zeros(1536, dtype=np.float32)

def add_knowledge_entry_direct(content, user_id=None, source="manual"):
    """Add a new knowledge entry to the database directly."""
    try:
        with app.app_context():
            logging.info(f"Generating embedding for text: {content[:50]}...")
            
            # Generate embedding
            embedding = get_embedding_for_text(content)
            
            # Create new knowledge entry
            entry = KnowledgeBase(
                user_id=user_id,
                content=content,
                source=source,
                relevance_score=1.0
            )
            
            # Set embedding
            logging.info("Setting embedding array...")
            entry.embedding = embedding.astype(np.float32).tobytes()
            
            # Save to database
            logging.info("Adding entry to database...")
            db.session.add(entry)
            db.session.commit()
            
            print(f"✅ Successfully added knowledge entry (ID: {entry.id})")
            return True
    except Exception as e:
        logging.error(f"Error adding to knowledge base: {str(e)}")
        if hasattr(db, 'session'):
            db.session.rollback()
        print(f"❌ Failed to add knowledge entry: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_knowledge.py \"Knowledge content to add\" [user_id] [source]")
        sys.exit(1)
    
    content = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else None
    source = sys.argv[3] if len(sys.argv) > 3 else "manual"
    
    print(f"Adding knowledge entry for user: {user_id or 'global'}")
    success = add_knowledge_entry_direct(content, user_id, source)
    sys.exit(0 if success else 1)