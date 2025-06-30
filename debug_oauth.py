#!/usr/bin/env python3
"""
Debug OAuth Configuration
Quick test to understand OAuth status
"""

import os
import sys
sys.path.append('.')

from utils.google_oauth import oauth_service

print("🔍 OAuth Configuration Debug")
print("=" * 40)

# Test environment variables
print("\n1. Environment Variables:")
print(f"   GOOGLE_CLIENT_ID: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_ID') else '❌ Missing'}")
print(f"   GOOGLE_CLIENT_SECRET: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_SECRET') else '❌ Missing'}")

# Test OAuth service
print("\n2. OAuth Service:")
print(f"   OAuth Service Exists: {'✅ Yes' if oauth_service else '❌ No'}")
print(f"   OAuth Service Type: {type(oauth_service)}")

# Test OAuth configuration
print("\n3. OAuth Configuration:")
try:
    is_configured = oauth_service.is_configured()
    print(f"   is_configured(): {'✅ True' if is_configured else '❌ False'}")
except Exception as e:
    print(f"   is_configured() Error: ❌ {e}")

# Test Google client
print("\n4. Google Client:")
try:
    google_client = oauth_service.google
    print(f"   Google Client: {'✅ Exists' if google_client else '❌ None'}")
    print(f"   Google Client Type: {type(google_client) if google_client else 'None'}")
except Exception as e:
    print(f"   Google Client Error: ❌ {e}")

# Test OAuth object
print("\n5. OAuth Object:")
try:
    oauth_obj = oauth_service.oauth
    print(f"   OAuth Object: {'✅ Exists' if oauth_obj else '❌ None'}")
    print(f"   OAuth Object Type: {type(oauth_obj) if oauth_obj else 'None'}")
except Exception as e:
    print(f"   OAuth Object Error: ❌ {e}")

print("\n" + "=" * 40)
print("Debug Complete")