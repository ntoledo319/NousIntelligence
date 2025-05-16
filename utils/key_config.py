"""
API Key Configuration Module

This module handles loading, validation, and secure access to API keys
for various AI and third-party services used in the NOUS application.
It implements a cost-efficient fallback strategy with quota management
and provides secure key rotation capabilities.

@module: key_config
@author: NOUS Development Team
"""

import os
import logging
import time
import json
import hashlib
import threading
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Key validation cache duration (increased from 5 to 15 minutes)
KEY_VALIDATION_CACHE_DURATION = 900  

# Dictionary to track key validation status, usage, and timestamps
key_metadata = {
    "last_check": 0,
    "status": {},
    "usage": {},
    "quota": {},
    "errors": {},
    "last_success": {}
}

# Thread lock for updating key metadata
_key_lock = threading.RLock()

class APIKeyManager:
    """Manages API keys with secure access patterns, validation, and quota tracking"""
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_key(service_name: str, default: str = "") -> str:
        """
        Get an API key for a specific service with proper validation and load balancing
        
        Args:
            service_name: The name of the service (e.g., 'openai', 'openrouter')
            default: Default value if key not found
            
        Returns:
            The API key or default value
        """
        # Generate environment variable name
        env_var_name = f"{service_name.upper()}_API_KEY"
        
        # Check for multiple keys (non-rotation based)
        multi_keys = []
        main_key = os.environ.get(env_var_name, default)
        if main_key:
            multi_keys.append((env_var_name, main_key))
        
        # Check for numbered keys (KEY_1, KEY_2, etc.)
        for i in range(1, 6):  # Support up to 5 numbered keys
            numbered_env_var = f"{env_var_name}_{i}"
            if numbered_env_var in os.environ and os.environ[numbered_env_var]:
                multi_keys.append((numbered_env_var, os.environ[numbered_env_var]))
                
        # If no keys found, return default
        if not multi_keys:
            return default
            
        # If only one key, return it
        if len(multi_keys) == 1:
            return multi_keys[0][1]
            
        # Multiple keys found - implement load balancing with error and quota awareness
        with _key_lock:
            # Initialize usage data for keys if not exists
            for var_name, key_value in multi_keys:
                key_id = f"{service_name}:{var_name}"
                if key_id not in key_metadata["usage"]:
                    key_metadata["usage"][key_id] = 0
                if key_id not in key_metadata["errors"]:
                    key_metadata["errors"][key_id] = 0
                if key_id not in key_metadata["last_success"]:
                    key_metadata["last_success"][key_id] = time.time()
                    
            # Sort keys by (error count, usage)
            sorted_keys = sorted(multi_keys, key=lambda k: (
                key_metadata["errors"].get(f"{service_name}:{k[0]}", 0),  # Fewest errors first
                key_metadata["usage"].get(f"{service_name}:{k[0]}", 0)    # Least usage first
            ))
            
            # Check if best key has recent errors; if so and we have alternatives, try next best
            best_key_id = f"{service_name}:{sorted_keys[0][0]}"
            now = time.time()
            
            # If best key has errors in last minute and we have alternatives, try next
            if (key_metadata["errors"].get(best_key_id, 0) > 0 and 
                (now - key_metadata["last_success"].get(best_key_id, 0)) < 60 and
                len(sorted_keys) > 1):
                # Use second-best key
                selected_key = sorted_keys[1][1]
                selected_key_id = f"{service_name}:{sorted_keys[1][0]}"
            else:
                # Use best key
                selected_key = sorted_keys[0][1]
                selected_key_id = best_key_id
                
            # Increment usage counter
            key_metadata["usage"][selected_key_id] = key_metadata["usage"].get(selected_key_id, 0) + 1
            
            return selected_key

    @staticmethod
    def record_key_usage(service_name: str, key: str, success: bool = True, error_type: Optional[str] = None) -> None:
        """
        Record success/failure of API key usage for better balancing
        
        Args:
            service_name: Service the key was used for
            key: The API key that was used
            success: Whether the call was successful
            error_type: Type of error if failure (e.g., 'rate_limit', 'quota')
        """
        if not key:
            return
            
        # Find the environment variable this key came from
        env_var_name = None
        key_hash = APIKeyManager.get_key_hash(key)
        
        # Check main key
        main_var = f"{service_name.upper()}_API_KEY"
        if os.environ.get(main_var) and APIKeyManager.get_key_hash(os.environ[main_var]) == key_hash:
            env_var_name = main_var
            
        # Check numbered keys
        if not env_var_name:
            for i in range(1, 6):
                var_name = f"{main_var}_{i}"
                if var_name in os.environ and APIKeyManager.get_key_hash(os.environ[var_name]) == key_hash:
                    env_var_name = var_name
                    break
                    
        if not env_var_name:
            # Couldn't identify the key's variable name
            return
            
        key_id = f"{service_name}:{env_var_name}"
        
        with _key_lock:
            if success:
                # Update last success time
                key_metadata["last_success"][key_id] = time.time()
                # Reset error count on success
                key_metadata["errors"][key_id] = 0
            else:
                # Increment error count
                key_metadata["errors"][key_id] = key_metadata["errors"].get(key_id, 0) + 1

    @staticmethod
    def validate_key_format(service_name: str, api_key: str) -> bool:
        """
        Validate the format of an API key for a specific service
        
        Args:
            service_name: The name of the service
            api_key: The API key to validate
            
        Returns:
            True if the key format is valid, False otherwise
        """
        if not api_key:
            return False
            
        if service_name.lower() == "openai":
            # OpenAI keys start with sk-
            return api_key.startswith("sk-") and not api_key.startswith("sk-or-")
            
        elif service_name.lower() == "openrouter":
            # OpenRouter keys start with sk-or-
            return api_key.startswith("sk-or-")
            
        elif service_name.lower() == "huggingface":
            # Hugging Face keys typically start with hf_
            return api_key.startswith("hf_")
            
        elif service_name.lower() == "google":
            # Google API keys are alphanumeric and 39 characters
            return len(api_key) == 39 and api_key.isalnum()
            
        elif service_name.lower() == "spotify":
            # No specific format for Spotify client ID, check if it exists
            return bool(api_key)
            
        # For other services, just check if key exists
        return bool(api_key)
    
    @staticmethod
    def get_key_hash(api_key: str) -> str:
        """
        Get a secure hash of an API key for logging purposes
        
        Args:
            api_key: The API key to hash
            
        Returns:
            A shortened hash of the API key
        """
        if not api_key:
            return "none"
            
        # Create SHA-256 hash and return first 8 chars
        return hashlib.sha256(api_key.encode()).hexdigest()[:8]


# Set up API key getters (with lazy loading)
def get_openai_key() -> str:
    """Get OpenAI API key with validation"""
    return APIKeyManager.get_key("openai")
    
def get_openrouter_key() -> str:
    """Get OpenRouter API key with validation"""
    return APIKeyManager.get_key("openrouter")
    
def get_huggingface_token() -> str:
    """Get Hugging Face access token with validation"""
    return APIKeyManager.get_key("huggingface")
    
def get_google_key() -> str:
    """Get Google API key with validation"""
    return APIKeyManager.get_key("google")

# Global flags from environment with defaults
USE_HUGGINGFACE = os.environ.get("USE_HUGGINGFACE", "true").lower() == "true"
USE_OPENROUTER = os.environ.get("USE_OPENROUTER", "true").lower() == "true"
USE_OPENAI = os.environ.get("USE_OPENAI", "false").lower() == "true"
DEFAULT_MODEL = os.environ.get("DEFAULT_LLM_MODEL", "gpt-3.5-turbo")
ENHANCED_MODEL = os.environ.get("ENHANCED_LLM_MODEL", "gpt-4")

@lru_cache(maxsize=1)
def validate_keys() -> Dict[str, bool]:
    """
    Validate all API keys and log their status
    
    Returns:
        Dictionary of key validation results
    """
    global key_metadata
    
    # Check if cached result is fresh
    current_time = time.time()
    with _key_lock:
        if current_time - key_metadata["last_check"] < KEY_VALIDATION_CACHE_DURATION:
            return key_metadata["status"].copy()
    
    keys_valid = {}
    
    # Check OpenRouter API key
    openrouter_key = get_openrouter_key()
    if openrouter_key:
        if APIKeyManager.validate_key_format("openrouter", openrouter_key):
            logger.info(f"OpenRouter API key found and has correct format (hash: {APIKeyManager.get_key_hash(openrouter_key)})")
            keys_valid["openrouter"] = True
        else:
            logger.warning("OpenRouter API key has incorrect format - should start with 'sk-or-'")
            keys_valid["openrouter"] = False
    else:
        logger.warning("OpenRouter API key not found")
        keys_valid["openrouter"] = False
    
    # Check OpenAI API key
    openai_key = get_openai_key()
    if openai_key:
        if APIKeyManager.validate_key_format("openai", openai_key):
            logger.info(f"OpenAI API key found and has correct format (hash: {APIKeyManager.get_key_hash(openai_key)})")
            keys_valid["openai"] = True
        else:
            logger.warning("OpenAI API key has incorrect format")
            keys_valid["openai"] = False
    else:
        logger.info("OpenAI API key not found")
        keys_valid["openai"] = False
        
    # Check Hugging Face token
    hf_token = get_huggingface_token()
    if hf_token:
        if APIKeyManager.validate_key_format("huggingface", hf_token):
            logger.info(f"Hugging Face token found and has correct format (hash: {APIKeyManager.get_key_hash(hf_token)})")
            keys_valid["huggingface"] = True
        else:
            logger.warning("Hugging Face token has incorrect format")
            keys_valid["huggingface"] = False
    else:
        logger.info("Hugging Face token not found")
        keys_valid["huggingface"] = False
        
    # Check Google API key
    google_key = get_google_key()
    if google_key:
        if APIKeyManager.validate_key_format("google", google_key):
            logger.info(f"Google API key found and has correct format (hash: {APIKeyManager.get_key_hash(google_key)})")
            keys_valid["google"] = True
        else:
            logger.warning("Google API key has incorrect format")
            keys_valid["google"] = False
    else:
        logger.info("Google API key not found")
        keys_valid["google"] = False
    
    # Update cache
    with _key_lock:
        key_metadata["last_check"] = current_time
        key_metadata["status"] = keys_valid.copy()
    
    return keys_valid

def get_preferred_service():
    """
    Get the preferred AI service based on available keys and configuration.
    Prioritizes cost-effective services (Hugging Face > OpenRouter > OpenAI).
    
    Returns:
        str: The name of the preferred service
    """
    keys_valid = validate_keys()
    
    # First priority: Hugging Face (free service)
    if USE_HUGGINGFACE and keys_valid.get("huggingface", False):
        return "huggingface"
    # Second priority: OpenRouter (lower cost than OpenAI)
    elif USE_OPENROUTER and keys_valid.get("openrouter", False):
        return "openrouter"
    # Third priority: OpenAI (highest cost)
    elif USE_OPENAI and keys_valid.get("openai", False):
        return "openai"
    # Fallbacks if preferred services aren't available
    elif keys_valid.get("huggingface", False):
        return "huggingface" 
    elif keys_valid.get("openrouter", False):
        return "openrouter"
    elif keys_valid.get("openai", False):
        return "openai"
    # Last resort
    else:
        return "local"  # Return "local" instead of None to enable local fallbacks

def get_model_for_task(task_complexity="standard", service=None):
    """
    Get the appropriate model for a given task complexity
    
    Args:
        task_complexity (str): Complexity of the task ('standard', 'high', 'critical')
        service (str, optional): Override the service selection
        
    Returns:
        tuple: (service_name, model_name)
    """
    if not service:
        service = get_preferred_service()
    
    if service == "openai":
        if task_complexity == "high" or task_complexity == "critical":
            return "openai", ENHANCED_MODEL
        else:
            return "openai", DEFAULT_MODEL
    
    elif service == "openrouter":
        if task_complexity == "high" or task_complexity == "critical":
            return "openrouter", "openai/gpt-4-turbo-preview"
        else:
            return "openrouter", "anthropic/claude-instant-v1"
    
    elif service == "huggingface":
        if task_complexity == "high":
            return "huggingface", "mistralai/Mixtral-8x7B-Instruct-v0.1"
        else:
            return "huggingface", "mistralai/Mistral-7B-Instruct-v0.2"
    
    else:  # local
        return "local", "default"