"""
Helper script to load Google OAuth credentials from client_secret.json into environment variables.

This module implements the credential loading approach described in Google's OAuth 2.0 documentation:
https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred

For proper OAuth setup, credentials should be obtained from the Google Cloud Console:
https://console.cloud.google.com/apis/credentials
"""
import os
import json
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_google_credentials() -> bool:
    """
    Load Google OAuth credentials from client_secret.json file into environment variables.
    
    This function loads the OAuth client ID and client secret from the standard
    client_secret.json file format provided by the Google Cloud Console and
    sets them as environment variables for use with OAuth libraries.
    
    Returns:
        bool: True if credentials were successfully loaded, False otherwise
    
    References:
        - https://developers.google.com/identity/protocols/oauth2/web-server#obtainingcred
    """
    try:
        # Path to client_secret.json file
        client_secrets_file = "client_secret.json"
        
        # Check if the file exists
        if not os.path.exists(client_secrets_file):
            logger.error(f"Client secrets file not found: {client_secrets_file}")
            logger.error("Download credentials from https://console.cloud.google.com/apis/credentials")
            return False
            
        # Load the JSON data
        with open(client_secrets_file, "r") as f:
            try:
                client_info = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {client_secrets_file}")
                return False
            
        # Extract relevant credentials
        if "web" in client_info:
            web_info = client_info["web"]
            
            # Validate required fields
            if not web_info.get("client_id") or not web_info.get("client_secret"):
                logger.error("Missing required credentials in client_secret.json")
                return False
                
            # Set environment variables if not already set
            if not os.environ.get("GOOGLE_CLIENT_ID"):
                os.environ["GOOGLE_CLIENT_ID"] = web_info.get("client_id", "")
            
            if not os.environ.get("GOOGLE_CLIENT_SECRET"):
                os.environ["GOOGLE_CLIENT_SECRET"] = web_info.get("client_secret", "")
                
            if not os.environ.get("GOOGLE_REDIRECT_URI") and "redirect_uris" in web_info and web_info["redirect_uris"]:
                os.environ["GOOGLE_REDIRECT_URI"] = web_info["redirect_uris"][0]
                
            # Also set alternate variable names used in different parts of the code
            if not os.environ.get("GOOGLE_OAUTH_CLIENT_ID"):
                os.environ["GOOGLE_OAUTH_CLIENT_ID"] = web_info.get("client_id", "")
                
            if not os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"):
                os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = web_info.get("client_secret", "")
            
            logger.info(f"Loaded Google OAuth credentials from {client_secrets_file}")
            
            # Log the credentials (partially masked for security)
            client_id = web_info.get("client_id", "")
            masked_id = client_id[:8] + "..." + client_id[-4:] if len(client_id) > 12 else ""
            logger.info(f"Client ID: {masked_id}")
            
            # Validate redirect URIs
            if not web_info.get("redirect_uris"):
                logger.warning("No redirect URIs found in client_secret.json")
            else:
                logger.info(f"Configured redirect URIs: {', '.join(web_info['redirect_uris'])}")
                
            # Check auth provider
            if "auth_provider_x509_cert_url" in web_info:
                logger.info("OAuth authority validation URL present")
            else:
                logger.warning("Missing auth_provider_x509_cert_url in credentials")
                
            return True
        else:
            logger.error("Invalid client_secret.json format: 'web' key not found")
            logger.error("Please ensure you're using a Web application credential type from Google Cloud Console")
            return False
    
    except Exception as e:
        logger.error(f"Error loading Google credentials: {str(e)}")
        return False

def get_credentials() -> Optional[Dict[str, Any]]:
    """
    Return OAuth credentials from environment variables as a dictionary.
    
    This is a convenience function for OAuth libraries that require
    credentials as a dictionary rather than environment variables.
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary with client_id and client_secret,
                                 or None if not available
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID") or os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET") or os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return None
        
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }

# Run this function when the module is imported
load_google_credentials() 