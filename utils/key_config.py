"""
API Key Configuration module.
Handles loading and validating API keys for various services.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys with proper validation
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
HF_ACCESS_TOKEN = os.environ.get("HF_ACCESS_TOKEN", "")

# If OpenAI key is actually an OpenRouter key, clear it to avoid errors
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-"):
    logging.warning("Found OpenRouter key in OPENAI_API_KEY environment variable. Clearing to avoid errors.")
    OPENAI_API_KEY = ""

# Make sure the OpenRouter key is properly set
if not OPENROUTER_API_KEY and os.environ.get("OPENAI_API_KEY", "").startswith("sk-or-"):
    OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Flag to control which AI service to use
USE_OPENROUTER = os.environ.get("USE_OPENROUTER", "True").lower() == "true"

def validate_keys():
    """Validate API keys and log their status"""
    keys_valid = {}
    
    # Check OpenRouter API key
    if OPENROUTER_API_KEY:
        if OPENROUTER_API_KEY.startswith("sk-or-"):
            logging.info("OpenRouter API key found and has correct format")
            keys_valid["openrouter"] = True
        else:
            logging.warning("OpenRouter API key has incorrect format - should start with 'sk-or-'")
            keys_valid["openrouter"] = False
    else:
        logging.warning("OpenRouter API key not found")
        keys_valid["openrouter"] = False
    
    # Check OpenAI API key
    if OPENAI_API_KEY:
        if OPENAI_API_KEY.startswith("sk-"):
            logging.info("OpenAI API key found and has correct format")
            keys_valid["openai"] = True
        else:
            logging.warning("OpenAI API key has incorrect format - should start with 'sk-'")
            keys_valid["openai"] = False
    else:
        logging.warning("OpenAI API key not found")
        keys_valid["openai"] = False
    
    # Log overall AI service status
    if USE_OPENROUTER:
        if keys_valid["openrouter"]:
            logging.info("Using OpenRouter as primary AI service")
        else:
            if keys_valid["openai"]:
                logging.warning("OpenRouter selected but key invalid, falling back to OpenAI")
            else:
                logging.error("No valid AI service keys found")
    else:
        if keys_valid["openai"]:
            logging.info("Using OpenAI as primary AI service")
        else:
            if keys_valid["openrouter"]:
                logging.warning("OpenAI selected but key invalid, falling back to OpenRouter")
            else:
                logging.error("No valid AI service keys found")
                
    return keys_valid

def get_preferred_service():
    """Get the preferred AI service based on available keys and configuration"""
    keys_valid = validate_keys()
    
    if USE_OPENROUTER and keys_valid["openrouter"]:
        return "openrouter"
    elif not USE_OPENROUTER and keys_valid["openai"]:
        return "openai"
    elif keys_valid["openrouter"]:
        return "openrouter"
    elif keys_valid["openai"]:
        return "openai"
    else:
        return None