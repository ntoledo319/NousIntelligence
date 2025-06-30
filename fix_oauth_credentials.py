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
    
    print("=== OAuth Credentials Analysis ===")
    print(f"Raw GOOGLE_CLIENT_ID length: {len(raw_client_id)}")
    print(f"Raw GOOGLE_CLIENT_SECRET length: {len(raw_client_secret)}")
    
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
    
    print("\n=== Extracted Credentials ===")
    print(f"Clean Client ID: {client_id}")
    print(f"Clean Client Secret: {client_secret}")
    
    # Validate credentials
    if client_id and client_secret:
        print("\n✅ OAuth credentials successfully extracted!")
        print(f"Client ID format: Valid (ends with .apps.googleusercontent.com)")
        print(f"Client Secret format: Valid (starts with GOCSPX-)")
        
        # Show what needs to be set in Replit Secrets
        print("\n=== Required Replit Secrets ===")
        print(f"GOOGLE_CLIENT_ID = {client_id}")
        print(f"GOOGLE_CLIENT_SECRET = {client_secret}")
        
        return client_id, client_secret
    else:
        print("\n❌ Failed to extract valid OAuth credentials")
        return None, None

if __name__ == "__main__":
    extract_clean_credentials()