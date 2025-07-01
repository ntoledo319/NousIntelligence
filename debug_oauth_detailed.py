import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Debug OAuth Configuration - Detailed Analysis
"""

import os
from app import create_app

def debug_oauth_detailed():
    """Debug OAuth configuration in detail"""
    logger.info(=== OAuth Debug Analysis ===)
    
    # Check environment variables
    logger.info(\n1. Environment Variables:)
    logger.info(   GOOGLE_CLIENT_ID: {'SET' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT SET'})
    logger.info(   GOOGLE_CLIENT_SECRET: {'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT SET'})
    logger.info(   SESSION_SECRET: {'SET' if os.environ.get('SESSION_SECRET') else 'NOT SET'})
    
    # Test app creation
    logger.info(\n2. App Creation:)
    try:
        app = create_app()
        logger.info(   ✅ App created successfully)
        logger.info(   OAuth Enabled: {app.config.get('OAUTH_ENABLED', 'NOT SET')})
    except Exception as e:
        logger.info(   ❌ App creation failed: {e})
        return
    
    # Test OAuth service in app context
    logger.info(\n3. OAuth Service in App Context:)
    with app.app_context():
        try:
            from utils.google_oauth import oauth_service
            logger.info(   OAuth Service: {'INITIALIZED' if oauth_service else 'NOT INITIALIZED'})
            
            if oauth_service:
                logger.info(   Is Configured: {oauth_service.is_configured()})
                logger.info(   Google Client: {'AVAILABLE' if oauth_service.google else 'NOT AVAILABLE'})
                
                # Test OAuth client registration
                if oauth_service.google:
                    logger.info(   Client Name: {oauth_service.google.name})
                    logger.info(   Client ID: {oauth_service.google.client_id[:20]}...)
                
        except Exception as e:
            logger.info(   ❌ OAuth service test failed: {e})
    
    # Test OAuth route
    logger.info(\n4. OAuth Route Test:)
    with app.test_client() as client:
        try:
            response = client.get('/auth/google', follow_redirects=False)
            logger.info(   Status Code: {response.status_code})
            logger.info(   Location Header: {response.location if hasattr(response, 'location') else 'NONE'})
            
            if response.status_code == 302:
                if 'google' in str(response.location):
                    logger.info(   ✅ Redirecting to Google OAuth)
                else:
                    logger.info(   ⚠️  Redirecting elsewhere: {response.location})
            else:
                logger.info(   ❌ Not redirecting)
                
        except Exception as e:
            logger.info(   ❌ Route test failed: {e})
    
    logger.info(\n=== Debug Complete ===)

if __name__ == "__main__":
    debug_oauth_detailed()