"""
Script to pre-load essential knowledge into the knowledge base.
This reduces API calls and improves response time for common queries.
"""

import os
import logging
from flask import Flask
from app import app
from utils.knowledge_download import download_all_knowledge

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Main function to load knowledge into the database."""
    logging.info("Starting knowledge pre-loading process")
    
    with app.app_context():
        # Download all categories of knowledge
        results = download_all_knowledge(force_refresh=False)
        
        # Log the results
        for category, count in results.items():
            logging.info(f"Added {count} entries for category: {category}")
            
        total_entries = sum(results.values())
        logging.info(f"Total knowledge entries added: {total_entries}")
        
    logging.info("Knowledge pre-loading process completed")

if __name__ == "__main__":
    main()