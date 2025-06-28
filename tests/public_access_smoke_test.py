#!/usr/bin/env python3
"""
OPERATION PUBLIC-OR-BUST Smoke Test Suite
Tests the 6 critical scenarios to ensure public deployment success
"""

import requests
import sys
import time
import json
from datetime import datetime


class PublicAccessSmokeTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log_test(self, test_name, success, response_code=None, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'response_code': response_code,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        code_info = f" [{response_code}]" if response_code else ""
        print(f"{status}{code_info} {test_name}: {details}")
        
    def test_1_public_root_access(self):
        """Test 1: GET / → 200 (public access without login)"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            details = "Public root accessible" if success else f"Expected 200, got {response.status_code}"
            self.log_test("Public Root Access", success, response.status_code, details)
            return success
        except Exception as e:
            self.log_test("Public Root Access", False, None, f"Request failed: {e}")
            return False
    
    def test_2_protected_route_blocks(self):
        """Test 2: GET /protected unauth → 302→/login OR 401"""
        try:
            # Try accessing a protected route that should require auth
            response = self.session.get(f"{self.base_url}/app")  # Main app requires auth
            success = response.status_code in [302, 401, 403]
            details = f"Protected route properly blocked" if success else f"Expected 302/401/403, got {response.status_code}"
            self.log_test("Protected Route Blocking", success, response.status_code, details)
            return success
        except Exception as e:
            self.log_test("Protected Route Blocking", False, None, f"Request failed: {e}")
            return False
    
    def test_3_health_endpoints(self):
        """Test 3: Health endpoints → 200"""
        endpoints = ['/health', '/healthz']
        all_success = True
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                success = response.status_code == 200
                details = f"Health endpoint working" if success else f"Expected 200, got {response.status_code}"
                self.log_test(f"Health Endpoint {endpoint}", success, response.status_code, details)
                all_success = all_success and success
            except Exception as e:
                self.log_test(f"Health Endpoint {endpoint}", False, None, f"Request failed: {e}")
                all_success = False
                
        return all_success
    
    def test_4_oauth_flow_available(self):
        """Test 4: OAuth login flow available"""
        try:
            response = self.session.get(f"{self.base_url}/login")
            success = response.status_code in [200, 302]  # Either login page or redirect to OAuth
            details = "Login flow accessible" if success else f"Expected 200/302, got {response.status_code}"
            self.log_test("OAuth Flow Available", success, response.status_code, details)
            return success
        except Exception as e:
            self.log_test("OAuth Flow Available", False, None, f"Request failed: {e}")
            return False
    
    def test_5_static_assets(self):
        """Test 5: Static assets loadable"""
        try:
            response = self.session.get(f"{self.base_url}/static/styles.css")
            success = response.status_code == 200
            details = "Static assets accessible" if success else f"Expected 200, got {response.status_code}"
            self.log_test("Static Assets", success, response.status_code, details)
            return success
        except Exception as e:
            self.log_test("Static Assets", False, None, f"Request failed: {e}")
            return False
    
    def test_6_api_accessibility(self):
        """Test 6: Public API endpoints work"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            success = response.status_code == 200
            details = "API endpoints accessible" if success else f"Expected 200, got {response.status_code}"
            self.log_test("API Accessibility", success, response.status_code, details)
            return success
        except Exception as e:
            self.log_test("API Accessibility", False, None, f"Request failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete smoke test suite"""
        print("🔥 OPERATION PUBLIC-OR-BUST SMOKE TESTS")
        print("=" * 50)
        print(f"Testing: {self.base_url}")
        print()
        
        tests = [
            self.test_1_public_root_access,
            self.test_2_protected_route_blocks,
            self.test_3_health_endpoints,
            self.test_4_oauth_flow_available,
            self.test_5_static_assets,
            self.test_6_api_accessibility
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print()
        print("=" * 50)
        print(f"📊 RESULTS: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("🎉 ALL TESTS PASSED - DEPLOYMENT READY!")
            return True
        else:
            print(f"💀 {len(tests) - passed} TESTS FAILED - FIX REQUIRED!")
            return False
    
    def save_results(self, filename="smoke_test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_tests': len(self.results),
                'passed': sum(1 for r in self.results if r['success']),
                'failed': sum(1 for r in self.results if not r['success']),
                'results': self.results
            }, f, indent=2)


def main():
    """Main test runner"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = PublicAccessSmokeTest(base_url)
    success = tester.run_all_tests()
    tester.save_results()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()