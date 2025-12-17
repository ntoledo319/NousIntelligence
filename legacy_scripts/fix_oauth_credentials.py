import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Fix OAuth Credentials
Extracts clean OAuth credentials from malformed environment variables
"""

import os
import re
import json

def extract_clean_credentials():
    """Extract clean OAuth credentials from malformed environment variables"""
    
    # Get raw environment variables
    raw_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    logger.info(=== OAuth Credentials Analysis ===)
    logger.info(Raw GOOGLE_CLIENT_ID length: {len(raw_client_id)})
    logger.info(Raw GOOGLE_CLIENT_SECRET length: {len(raw_client_secret)})
    
    # Extract clean client ID
    client_id = None
    if 'apps.googleusercontent.com' in raw_client_id:
        # Look for the client ID pattern
        match = re.search(r'(\d{10,15}-[a-zA-Z0-9]+\.apps\.googleusercontent\.com)', raw_client_id)
        if match:
            client_id = match.group(1)
    
    # Extract clean client secret
    client_secret = None
    if 'GOCSPX-' in raw_client_secret:
        # Look for the client secret pattern
        match = re.search(r'(GOCSPX-[a-zA-Z0-9_-]+)', raw_client_secret)
        if match:
            client_secret = match.group(1)
    
    logger.info(\n=== Extracted Credentials ===)
    logger.info(Clean Client ID: {client_id})
    logger.info(Clean Client Secret: {client_secret})
    
    # Validate credentials
    if client_id and client_secret:
        logger.info(\n✅ OAuth credentials successfully extracted!)
        logger.info(Client ID format: Valid (ends with .apps.googleusercontent.com))
        logger.info(Client Secret format: Valid (starts with GOCSPX-))
        
        # Show what needs to be set in Replit Secrets
        logger.info(\n=== Required Replit Secrets ===)
        logger.info(GOOGLE_CLIENT_ID = {client_id})
        logger.info(GOOGLE_CLIENT_SECRET = {client_secret})
        
        return client_id, client_secret
    else:
        logger.info(\n❌ Failed to extract valid OAuth credentials)
        return None, None

if __name__ == "__main__":
    extract_clean_credentials()