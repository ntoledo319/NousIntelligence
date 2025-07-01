import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Debug OAuth Configuration
Quick test to understand OAuth status
"""

import os
import sys
sys.path.append('.')

from utils.google_oauth import oauth_service

logger.info(🔍 OAuth Configuration Debug)
logger.info(=)

# Test environment variables
logger.info(\n1. Environment Variables:)
logger.info(   GOOGLE_CLIENT_ID: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_ID') else '❌ Missing'})
logger.info(   GOOGLE_CLIENT_SECRET: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_SECRET') else '❌ Missing'})

# Test OAuth service
logger.info(\n2. OAuth Service:)
logger.info(   OAuth Service Exists: {'✅ Yes' if oauth_service else '❌ No'})
logger.info(   OAuth Service Type: {type(oauth_service)})

# Test OAuth configuration
logger.info(\n3. OAuth Configuration:)
try:
    is_configured = oauth_service.is_configured()
    logger.info(   is_configured(): {'✅ True' if is_configured else '❌ False'})
except Exception as e:
    logger.error(   is_configured() Error: ❌ {e})

# Test Google client
logger.info(\n4. Google Client:)
try:
    google_client = oauth_service.google
    logger.info(   Google Client: {'✅ Exists' if google_client else '❌ None'})
    logger.info(   Google Client Type: {type(google_client) if google_client else 'None'})
except Exception as e:
    logger.error(   Google Client Error: ❌ {e})

# Test OAuth object
logger.info(\n5. OAuth Object:)
try:
    oauth_obj = oauth_service.oauth
    logger.info(   OAuth Object: {'✅ Exists' if oauth_obj else '❌ None'})
    logger.info(   OAuth Object Type: {type(oauth_obj) if oauth_obj else 'None'})
except Exception as e:
    logger.error(   OAuth Object Error: ❌ {e})

logger.info(\n)
logger.info(Debug Complete)