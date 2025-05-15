#!/usr/bin/env python
"""
Utility to download and load knowledge into the knowledge base.
This script runs the knowledge pre-downloader to ensure the database
has essential information.
"""

import sys
import logging
import time
from app import app
from utils.knowledge_download import download_all_knowledge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Download and load all predefined knowledge categories."""
    
    with app.app_context():
        force_refresh = "--force" in sys.argv
        
        logging.info("Starting knowledge download process")
        logging.info(f"Force refresh: {force_refresh}")
        
        start_time = time.time()
        
        # Download all knowledge categories
        results = download_all_knowledge(force_refresh=force_refresh)
        
        # Output results
        total_entries = sum(results.values())
        duration = time.time() - start_time
        
        logging.info(f"Knowledge download complete.")
        logging.info(f"Added {total_entries} total entries across {len(results)} categories.")
        logging.info(f"Process took {duration:.2f} seconds.")
        
        # Print breakdown by category
        logging.info("\nBreakdown by category:")
        for category, count in results.items():
            logging.info(f"  {category}: {count} entries")
            
        return total_entries

if __name__ == "__main__":
    main()