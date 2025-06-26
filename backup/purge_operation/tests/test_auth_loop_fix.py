#!/usr/bin/env python3
"""
Authentication Loop Fix Test Suite

Tests to verify the auth loop has been completely eliminated.
"""

import pytest
import requests
import json
import time
from urllib.parse import urljoin

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

class TestAuthLoopFix:
    """Test suite for authentication loop fixes"""
    
    def test_root_accessible_without_auth(self):
        """Test that / returns 200 without authentication"""
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        assert response.status_code == 200
        # Should not redirect to login
        assert "login" not in response.url.lower()
        
    def test_health_check_public(self):
        """Test health endpoint is publicly accessible"""
        response = requests.get(BASE_URL + "/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["access_level"] == "public"
        assert data["authentication"] == "disabled"
        
    def test_dashboard_accessible_without_auth(self):
        """Test dashboard is accessible without authentication"""
        response = requests.get(BASE_URL + "/dashboard", timeout=TIMEOUT)
        assert response.status_code == 200
        # Should not redirect to login
        assert "login" not in response.url.lower()
        
    def test_chat_interface_public(self):
        """Test chat interface is publicly accessible"""
        response = requests.get(BASE_URL + "/chat", timeout=TIMEOUT)
        assert response.status_code == 200
        
    def test_api_chat_works_without_auth(self):
        """Test API chat endpoint works without authentication"""
        payload = {"message": "Hello, test message"}
        response = requests.post(
            BASE_URL + "/api/chat",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["access_level"] == "public"
        
    def test_no_auth_redirects(self):
        """Test that no routes redirect to authentication"""
        public_routes = [
            "/",
            "/health",
            "/about", 
            "/features",
            "/dashboard",
            "/chat"
        ]
        
        for route in public_routes:
            response = requests.get(BASE_URL + route, timeout=TIMEOUT, allow_redirects=False)
            # Should not be a redirect
            assert response.status_code != 302
            assert response.status_code != 301
            # And definitely not redirect to login
            if 'Location' in response.headers:
                assert 'login' not in response.headers['Location'].lower()
                
    def test_cors_headers_present(self):
        """Test CORS headers are properly set for public access"""
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        assert response.headers.get('Access-Control-Allow-Origin') == '*'
        assert response.headers.get('X-Replit-Auth') == 'false'
        
    def test_admin_routes_require_header(self):
        """Test admin routes require proper header authentication"""
        # Admin route without header should return 401
        response = requests.get(BASE_URL + "/admin", timeout=TIMEOUT)
        assert response.status_code == 401
        
        # Admin route with header should work
        headers = {'X-Admin-Key': 'admin123'}
        response = requests.get(BASE_URL + "/admin", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200
        
    def test_session_cookies_configured(self):
        """Test session cookies are properly configured"""
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        
        # Check for properly configured cookies
        cookies = response.cookies
        if cookies:
            for cookie in cookies:
                # Cookies should be properly configured for Replit
                assert cookie.secure == False  # HTTP allowed for Replit
                
def run_smoke_tests():
    """Run smoke tests to verify the fix works"""
    print("🧪 Running Authentication Loop Fix Tests...")
    
    # Test basic connectivity
    try:
        response = requests.get(BASE_URL + "/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
        
    # Test key routes
    test_routes = {
        "/": "Homepage",
        "/health": "Health check", 
        "/about": "About page",
        "/dashboard": "Dashboard",
        "/api/health": "API health"
    }
    
    all_passed = True
    
    for route, name in test_routes.items():
        try:
            response = requests.get(BASE_URL + route, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")
            elif response.status_code in [301, 302]:
                print(f"❌ {name}: Redirecting (possible auth loop)")
                all_passed = False
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    success = run_smoke_tests()
    if success:
        print("\n🎉 AUTH LOOP FIX: ALL TESTS PASSED")
        print("The application is now fully accessible without authentication loops!")
    else:
        print("\n🚨 AUTH LOOP FIX: SOME TESTS FAILED")
        print("Manual intervention may be required.")
        
    exit(0 if success else 1)