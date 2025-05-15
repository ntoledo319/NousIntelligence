#!/usr/bin/env python
"""
Test script for OpenAI and OpenRouter API keys.

This script verifies that the API keys are valid and the API endpoints
are accessible. It will try both OpenAI and OpenRouter APIs.
"""

import os
import sys
import logging
import requests
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Get API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

def test_openai_api():
    """Test OpenAI API key and endpoint."""
    
    if not OPENAI_API_KEY:
        logging.error("OpenAI API key not found in environment variables")
        return False
    
    try:
        # Simple models list API call to check access
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        
        logging.info("Testing OpenAI API access...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ OpenAI API access successful")
            # Show a few available models
            models = response.json().get("data", [])
            if models:
                logging.info("Available models:")
                for model in models[:5]:  # Just show a few
                    logging.info(f"  - {model.get('id')}")
            return True
        else:
            logging.error(f"❌ OpenAI API access failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logging.error(f"❌ Error testing OpenAI API: {str(e)}")
        return False

def test_openrouter_api():
    """Test OpenRouter API key and endpoints."""
    
    if not OPENROUTER_API_KEY:
        logging.error("OpenRouter API key not found in environment variables")
        return False
    
    try:
        # Test with a models list request
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://nous.replit.app/",
            "X-Title": "Nous AI Assistant"
        }
        
        logging.info("Testing OpenRouter API access...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ OpenRouter API access successful")
            # Show available models
            models = response.json()
            if models:
                logging.info("Available models:")
                for model in models['data'][:5]:  # Just show a few
                    logging.info(f"  - {model.get('id')}")
            return True
        else:
            logging.error(f"❌ OpenRouter API access failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logging.error(f"❌ Error testing OpenRouter API: {str(e)}")
        return False

def main():
    """Run the API key tests."""
    print("\n=== Testing AI API Keys ===\n")
    
    openai_success = test_openai_api()
    print("\n" + "-" * 50 + "\n")
    openrouter_success = test_openrouter_api()
    
    print("\n=== Test Summary ===")
    print(f"OpenAI API: {'✅ PASSED' if openai_success else '❌ FAILED'}")
    print(f"OpenRouter API: {'✅ PASSED' if openrouter_success else '❌ FAILED'}")
    
    # Return overall success status for shell usage
    return 0 if (openai_success or openrouter_success) else 1

if __name__ == "__main__":
    sys.exit(main())