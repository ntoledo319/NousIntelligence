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
    print("🔍 Google OAuth Configuration Test")
    print("=" * 50)
    
    # Test environment variables
    print("\n1. Environment Variables:")
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    session_secret = os.environ.get('SESSION_SECRET')
    
    print(f"   GOOGLE_CLIENT_ID: {'✅ Set' if client_id else '❌ Missing'}")
    if client_id:
        print(f"      Value: {client_id[:20]}...{client_id[-10:]}")
    
    print(f"   GOOGLE_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Missing'}")
    if client_secret:
        print(f"      Value: {client_secret[:10]}...{client_secret[-5:]}")
    
    print(f"   SESSION_SECRET: {'✅ Set' if session_secret else '❌ Missing'}")
    
    # Test OAuth service configuration
    print("\n2. OAuth Service Configuration:")
    try:
        configured = oauth_service.is_configured()
        print(f"   OAuth Service: {'✅ Configured' if configured else '❌ Not Configured'}")
    except Exception as e:
        print(f"   OAuth Service: ❌ Error - {e}")
    
    # Test Flask app and URL generation
    print("\n3. Flask URL Generation Test:")
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    with app.app_context():
        try:
            # Test local URL generation
            local_callback = url_for('auth.google_callback', _external=True)
            print(f"   Local Callback URL: {local_callback}")
            
            # Test what redirect URI would be generated
            if oauth_service.google:
                fixed_uri = oauth_service._fix_redirect_uri(local_callback)
                print(f"   Fixed Callback URL: {fixed_uri}")
            
        except Exception as e:
            print(f"   URL Generation: ❌ Error - {e}")
    
    # Environment info for Replit
    print("\n4. Replit Environment Info:")
    repl_url = os.environ.get('REPL_URL')
    repl_slug = os.environ.get('REPL_SLUG')
    replit_domain = os.environ.get('REPLIT_DOMAIN')
    
    print(f"   REPL_URL: {repl_url or 'Not set'}")
    print(f"   REPL_SLUG: {repl_slug or 'Not set'}")
    print(f"   REPLIT_DOMAIN: {replit_domain or 'Not set'}")
    
    # Recommended redirect URIs
    print("\n5. Recommended Google Cloud Console Configuration:")
    print("   Add these redirect URIs to your Google OAuth Client:")
    
    if repl_url:
        print(f"   • {repl_url}/auth/google/callback")
    
    # Common Replit patterns
    if repl_slug:
        print(f"   • https://{repl_slug}.replit.dev/auth/google/callback")
        print(f"   • https://{repl_slug}.replit.app/auth/google/callback")
    
    print("   • http://localhost:8080/auth/google/callback (for testing)")
    print("   • https://workspace.replit.dev/auth/google/callback")
    
    print("\n📝 Summary:")
    if client_id and client_secret and session_secret:
        print("   ✅ All environment variables are configured")
    else:
        print("   ❌ Missing required environment variables")
    
    if configured:
        print("   ✅ OAuth service is properly initialized")
    else:
        print("   ❌ OAuth service failed to initialize")
    
    print("\n🔧 Next Steps:")
    print("   1. Ensure all environment variables are set in Replit Secrets")
    print("   2. Add the recommended redirect URIs to Google Cloud Console")
    print("   3. Test the Google login flow")

if __name__ == "__main__":
    test_oauth_configuration()