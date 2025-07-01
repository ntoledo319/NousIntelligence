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

logger.info(🔍 Testing OAuth Initialization)
logger.info(=)

logger.info(\n1. Environment Variables:)
logger.info(   GOOGLE_CLIENT_ID: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_ID') else '❌ Missing'})
logger.info(   GOOGLE_CLIENT_SECRET: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_SECRET') else '❌ Missing'})

logger.info(\n2. Flask App Context:)
with app.app_context():
    logger.info(   App Context: ✅ Active)
    
    logger.info(\n3. OAuth Service Before Init:)
    logger.info(   Google Client: {'✅ Exists' if oauth_service.google else '❌ None'})
    
    logger.info(\n4. Initializing OAuth:)
    try:
        success = oauth_service.init_app(app)
        logger.info(   init_app() returned: {'✅ True' if success else '❌ False'})
    except Exception as e:
        logger.info(   init_app() Exception: ❌ {e})
        
    logger.info(\n5. OAuth Service After Init:)
    logger.info(   Google Client: {'✅ Exists' if oauth_service.google else '❌ None'})
    logger.info(   is_configured(): {'✅ True' if oauth_service.is_configured() else '❌ False'})
    
    if oauth_service.google:
        logger.info(   Google Client Type: {type(oauth_service.google)})
        logger.info(   Google Client Name: {getattr(oauth_service.google, 'name', 'Unknown')})

logger.info(\n)
logger.info(OAuth Initialization Test Complete)