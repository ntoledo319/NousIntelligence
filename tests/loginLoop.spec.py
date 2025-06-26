#!/usr/bin/env python3
"""
Login Loop Elimination Test Suite

Tests to verify authentication loops have been completely eliminated
according to the ONE-PROMPT LOGIN-LOOP EXORCIST protocol.
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

def test_basic_connectivity():
    """Test that server is responsive"""
    print("🔍 Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_homepage_no_redirect():
    """GET / => expect 200, no authentication redirect"""
    print("🔍 Testing homepage accessibility...")
    try:
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT, allow_redirects=False)
        if response.status_code == 200:
            print("✅ Homepage: Direct access (200)")
            return True
        elif response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', 'unknown')
            print(f"❌ Homepage: Redirecting to {location} (possible auth loop)")
            return False
        else:
            print(f"⚠️  Homepage: Unexpected status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Homepage: Error - {e}")
        return False

def test_dashboard_accessibility():
    """GET /dashboard => expect 200, no login requirement"""
    print("🔍 Testing dashboard accessibility...")
    try:
        response = requests.get(BASE_URL + "/dashboard", timeout=TIMEOUT, allow_redirects=False)
        if response.status_code == 200:
            print("✅ Dashboard: Direct access (200)")
            return True
        elif response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', 'unknown')
            print(f"❌ Dashboard: Redirecting to {location} (auth loop detected)")
            return False
        else:
            print(f"⚠️  Dashboard: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard: Error - {e}")
        return False

def test_api_chat_functionality():
    """POST /api/chat => expect 200, functional API"""
    print("🔍 Testing chat API functionality...")
    try:
        payload = {"message": "Hello from smoke test"}
        response = requests.post(
            BASE_URL + "/api/chat", 
            json=payload, 
            timeout=TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print("✅ Chat API: Functional and accessible")
                return True
            else:
                print("⚠️  Chat API: Missing response field")
                return False
        else:
            print(f"❌ Chat API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat API: Error - {e}")
        return False

def test_health_endpoints():
    """Test health check endpoints"""
    print("🔍 Testing health endpoints...")
    endpoints = ["/health", "/healthz"]
    all_passed = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(BASE_URL + endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Healthy")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_cors_headers():
    """Test CORS headers for public access"""
    print("🔍 Testing CORS headers...")
    try:
        response = requests.get(BASE_URL + "/", timeout=5)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_header == '*':
            print("✅ CORS: Public access enabled")
            return True
        else:
            print(f"⚠️  CORS: Header value '{cors_header}' (should be '*')")
            return False
    except Exception as e:
        print(f"❌ CORS: Error - {e}")
        return False

def test_no_auth_headers():
    """Test that authentication headers indicate disabled auth"""
    print("🔍 Testing authentication headers...")
    try:
        response = requests.get(BASE_URL + "/", timeout=5)
        replit_auth = response.headers.get('X-Replit-Auth', '').lower()
        
        if replit_auth == 'false':
            print("✅ Auth Headers: Authentication disabled")
            return True
        else:
            print(f"⚠️  Auth Headers: X-Replit-Auth = '{replit_auth}' (should be 'false')")
            return False
    except Exception as e:
        print(f"❌ Auth Headers: Error - {e}")
        return False

def run_smoke_tests():
    """Run complete smoke test suite"""
    print("🪓 ONE-PROMPT LOGIN-LOOP EXORCIST - SMOKE TESTS 🪓")
    print("=" * 60)
    
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("Homepage Access", test_homepage_no_redirect),
        ("Dashboard Access", test_dashboard_accessibility),
        ("Chat API Function", test_api_chat_functionality),
        ("Health Endpoints", test_health_endpoints),
        ("CORS Headers", test_cors_headers),
        ("Auth Headers", test_no_auth_headers)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
        else:
            print(f"💥 {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 SMOKE TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 AUTH LOOP EXORCISM: SUCCESSFUL!")
        print("✅ All routes accessible without authentication loops")
        print("✅ API functionality confirmed")
        print("✅ CORS and security headers properly configured")
        print("🚀 DEPLOYMENT READY - No authentication barriers remain")
        return True
    else:
        print("🚨 AUTH LOOP EXORCISM: INCOMPLETE")
        print(f"❌ {total - passed} tests failed")
        print("🔧 Manual intervention required")
        return False

if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)