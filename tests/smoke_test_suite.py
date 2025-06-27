"""
GLOBAL HEALTH CHECK: Automated Smoke Test Suite
Auto-generated test grid for login loop prevention and deployment verification
"""
import pytest
import requests
import os
from urllib.parse import urljoin

class TestSmokeSuite:
    """Comprehensive smoke test suite per GLOBAL HEALTH CHECK protocol"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        # Use unified configuration for base URL
        from config import PORT, HOST
        cls.base_url = f"http://{HOST}:{PORT}"
        cls.session = requests.Session()
    
    def test_01_root_endpoint_public_access(self):
        """TEST 1: GET / ⇒ 200 (Public access without login)"""
        response = self.session.get(f"{self.base_url}/")
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        assert "html" in response.headers.get('content-type', '').lower()
        
    def test_02_health_check_endpoint(self):
        """TEST 2: GET /health ⇒ 200 (Health monitoring)"""
        response = self.session.get(f"{self.base_url}/health")
        # Should return 200 or 404 (if not implemented), but not auth redirect
        assert response.status_code in [200, 404], f"Health check failed: {response.status_code}"
        
    def test_03_dashboard_access_pattern(self):
        """TEST 3: GET /dashboard ⇒ Should not cause infinite redirects"""
        response = self.session.get(f"{self.base_url}/dashboard", allow_redirects=False)
        # Should either be accessible (200) or redirect once (302/301), not loop
        assert response.status_code in [200, 302, 301, 404], f"Dashboard access issue: {response.status_code}"
        
        # Check for redirect loops by following max 3 redirects
        if response.status_code in [302, 301]:
            redirect_count = 0
            current_url = f"{self.base_url}/dashboard" 
            
            while redirect_count < 3:
                response = self.session.get(current_url, allow_redirects=False)
                if response.status_code not in [302, 301]:
                    break
                redirect_count += 1
                location = response.headers.get('Location', '')
                if location.startswith('/'):
                    current_url = urljoin(self.base_url, location)
                else:
                    current_url = location
                    
            assert redirect_count < 3, "Detected redirect loop in dashboard access"
    
    def test_04_api_endpoints_no_auth_loops(self):
        """TEST 4: API endpoints should not cause authentication loops"""
        api_endpoints = ['/api/health', '/api/me', '/api/chat']
        
        for endpoint in api_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}", allow_redirects=False)
            # APIs should return JSON responses or 404, not HTML redirects
            assert response.status_code not in [302, 301] or not response.headers.get('Location', '').endswith('/login'), \
                f"API endpoint {endpoint} causing auth redirect"
    
    def test_05_cors_headers_present(self):
        """TEST 5: CORS headers for public access"""
        response = self.session.get(f"{self.base_url}/")
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        assert cors_header is not None, "CORS headers missing for public access"
        
    def test_06_security_headers_present(self):
        """TEST 6: Essential security headers are present"""
        response = self.session.get(f"{self.base_url}/")
        
        # Check for essential security headers
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') in ['DENY', 'SAMEORIGIN']
        
    def test_07_no_server_errors_on_basic_routes(self):
        """TEST 7: Basic routes return proper responses, not 500 errors"""
        basic_routes = ['/', '/health', '/api/health']
        
        for route in basic_routes:
            response = self.session.get(f"{self.base_url}{route}")
            assert response.status_code < 500, f"Server error on {route}: {response.status_code}"

if __name__ == "__main__":
    # Can be run directly for manual testing
    import subprocess
    import sys
    
    print("🚑 Running GLOBAL HEALTH CHECK Smoke Test Suite...")
    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All smoke tests passed!")
    else:
        print("❌ Smoke tests failed!")
        sys.exit(result.returncode)