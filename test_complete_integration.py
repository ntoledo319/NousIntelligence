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
        if response.status_code == expected_status:
            status = "PASS"
            logger.info("{} - {}: {}".format(status, description, url))
        else:
            status = "FAIL ({}))".format(response.status_code)
            logger.warning("{} - {}: {}".format(status, description, url))
        return response.status_code == expected_status
    except Exception as e:
        logger.error("ERROR - {}: {} - {}".format(description, url, str(e)))
        return False

def test_oauth_flow():
    """Test OAuth flow"""
    logger.info("\nTesting OAuth Flow...")
    
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
                logger.info("✅ OAuth endpoint working: {}".format(url))
                oauth_working = True
                break
        except Exception as e:
            logger.info("❌ OAuth endpoint failed: {} - {}".format(url, str(e)))
    
    return oauth_working

def main():
    """Run complete integration test"""
    logger.info("NOUS Complete Integration Test")
    logger.info("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test core pathways
    tests = [
        ("{}/".format(base_url), "Landing Page", 200),
        ("{}/demo".format(base_url), "Demo Interface", 200),
        ("{}/public".format(base_url), "Public Access", 200),
        ("{}/health".format(base_url), "Health Check", 200),
        ("{}/api/health".format(base_url), "API Health", 200),
        ("{}/api/v1/health".format(base_url), "API V1 Health", 200),
    ]
    
    logger.info("\nTesting Core Pathways...")
    passed = 0
    total = len(tests)
    
    for url, desc, expected in tests:
        if test_endpoint(url, desc, expected):
            passed += 1
    
    # Test OAuth flow
    oauth_working = test_oauth_flow()
    
    # Test modern UI elements
    logger.info("\nTesting Modern UI Integration...")
    try:
        response = requests.get("{}/".format(base_url), timeout=10)
        if "Inter" in response.text and "modern-chat.js" in response.text:
            logger.info("Modern UI integration confirmed")
            ui_working = True
        else:
            logger.warning("Modern UI integration not detected")
            ui_working = False
    except Exception as e:
        logger.error("UI test failed: {}".format(str(e)))
        ui_working = False
    
    # Generate report
    logger.info("\nIntegration Test Report")
    logger.info("=" * 50)
    logger.info("Core Pathways: {}/{} working".format(passed, total))
    logger.info("OAuth System: {}".format("Working" if oauth_working else "Issues detected"))
    logger.info("Modern UI: {}".format("Integrated" if ui_working else "Issues detected"))
    
    overall_score = (passed / total) * 100 if total > 0 else 0
    logger.info("\nOverall Health: {:.1f}%".format(overall_score))
    
    if overall_score >= 80 and ui_working:
        logger.info("INTEGRATION SUCCESS - System ready for production!")
        return True
    else:
        logger.warning("INTEGRATION ISSUES - Some components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)