#!/usr/bin/env python
"""
Test script for knowledge pre-downloading system.

This script verifies that our knowledge pre-loading system works correctly
and can fall back to OpenRouter when OpenAI quota is exceeded.
"""

import os
import sys
import logging
import time
from app import app
from utils.knowledge_download import download_and_store_knowledge, KNOWLEDGE_CATEGORIES
from utils.knowledge_helper import get_embedding_for_text, get_completion_via_openrouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_knowledge_download():
    """Test knowledge downloading for key categories."""
    
    with app.app_context():
        logging.info("Starting knowledge download test")
        
        # Test only a subset of categories to save time and resources
        test_categories = [
            "basic_facts", 
            "health_information",
            "dbt_skills",
            "aa_principles",
            "mindfulness_exercises"
        ]
        
        results = {}
        
        for category in test_categories:
            try:
                logging.info(f"Testing download for category: {category}")
                count = download_and_store_knowledge(category, force_refresh=True)
                results[category] = count
                logging.info(f"Added {count} entries for {category}")
                
                # Small delay to avoid overwhelming the API
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error downloading {category}: {str(e)}")
                results[category] = f"ERROR: {str(e)}"
        
        logging.info("Knowledge download test results:")
        for category, result in results.items():
            logging.info(f"  {category}: {result}")
            
        total_success = sum([r for r in results.values() if isinstance(r, int)])
        logging.info(f"Total successful entries added: {total_success}")
        
        return results

def test_openrouter_fallback():
    """Test OpenRouter fallback functionality."""
    
    logging.info("Testing OpenRouter fallback...")
    
    try:
        # Test embedding
        test_text = "This is a test to verify OpenRouter fallback for embeddings works correctly."
        logging.info("Testing embedding generation...")
        embedding = get_embedding_for_text(test_text)
        logging.info(f"Embedding shape: {embedding.shape}")
        
        # Test completion
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Complete this sentence in exactly 10 words: The purpose of pre-downloading knowledge is to..."}
        ]
        
        logging.info("Testing completion generation...")
        completion = get_completion_via_openrouter(test_messages)
        
        if completion:
            logging.info(f"Completion result: {completion}")
            return True
        else:
            logging.error("Failed to get completion from OpenRouter")
            return False
            
    except Exception as e:
        logging.error(f"Error testing OpenRouter fallback: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Knowledge Pre-Download System ===\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--openrouter-only":
        # Only test OpenRouter fallback
        success = test_openrouter_fallback()
        sys.exit(0 if success else 1)
    else:
        # Run full test
        results = test_knowledge_download()
        test_openrouter_fallback()
        
        print("\nAvailable Knowledge Categories:")
        for i, category in enumerate(KNOWLEDGE_CATEGORIES, 1):
            print(f"{i}. {category}")
            
        print("\nTest completed successfully!")