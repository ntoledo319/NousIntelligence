#!/usr/bin/env python
"""
Utility script to manually add knowledge entries to the knowledge base.
"""

import sys
import logging
from app import app
from utils.knowledge_helper import add_to_knowledge_base

logging.basicConfig(level=logging.INFO)

def add_knowledge_entry(content, user_id=None, source="manual"):
    """Add a new knowledge entry to the database."""
    with app.app_context():
        entry = add_to_knowledge_base(content, user_id, source)
        if entry:
            print(f"✅ Successfully added knowledge entry (ID: {entry.id})")
            return True
        else:
            print("❌ Failed to add knowledge entry")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_knowledge.py \"Knowledge content to add\" [user_id] [source]")
        sys.exit(1)
    
    content = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else None
    source = sys.argv[3] if len(sys.argv) > 3 else "manual"
    
    print(f"Adding knowledge entry for user: {user_id or 'global'}")
    success = add_knowledge_entry(content, user_id, source)
    sys.exit(0 if success else 1)