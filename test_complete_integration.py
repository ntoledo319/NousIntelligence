import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Complete Integration Test
Tests all pathways, OAuth, and modern UI integration
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_endpoint(url, description, expected_status=200):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=10)
        status = "✅ PASS" if response.status_code == expected_status else f"❌ FAIL ({response.status_code})"
        logger.info({status} - {description}: {url})
        return response.status_code == expected_status
    except Exception as e:
        logger.error(❌ ERROR - {description}: {url} - {str(e)})
        return False

def test_oauth_flow():
    """Test OAuth flow"""
    logger.info(\n🔐 Testing OAuth Flow...)
    
    # Test OAuth login initiation
    oauth_urls = [
        "http://localhost:8080/auth/google_login",
        "http://localhost:8080/auth/login", 
        "http://localhost:8080/callback/google"
    ]
    
    oauth_working = False
    for url in oauth_urls:
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            if response.status_code in [302, 200]:  # Redirect to Google or login page
                logger.info(✅ OAuth endpoint working: {url})
                oauth_working = True
                break
        except Exception as e:
            logger.info(❌ OAuth endpoint failed: {url} - {str(e)})
    
    return oauth_working

def main():
    """Run complete integration test"""
    logger.info(🧪 NOUS Complete Integration Test)
    logger.info(=)
    
    base_url = "http://localhost:8080"
    
    # Test core pathways
    tests = [
        (f"{base_url}/", "Landing Page", 200),
        (f"{base_url}/demo", "Demo Interface", 200),
        (f"{base_url}/public", "Public Access", 200),
        (f"{base_url}/health", "Health Check", 200),
        (f"{base_url}/api/health", "API Health", 200),
        (f"{base_url}/api/v1/health", "API V1 Health", 200),
    ]
    
    logger.info(\n🌐 Testing Core Pathways...)
    passed = 0
    total = len(tests)
    
    for url, desc, expected in tests:
        if test_endpoint(url, desc, expected):
            passed += 1
    
    # Test OAuth flow
    oauth_working = test_oauth_flow()
    
    # Test modern UI elements
    logger.info(\n🎨 Testing Modern UI Integration...)
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if "Inter" in response.text and "modern-chat.js" in response.text:
            logger.info(✅ Modern UI integration confirmed)
            ui_working = True
        else:
            logger.info(❌ Modern UI integration not detected)
            ui_working = False
    except Exception as e:
        logger.info(❌ UI test failed: {str(e)})
        ui_working = False
    
    # Generate report
    logger.info(\n📊 Integration Test Report)
    logger.info(=)
    logger.info(Core Pathways: {passed}/{total} working)
    logger.info(OAuth System: {'✅ Working' if oauth_working else '❌ Issues detected'})
    logger.info(Modern UI: {'✅ Integrated' if ui_working else '❌ Issues detected'})
    
    overall_score = (passed / total) * 100
    logger.info(\nOverall Health: {overall_score:.1f}%)
    
    if overall_score >= 80 and ui_working:
        logger.info(🎉 INTEGRATION SUCCESS - System ready for production!)
        return True
    else:
        logger.info(⚠️  INTEGRATION ISSUES - Some components need attention)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)