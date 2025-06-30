#!/usr/bin/env python3
"""
Check Deployed OAuth Status
Investigate OAuth issues on the deployed application
"""

import requests
import os
import sys

def check_deployed_oauth():
    """Check OAuth status on deployed application"""
    
    print("🔍 Checking Deployed OAuth Status")
    print("=" * 50)
    
    # Get the deployed URL from environment or use default
    base_url = os.environ.get('REPL_URL', 'https://workspace.replit.dev')
    
    print(f"Testing deployment at: {base_url}")
    
    try:
        # Test 1: Landing page
        print("\n1. Landing Page Test:")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            has_google_button = 'Sign in with Google' in response.text or 'google' in response.text.lower()
            print(f"   Google sign-in button: {'✅ Found' if has_google_button else '❌ Missing'}")
            
            # Check for any error messages
            if 'error' in response.text.lower() or 'failed' in response.text.lower():
                print("   ⚠️  Possible error messages found in page")
        else:
            print(f"   ❌ Landing page failed: {response.status_code}")
            return
            
        # Test 2: OAuth endpoint
        print("\n2. OAuth Endpoint Test:")
        oauth_url = f"{base_url}/auth/google"
        oauth_response = requests.get(oauth_url, allow_redirects=False, timeout=10)
        print(f"   OAuth endpoint status: {oauth_response.status_code}")
        
        if oauth_response.status_code == 302:
            location = oauth_response.headers.get('Location', '')
            print(f"   Redirect location: {location}")
            
            if 'accounts.google.com' in location:
                print("   ✅ OAuth working: Redirecting to Google")
            elif 'login' in location:
                print("   ❌ OAuth not working: Redirecting to login page")
            else:
                print(f"   ⚠️  Unexpected redirect: {location}")
        else:
            print(f"   ❌ OAuth endpoint error: {oauth_response.status_code}")
            if oauth_response.text:
                print(f"   Response: {oauth_response.text[:200]}...")
                
        # Test 3: Health check
        print("\n3. Health Check:")
        try:
            health_response = requests.get(f"{base_url}/api/health", timeout=10)
            print(f"   Health endpoint status: {health_response.status_code}")
            if health_response.status_code == 200:
                try:
                    health_data = health_response.json()
                    print(f"   Health status: {health_data.get('status', 'unknown')}")
                except:
                    print("   Health response not JSON")
        except Exception as e:
            print(f"   Health check failed: {e}")
            
        # Test 4: Check for common OAuth issues
        print("\n4. Common OAuth Issues Check:")
        
        # Check redirect URI mismatch
        print("   Checking redirect URI configuration...")
        callback_url = f"{base_url}/auth/google/callback"
        print(f"   Expected callback URI: {callback_url}")
        print("   ⚠️  Verify this URI is configured in Google Cloud Console")
        
        # Check environment variables (can't access directly, but check behavior)
        print("   Environment variables check:")
        print("   • GOOGLE_CLIENT_ID: Check if configured in Replit Secrets")
        print("   • GOOGLE_CLIENT_SECRET: Check if configured in Replit Secrets")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        
    print("\n" + "=" * 50)
    print("OAuth Status Check Complete")

if __name__ == "__main__":
    check_deployed_oauth()