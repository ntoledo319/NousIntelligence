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
    logger.info(=== Final OAuth System Fix ===)
    
    # Test current OAuth service
    try:
        from utils.google_oauth import oauth_service
        logger.info(✅ OAuth service imported)
        
        # Test credential extraction
        raw_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        logger.info(Raw Client ID length: {len(raw_client_id) if raw_client_id else 0})
        logger.info(Raw Client Secret length: {len(raw_client_secret) if raw_client_secret else 0})
        
        # Extract clean credentials
        clean_client_id = oauth_service._extract_client_id(raw_client_id)
        clean_client_secret = oauth_service._extract_client_secret(raw_client_secret)
        
        logger.info(Clean Client ID: {clean_client_id})
        logger.info(Clean Client Secret: {clean_client_secret[:20]}...)
        
        # Test OAuth configuration
        is_configured = oauth_service.is_configured()
        logger.info(OAuth Configured: {is_configured})
        
        if is_configured:
            logger.info(✅ OAuth system is working correctly!)
        else:
            logger.info(❌ OAuth system needs initialization)
            
        # Test with a minimal Flask app
        from flask import Flask
        test_app = Flask(__name__)
        test_app.secret_key = os.environ.get('SESSION_SECRET', 'test-key')
        
        # Test initialization
        with test_app.app_context():
            result = oauth_service.init_app(test_app)
            logger.info(OAuth init result: {result})
            
            if result:
                logger.info(✅ OAuth initialization successful!)
                configured = oauth_service.is_configured()
                logger.info(✅ OAuth configured after init: {configured})
            else:
                logger.info(❌ OAuth initialization failed)
                
    except Exception as e:
        logger.error(❌ Error: {e})
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()