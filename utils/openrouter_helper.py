"""
OpenRouter API integration helper for NOUS Personal Assistant.
Provides clean integration with OpenRouter's API for AI functionality.
"""

import os
import logging
import json
import requests
from typing import List, Dict, Any, Optional

# Get the OpenRouter API key from environment
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"

def get_headers():
    """Get fresh headers with the current API key"""
    return {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nous.replit.app/",
        "X-Title": "NOUS Personal Assistant"
    }

def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "openai/gpt-4-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Optional[str]:
    """
    Send a chat completion request to OpenRouter API.
    
    Args:
        messages: List of message objects with 'role' and 'content'
        model: The model to use (needs provider prefix for OpenRouter)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        The generated text response or None if there was an error
    """
    # Get the current API key from environment
    current_api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not current_api_key:
        logging.error("No OpenRouter API key found")
        return None
        
    try:
        logging.info(f"Using OpenRouter API with model {model}")
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Send request to OpenRouter API with fresh headers
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                    content = result["choices"][0]["message"]["content"]
                    return content
                    
        logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logging.error(f"Error using OpenRouter API: {str(e)}")
        return None


def get_embeddings(text: str) -> Optional[List[float]]:
    """
    Generate embeddings using OpenRouter API.
    
    Args:
        text: The text to embed
        
    Returns:
        List of embedding values or None if there was an error
    """
    if not API_KEY:
        logging.error("No OpenRouter API key found")
        return None
        
    try:
        logging.info("Generating embeddings with OpenRouter API")
        
        # Prepare the request payload
        payload = {
            "model": "openai/text-embedding-ada-002",
            "input": text
        }
        
        # Send request to OpenRouter API
        response = requests.post(
            f"{BASE_URL}/embeddings",
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
                embedding = result["data"][0]["embedding"]
                return embedding
                
        logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logging.error(f"Error generating embeddings with OpenRouter: {str(e)}")
        return None


def list_available_models() -> Optional[List[Dict[str, Any]]]:
    """
    Get a list of models available through OpenRouter.
    
    Returns:
        List of model information or None if there was an error
    """
    if not API_KEY:
        logging.error("No OpenRouter API key found")
        return None
        
    try:
        response = requests.get(
            f"{BASE_URL}/models",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get("data", [])
            
        logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logging.error(f"Error retrieving models from OpenRouter: {str(e)}")
        return None