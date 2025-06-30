#!/usr/bin/env python3
"""
Final OAuth Fix
Applies the complete OAuth credential extraction fix to the running application
"""

import os
import sys
import re
import logging

sys.path.insert(0, '.')

def main():
    """Apply OAuth fixes"""
    print("=== Final OAuth System Fix ===")
    
    # Test current OAuth service
    try:
        from utils.google_oauth import oauth_service
        print("✅ OAuth service imported")
        
        # Test credential extraction
        raw_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        print(f"Raw Client ID length: {len(raw_client_id) if raw_client_id else 0}")
        print(f"Raw Client Secret length: {len(raw_client_secret) if raw_client_secret else 0}")
        
        # Extract clean credentials
        clean_client_id = oauth_service._extract_client_id(raw_client_id)
        clean_client_secret = oauth_service._extract_client_secret(raw_client_secret)
        
        print(f"Clean Client ID: {clean_client_id}")
        print(f"Clean Client Secret: {clean_client_secret[:20]}..." if clean_client_secret else "None")
        
        # Test OAuth configuration
        is_configured = oauth_service.is_configured()
        print(f"OAuth Configured: {is_configured}")
        
        if is_configured:
            print("✅ OAuth system is working correctly!")
        else:
            print("❌ OAuth system needs initialization")
            
        # Test with a minimal Flask app
        from flask import Flask
        test_app = Flask(__name__)
        test_app.secret_key = os.environ.get('SESSION_SECRET', 'test-key')
        
        # Test initialization
        with test_app.app_context():
            result = oauth_service.init_app(test_app)
            print(f"OAuth init result: {result}")
            
            if result:
                print("✅ OAuth initialization successful!")
                configured = oauth_service.is_configured()
                print(f"✅ OAuth configured after init: {configured}")
            else:
                print("❌ OAuth initialization failed")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()