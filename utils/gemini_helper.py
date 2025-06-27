"""
Google Gemini API Helper

This module provides a direct interface to Google's Gemini API
for generative AI tasks, using the official Google AI SDK.
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configure the Gemini API client
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
        logger.warning("GEMINI_API_KEY not found. Direct Gemini API calls will be disabled.")
except Exception as e:
    GEMINI_AVAILABLE = False
    logger.error(f"Error configuring Gemini API: {e}")

def call_gemini_api(prompt: str, model_name: str = "gemini-pro") -> Dict[str, Any]:
    """
    Calls the Google Gemini API with a given prompt.

    Args:
        prompt: The text prompt to send to the Gemini API.
        model_name: The name of the Gemini model to use.

    Returns:
        A dictionary containing the response from the API or an error.
    """
    if not GEMINI_AVAILABLE:
        return {"success": False, "error": "Gemini API is not configured."}

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "response": response.text,
            "model": model_name
        }
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return {"success": False, "error": str(e)} 