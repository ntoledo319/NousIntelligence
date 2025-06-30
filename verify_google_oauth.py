#!/usr/bin/env python3
"""
Google OAuth Verification Test
Comprehensive verification of Google OAuth functionality
"""

import os
import sys
import requests
import logging
from flask import Flask
from utils.google_oauth import oauth_service
from config.app_config import AppConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_oauth_endpoints():
    """Verify OAuth endpoints are working correctly"""
    base_url = "http://localhost:8080"
    
    print("🔍 Google OAuth Verification Test")
    print("=" * 50)
    
    # Test 1: Application Health Check
    print("\n1. Application Health Check:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Landing Page: {'✅ OK' if response.status_code == 200 else '❌ Failed'} ({response.status_code})")
    except Exception as e:
        print(f"   Landing Page: ❌ Error - {e}")
        return False
    
    # Test 2: Google Sign-in Button
    print("\n2. Google Sign-in Button Test:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if "Sign in with Google" in response.text:
            print("   ✅ Google sign-in button found on landing page")
        else:
            print("   ❌ Google sign-in button not found")
    except Exception as e:
        print(f"   ❌ Error checking landing page: {e}")
    
    # Test 3: OAuth Endpoint Response
    print("\n3. OAuth Endpoint Response:")
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False, timeout=5)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   Redirect Location: {location}")
            
            if 'accounts.google.com' in location:
                print("   ✅ Correctly redirecting to Google OAuth")
            elif 'auth/login' in location:
                print("   ⚠️  Redirecting to login page - possible rate limiting or config issue")
            else:
                print(f"   ❌ Unexpected redirect: {location}")
        else:
            print("   ❌ Expected 302 redirect, got different status")
            
    except Exception as e:
        print(f"   ❌ Error testing OAuth endpoint: {e}")
    
    # Test 4: OAuth Service Configuration
    print("\n4. OAuth Service Configuration:")
    print(f"   OAuth Service Configured: {'✅ Yes' if oauth_service.is_configured() else '❌ No'}")
    
    if oauth_service.google:
        print("   ✅ Google OAuth client initialized")
    else:
        print("   ❌ Google OAuth client not initialized")
    
    # Test 5: Environment Variables
    print("\n5. Environment Variables Check:")
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
    all_set = True
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: ✅ Set")
        else:
            print(f"   {var}: ❌ Missing")
            all_set = False
    
    # Test 6: Rate Limiting Check
    print("\n6. Rate Limiting Test:")
    try:
        # Make multiple requests to test rate limiting
        for i in range(3):
            response = requests.get(f"{base_url}/auth/google", allow_redirects=False, timeout=5)
            if response.status_code == 429:
                print(f"   ❌ Rate limited on request {i+1}")
                break
        else:
            print("   ✅ No immediate rate limiting detected")
    except Exception as e:
        print(f"   ⚠️  Error testing rate limiting: {e}")
    
    print("\n📊 Verification Summary:")
    if all_set and oauth_service.is_configured():
        print("   ✅ All OAuth prerequisites are met")
        print("   ✅ Ready for Google authentication testing")
    else:
        print("   ❌ Some OAuth prerequisites are missing")
    
    print("\n🔧 Recommended Actions:")
    print("   1. Test the 'Sign in with Google' button on the landing page")
    print("   2. Verify redirect URIs are configured in Google Cloud Console:")
    print("      • https://workspace.replit.dev/auth/google/callback")
    print("      • https://workspace.replit.app/auth/google/callback")
    print("   3. Check application logs for any OAuth-related errors")
    
    return True

if __name__ == "__main__":
    try:
        verify_oauth_endpoints()
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)