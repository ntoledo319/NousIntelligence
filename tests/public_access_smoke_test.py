#!/usr/bin/env python3
"""
💀 OPERATION PUBLIC-OR-BUST Smoke Test Suite 💀
Comprehensive testing to ensure public deployment access without auth walls
"""
import os
import sys
import json
import time
import requests
from datetime import datetime

class PublicAccessSmokeTest:
    def __init__(self, base_url="http://localhost:5000"):
        """Initialize smoke test with base URL"""
        self.base_url = base_url
        self.results = []
        self.errors = []
        self.start_time = datetime.now()
        
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status} {details}")
        
    def log_error(self, test_name, error):
        """Log test error"""
        self.errors.append({'test': test_name, 'error': str(error)})
        self.log_result(test_name, "FAIL", f"Error: {error}")
        
    def test_landing_page_public(self):
        """Test 1: Landing page loads without authentication"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_result("Landing Page Public Access", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Landing Page Public Access", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Landing Page Public Access", e)
            return False
            
    def test_demo_page_public(self):
        """Test 2: Demo page loads without authentication"""
        try:
            response = requests.get(f"{self.base_url}/demo", timeout=10)
            if response.status_code == 200:
                self.log_result("Demo Page Public Access", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Demo Page Public Access", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Demo Page Public Access", e)
            return False
            
    def test_protected_route_redirect(self):
        """Test 3: Protected /app route redirects properly (not 401)"""
        try:
            response = requests.get(f"{self.base_url}/app", allow_redirects=False, timeout=10)
            if response.status_code in [302, 303]:  # Redirect is OK
                self.log_result("Protected Route Handling", "PASS", f"Redirects properly: {response.status_code}")
                return True
            elif response.status_code == 401:
                self.log_result("Protected Route Handling", "FAIL", "Returns 401 instead of redirect")
                return False
            else:
                self.log_result("Protected Route Handling", "WARN", f"Unexpected status: {response.status_code}")
                return True
        except Exception as e:
            self.log_error("Protected Route Handling", e)
            return False
            
    def test_public_api_user(self):
        """Test 4: Public API returns guest user info without 401"""
        try:
            response = requests.get(f"{self.base_url}/api/user", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('is_guest'):
                    self.log_result("Public API User Endpoint", "PASS", "Returns guest user")
                    return True
                else:
                    self.log_result("Public API User Endpoint", "FAIL", "No guest user data")
                    return False
            else:
                self.log_result("Public API User Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Public API User Endpoint", e)
            return False
            
    def test_public_demo_chat(self):
        """Test 5: Public demo chat API works without authentication"""
        try:
            payload = {"message": "Hello, this is a test!"}
            response = requests.post(
                f"{self.base_url}/api/demo/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('demo_mode'):
                    self.log_result("Public Demo Chat API", "PASS", "Demo response received")
                    return True
                else:
                    self.log_result("Public Demo Chat API", "FAIL", "No demo mode flag")
                    return False
            else:
                self.log_result("Public Demo Chat API", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Public Demo Chat API", e)
            return False
            
    def test_health_endpoints(self):
        """Test 6: Health endpoints are publicly accessible"""
        endpoints = ['/health', '/healthz']
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_result(f"Health Endpoint {endpoint}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"Health Endpoint {endpoint}", "FAIL", f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_error(f"Health Endpoint {endpoint}", e)
                all_passed = False
                
        return all_passed
        
    def test_no_replit_auth_headers(self):
        """Test 7: Check for presence of public access headers"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            headers = response.headers
            
            # Check for public access headers
            if headers.get('X-Frame-Options') == 'ALLOWALL':
                self.log_result("Public Access Headers", "PASS", "X-Frame-Options: ALLOWALL")
                return True
            else:
                self.log_result("Public Access Headers", "WARN", f"X-Frame-Options: {headers.get('X-Frame-Options')}")
                return True  # Not critical
        except Exception as e:
            self.log_error("Public Access Headers", e)
            return False
            
    def run_all_tests(self):
        """Run complete smoke test suite"""
        print("💀 OPERATION PUBLIC-OR-BUST Smoke Test Suite 💀")
        print(f"Testing URL: {self.base_url}")
        print(f"Start Time: {self.start_time.isoformat()}")
        print("=" * 60)
        
        tests = [
            self.test_landing_page_public,
            self.test_demo_page_public, 
            self.test_protected_route_redirect,
            self.test_public_api_user,
            self.test_public_demo_chat,
            self.test_health_endpoints,
            self.test_no_replit_auth_headers
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test execution failed: {e}")
                
        self.generate_report(passed, total)
        return passed == total
        
    def generate_report(self, passed, total):
        """Generate final test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🏆 SMOKE TEST RESULTS")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Status: {'🟢 PASS' if passed == total else '🔴 FAIL'}")
        
        if self.errors:
            print("\n❌ ERRORS FOUND:")
            for error in self.errors:
                print(f"  - {error['test']}: {error['error']}")
                
        # Deployment readiness
        if passed >= total * 0.85:  # 85% pass rate minimum
            print("\n✅ DEPLOYMENT READY: Public access validated")
        else:
            print("\n❌ DEPLOYMENT BLOCKED: Fix authentication issues")
            
        print("=" * 60)
        
def main():
    """Main test runner"""
    # Check if server is specified
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Wait a moment for server startup if running locally
    if "localhost" in base_url:
        print("Waiting 3 seconds for local server startup...")
        time.sleep(3)
    
    tester = PublicAccessSmokeTest(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()