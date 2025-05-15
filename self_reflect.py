#!/usr/bin/env python
"""
Self-Reflection Script for Nous AI

This script performs a self-reflection routine on the knowledge base,
identifying gaps and opportunities for improvement.

It should be run daily via Replit's built-in cron system with:
python self_reflect.py
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("self_reflection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables
load_dotenv()

def main():
    """Main entry point for self-reflection script"""
    parser = argparse.ArgumentParser(description="Nous AI Self-Reflection Tool")
    parser.add_argument('--max-prompts', type=int, default=5, 
                        help='Maximum number of reflection prompts to process')
    parser.add_argument('--user-id', type=str, 
                        help='Run self-reflection for a specific user ID')
    parser.add_argument('--prune', action='store_true', 
                        help='Prune knowledge base after reflection')
    parser.add_argument('--max-entries', type=int, default=1000, 
                        help='Maximum entries to keep when pruning')
    
    args = parser.parse_args()
    
    # We need to import here to ensure app context is properly set up
    from app import app
    with app.app_context():
        from utils.knowledge_helper import run_self_reflection, prune_knowledge_base
        
        logging.info(f"Starting self-reflection at {datetime.now().isoformat()}")
        
        # Run the reflection process
        new_entries = run_self_reflection(
            user_id=args.user_id,
            max_prompts=args.max_prompts
        )
        
        logging.info(f"Self-reflection added {len(new_entries)} new knowledge entries")
        
        # Prune knowledge base if requested
        if args.prune:
            removed_count = prune_knowledge_base(
                user_id=args.user_id,
                max_entries=args.max_entries
            )
            logging.info(f"Pruned {removed_count} entries from knowledge base")
        
        logging.info(f"Self-reflection completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error in self-reflection: {str(e)}", exc_info=True)
        sys.exit(1)