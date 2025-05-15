#!/usr/bin/env python
"""
Demonstration script to show the enhanced conversation handler with knowledge base integration.
"""

import sys
import logging
from app import app
from utils.ai_helper import handle_conversation

logging.basicConfig(level=logging.INFO)

def simulate_conversation(query, user_id=None):
    """Simulate a conversation with the enhanced AI helper."""
    with app.app_context():
        print(f"\n======= User Query =======")
        print(query)
        print("==========================\n")
        
        # Create a simple message history with just the user query
        messages = [{"role": "user", "content": query}]
        
        # Process with knowledge base integration and include debug info
        print("Processing with knowledge base integration...")
        result = handle_conversation(messages, user_id, include_debug=True)
        
        # Display the response with debug info
        print("\n======= AI Response =======")
        print(result['response'])
        print("===========================\n")
        
        # Show debug info about knowledge base usage
        if 'debug' in result:
            debug = result['debug']
            if debug.get('knowledge_used'):
                print("\n--- Knowledge Used In Response ---")
                for i, entry in enumerate(debug['knowledge_used'], 1):
                    print(f"Entry {i} (ID: {entry['id']}, Similarity: {entry['similarity']:.2f})")
                    print(f"Content: {entry['content']}")
                    print(f"Source: {entry['source']}")
                    print(f"Created: {entry['created_at']}")
                    print("-" * 40)
            else:
                print("\nNo relevant knowledge was used from the knowledge base.")
                
            if debug.get('knowledge_added', False):
                print("\nResponse was saved to knowledge base for future use.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_conversation.py \"Your question for Nous\"")
        sys.exit(1)
    
    query = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    simulate_conversation(query, user_id)