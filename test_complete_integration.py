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
        print(f"{status} - {description}: {url}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ ERROR - {description}: {url} - {str(e)}")
        return False

def test_oauth_flow():
    """Test OAuth flow"""
    print("\n🔐 Testing OAuth Flow...")
    
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
                print(f"✅ OAuth endpoint working: {url}")
                oauth_working = True
                break
        except Exception as e:
            print(f"❌ OAuth endpoint failed: {url} - {str(e)}")
    
    return oauth_working

def main():
    """Run complete integration test"""
    print("🧪 NOUS Complete Integration Test")
    print("=" * 50)
    
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
    
    print("\n🌐 Testing Core Pathways...")
    passed = 0
    total = len(tests)
    
    for url, desc, expected in tests:
        if test_endpoint(url, desc, expected):
            passed += 1
    
    # Test OAuth flow
    oauth_working = test_oauth_flow()
    
    # Test modern UI elements
    print("\n🎨 Testing Modern UI Integration...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if "Inter" in response.text and "modern-chat.js" in response.text:
            print("✅ Modern UI integration confirmed")
            ui_working = True
        else:
            print("❌ Modern UI integration not detected")
            ui_working = False
    except Exception as e:
        print(f"❌ UI test failed: {str(e)}")
        ui_working = False
    
    # Generate report
    print("\n📊 Integration Test Report")
    print("=" * 50)
    print(f"Core Pathways: {passed}/{total} working")
    print(f"OAuth System: {'✅ Working' if oauth_working else '❌ Issues detected'}")
    print(f"Modern UI: {'✅ Integrated' if ui_working else '❌ Issues detected'}")
    
    overall_score = (passed / total) * 100
    print(f"\nOverall Health: {overall_score:.1f}%")
    
    if overall_score >= 80 and ui_working:
        print("🎉 INTEGRATION SUCCESS - System ready for production!")
        return True
    else:
        print("⚠️  INTEGRATION ISSUES - Some components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)