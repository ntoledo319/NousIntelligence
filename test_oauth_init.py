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

print("🔍 Testing OAuth Initialization")
print("=" * 40)

print("\n1. Environment Variables:")
print(f"   GOOGLE_CLIENT_ID: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_ID') else '❌ Missing'}")
print(f"   GOOGLE_CLIENT_SECRET: {'✅ Set' if os.environ.get('GOOGLE_CLIENT_SECRET') else '❌ Missing'}")

print("\n2. Flask App Context:")
with app.app_context():
    print("   App Context: ✅ Active")
    
    print("\n3. OAuth Service Before Init:")
    print(f"   Google Client: {'✅ Exists' if oauth_service.google else '❌ None'}")
    
    print("\n4. Initializing OAuth:")
    try:
        success = oauth_service.init_app(app)
        print(f"   init_app() returned: {'✅ True' if success else '❌ False'}")
    except Exception as e:
        print(f"   init_app() Exception: ❌ {e}")
        
    print("\n5. OAuth Service After Init:")
    print(f"   Google Client: {'✅ Exists' if oauth_service.google else '❌ None'}")
    print(f"   is_configured(): {'✅ True' if oauth_service.is_configured() else '❌ False'}")
    
    if oauth_service.google:
        print(f"   Google Client Type: {type(oauth_service.google)}")
        print(f"   Google Client Name: {getattr(oauth_service.google, 'name', 'Unknown')}")

print("\n" + "=" * 40)
print("OAuth Initialization Test Complete")