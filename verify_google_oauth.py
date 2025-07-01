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
    
    logger.info(🔍 Google OAuth Verification Test)
    logger.info(=)
    
    # Test 1: Application Health Check
    logger.info(\n1. Application Health Check:)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        logger.info(   Landing Page: {'✅ OK' if response.status_code == 200 else '❌ Failed'} ({response.status_code}))
    except Exception as e:
        logger.error(   Landing Page: ❌ Error - {e})
        return False
    
    # Test 2: Google Sign-in Button
    logger.info(\n2. Google Sign-in Button Test:)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if "Sign in with Google" in response.text:
            logger.info(   ✅ Google sign-in button found on landing page)
        else:
            logger.info(   ❌ Google sign-in button not found)
    except Exception as e:
        logger.error(   ❌ Error checking landing page: {e})
    
    # Test 3: OAuth Endpoint Response
    logger.info(\n3. OAuth Endpoint Response:)
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False, timeout=5)
        logger.info(   Status Code: {response.status_code})
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            logger.info(   Redirect Location: {location})
            
            if 'accounts.google.com' in location:
                logger.info(   ✅ Correctly redirecting to Google OAuth)
            elif 'auth/login' in location:
                logger.info(   ⚠️  Redirecting to login page - possible rate limiting or config issue)
            else:
                logger.info(   ❌ Unexpected redirect: {location})
        else:
            logger.info(   ❌ Expected 302 redirect, got different status)
            
    except Exception as e:
        logger.error(   ❌ Error testing OAuth endpoint: {e})
    
    # Test 4: OAuth Service Configuration
    logger.info(\n4. OAuth Service Configuration:)
    logger.info(   OAuth Service Configured: {'✅ Yes' if oauth_service.is_configured() else '❌ No'})
    
    if oauth_service.google:
        logger.info(   ✅ Google OAuth client initialized)
    else:
        logger.info(   ❌ Google OAuth client not initialized)
    
    # Test 5: Environment Variables
    logger.info(\n5. Environment Variables Check:)
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
    all_set = True
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            logger.info(   {var}: ✅ Set)
        else:
            logger.info(   {var}: ❌ Missing)
            all_set = False
    
    # Test 6: Rate Limiting Check
    logger.info(\n6. Rate Limiting Test:)
    try:
        # Make multiple requests to test rate limiting
        for i in range(3):
            response = requests.get(f"{base_url}/auth/google", allow_redirects=False, timeout=5)
            if response.status_code == 429:
                logger.info(   ❌ Rate limited on request {i+1})
                break
        else:
            logger.info(   ✅ No immediate rate limiting detected)
    except Exception as e:
        logger.error(   ⚠️  Error testing rate limiting: {e})
    
    logger.info(\n📊 Verification Summary:)
    if all_set and oauth_service.is_configured():
        logger.info(   ✅ All OAuth prerequisites are met)
        logger.info(   ✅ Ready for Google authentication testing)
    else:
        logger.info(   ❌ Some OAuth prerequisites are missing)
    
    logger.info(\n🔧 Recommended Actions:)
    logger.info(   1. Test the 'Sign in with Google' button on the landing page)
    logger.info(   2. Verify redirect URIs are configured in Google Cloud Console:)
    logger.info(      • https://workspace.replit.dev/auth/google/callback)
    logger.info(      • https://workspace.replit.app/auth/google/callback)
    logger.error(   3. Check application logs for any OAuth-related errors)
    
    return True

if __name__ == "__main__":
    try:
        verify_oauth_endpoints()
    except KeyboardInterrupt:
        logger.info(\n⚠️  Verification interrupted by user)
    except Exception as e:
        logger.info(\n❌ Verification failed: {e})
        sys.exit(1)