#!/usr/bin/env python3
"""
Debug OAuth Configuration - Detailed Analysis
"""

import os
from app import create_app

def debug_oauth_detailed():
    """Debug OAuth configuration in detail"""
    print("=== OAuth Debug Analysis ===")
    
    # Check environment variables
    print("\n1. Environment Variables:")
    print(f"   GOOGLE_CLIENT_ID: {'SET' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT SET'}")
    print(f"   GOOGLE_CLIENT_SECRET: {'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT SET'}")
    print(f"   SESSION_SECRET: {'SET' if os.environ.get('SESSION_SECRET') else 'NOT SET'}")
    
    # Test app creation
    print("\n2. App Creation:")
    try:
        app = create_app()
        print("   ✅ App created successfully")
        print(f"   OAuth Enabled: {app.config.get('OAUTH_ENABLED', 'NOT SET')}")
    except Exception as e:
        print(f"   ❌ App creation failed: {e}")
        return
    
    # Test OAuth service in app context
    print("\n3. OAuth Service in App Context:")
    with app.app_context():
        try:
            from utils.google_oauth import oauth_service
            print(f"   OAuth Service: {'INITIALIZED' if oauth_service else 'NOT INITIALIZED'}")
            
            if oauth_service:
                print(f"   Is Configured: {oauth_service.is_configured()}")
                print(f"   Google Client: {'AVAILABLE' if oauth_service.google else 'NOT AVAILABLE'}")
                
                # Test OAuth client registration
                if oauth_service.google:
                    print(f"   Client Name: {oauth_service.google.name}")
                    print(f"   Client ID: {oauth_service.google.client_id[:20]}..." if oauth_service.google.client_id else "NOT SET")
                
        except Exception as e:
            print(f"   ❌ OAuth service test failed: {e}")
    
    # Test OAuth route
    print("\n4. OAuth Route Test:")
    with app.test_client() as client:
        try:
            response = client.get('/auth/google', follow_redirects=False)
            print(f"   Status Code: {response.status_code}")
            print(f"   Location Header: {response.location if hasattr(response, 'location') else 'NONE'}")
            
            if response.status_code == 302:
                if 'google' in str(response.location):
                    print("   ✅ Redirecting to Google OAuth")
                else:
                    print(f"   ⚠️  Redirecting elsewhere: {response.location}")
            else:
                print("   ❌ Not redirecting")
                
        except Exception as e:
            print(f"   ❌ Route test failed: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_oauth_detailed()