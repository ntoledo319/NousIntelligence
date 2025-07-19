#!/usr/bin/env python3
"""
Google OAuth Configuration Test
Tests and diagnoses Google OAuth issues
"""

import os
import logging
from flask import Flask, url_for
from utils.google_oauth import oauth_service
from config.app_config import AppConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_oauth_configuration():
    """Test Google OAuth configuration"""
    logger.info("🔍 Google OAuth Configuration Test")
    logger.info("=" * 50)
    
    # Test environment variables
    logger.info("\n1. Environment Variables:")
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    session_secret = os.environ.get('SESSION_SECRET')
    
    logger.info("   GOOGLE_CLIENT_ID: {}".format('Set' if client_id else 'Missing'))
    if client_id:
        logger.info("      Value: {}...{}".format(client_id[:20], client_id[-10:]))
    
    logger.info("   GOOGLE_CLIENT_SECRET: {}".format('Set' if client_secret else 'Missing'))
    if client_secret:
        logger.info("      Value: {}...{}".format(client_secret[:10], client_secret[-5:]))
    
    logger.info("   SESSION_SECRET: {}".format('Set' if session_secret else 'Missing'))
    
    # Test OAuth service configuration
    logger.info("\n2. OAuth Service Configuration:")
    try:
        configured = oauth_service.is_configured()
        logger.info("   OAuth Service: {}".format('Configured' if configured else 'Not Configured'))
    except Exception as e:
        logger.error("   OAuth Service: Error - {}".format(str(e)))
    
    # Test Flask app and URL generation
    logger.info("\n3. Flask URL Generation Test:")
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    with app.app_context():
        try:
            # Test local URL generation
            local_callback = url_for('auth.google_callback', _external=True)
            logger.info("   Local Callback URL: {}".format(local_callback))
            
            # Test what redirect URI would be generated
            if oauth_service.google:
                fixed_uri = oauth_service._fix_redirect_uri(local_callback)
                logger.info("   Fixed Callback URL: {}".format(fixed_uri))
            
        except Exception as e:
            logger.error("   URL Generation: Error - {}".format(str(e)))
    
    # Environment info for Replit
    logger.info("\n4. Replit Environment Info:")
    repl_url = os.environ.get('REPL_URL')
    repl_slug = os.environ.get('REPL_SLUG')
    replit_domain = os.environ.get('REPLIT_DOMAIN')
    
    logger.info("   REPL_URL: {}".format(repl_url or 'Not set'))
    logger.info("   REPL_SLUG: {}".format(repl_slug or 'Not set'))
    logger.info("   REPLIT_DOMAIN: {}".format(replit_domain or 'Not set'))
    
    # Recommended redirect URIs
    logger.info("\n5. Recommended Google Cloud Console Configuration:")
    logger.info("   Add these redirect URIs to your Google OAuth Client:")
    
    if repl_url:
        logger.info("   • {}".format(repl_url + "/auth/google/callback"))
    
    # Common Replit patterns
    if repl_slug:
        logger.info("   • https://{}.replit.dev/auth/google/callback".format(repl_slug))
        logger.info("   • https://{}.replit.app/auth/google/callback".format(repl_slug))
    
    logger.info("   • http://localhost:8080/auth/google/callback (for testing)")
    logger.info("   • https://workspace.replit.dev/auth/google/callback")
    
    logger.info("\n📝 Summary:")
    if client_id and client_secret and session_secret:
        logger.info("   ✅ All environment variables are configured")
    else:
        logger.info("   ❌ Missing required environment variables")
    
    if configured:
        logger.info("   ✅ OAuth service is properly initialized")
    else:
        logger.info("   ❌ OAuth service failed to initialize")
    
    logger.info("\n🔧 Next Steps:")
    logger.info("   1. Ensure all environment variables are set in Replit Secrets")
    logger.info("   2. Add the recommended redirect URIs to Google Cloud Console")
    logger.info("   3. Test the Google login flow")

if __name__ == "__main__":
    test_oauth_configuration()