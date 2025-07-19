import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Test OAuth Initialization in Flask Context
"""

import os
import sys
sys.path.append('.')

from flask import Flask
from utils.google_oauth import oauth_service

# Create minimal Flask app for testing
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "test-secret")

logger.info("Testing OAuth Initialization")
logger.info("=" * 40)

logger.info("\n1. Environment Variables:")
logger.info("   GOOGLE_CLIENT_ID: {}".format('Set' if os.environ.get('GOOGLE_CLIENT_ID') else 'Missing'))
logger.info("   GOOGLE_CLIENT_SECRET: {}".format('Set' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'Missing'))

logger.info("\n2. Flask App Context:")
with app.app_context():
    logger.info("   App Context: Active")
    
    logger.info("\n3. OAuth Service Before Init:")
    logger.info("   Google Client: {}".format('Exists' if oauth_service.google else 'None'))
    logger.info("   Authorized: {}".format('Yes' if oauth_service.google and oauth_service.google.authorized else 'No'))
    
    # Initialize OAuth in app context
    oauth_service.init_app(app)
    
    logger.info("\n4. OAuth Service After Init:")
    logger.info("   Google Client: {}".format('Exists' if oauth_service.google else 'None'))
    logger.info("   Authorized: {}".format('Yes' if oauth_service.google and oauth_service.google.authorized else 'No'))
    
    if oauth_service.google:
        logger.info("   Redirect URI: {}".format(oauth_service.google.authorize_redirect_uri))
        logger.info("   Google Client Name: {}".format(getattr(oauth_service.google, 'name', 'Unknown')))

logger.info("\n")
logger.info("OAuth Initialization Test Complete")