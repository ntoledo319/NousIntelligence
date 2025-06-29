#!/usr/bin/env python3
"""
Public Access Verification Suite
Comprehensive testing to ensure the application is fully accessible to the public
"""
import os
import sys
import requests
import json
from datetime import datetime

class PublicAccessTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
            
    def test_landing_page(self):
        """Test that landing page loads publicly"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                if "Try Demo Now" in response.text:
                    self.log_test("Landing Page Access", "PASS", "Landing page loads with demo button")
                    return True
                else:
                    self.log_test("Landing Page Access", "WARN", "Landing page loads but no demo button found")
                    return False
            else:
                self.log_test("Landing Page Access", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Landing Page Access", "FAIL", f"Error: {e}")
            return False
            
    def test_public_demo_page(self):
        """Test that demo page loads without authentication"""
        try:
            response = requests.get(f"{self.base_url}/demo", timeout=10)
            if response.status_code == 200:
                self.log_test("Public Demo Page", "PASS", "Demo page accessible without auth")
                return True
            else:
                self.log_test("Public Demo Page", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Public Demo Page", "FAIL", f"Error: {e}")
            return False
            
    def test_health_endpoints(self):
        """Test health endpoints are publicly accessible"""
        endpoints = ['/health', '/healthz']
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') in ['healthy', 'functional_with_limitations']:
                        self.log_test(f"Health Endpoint {endpoint}", "PASS", f"Status: {data.get('status')}")
                    else:
                        self.log_test(f"Health Endpoint {endpoint}", "WARN", f"Unexpected status: {data.get('status')}")
                        all_passed = False
                else:
                    self.log_test(f"Health Endpoint {endpoint}", "FAIL", f"Status code: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Health Endpoint {endpoint}", "FAIL", f"Error: {e}")
                all_passed = False
                
        return all_passed
        
    def test_public_api_endpoints(self):
        """Test that API endpoints work without authentication"""
        tests = [
            ("/api/user", "GET", None, "Should return guest user info"),
            ("/api/demo/chat", "POST", {"message": "Hello!"}, "Should work without auth"),
            ("/api/analytics", "GET", None, "Should return demo analytics"),
            ("/api/v1/search/", "GET", None, "Should return demo search results"),
            ("/api/v1/notifications/", "GET", None, "Should return demo notifications")
        ]
        
        all_passed = True
        
        for endpoint, method, payload, description in tests:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}", 
                        json=payload, 
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('demo_mode') or data.get('is_guest') or 'demo' in str(data).lower():
                            self.log_test(f"API {endpoint}", "PASS", description)
                        else:
                            self.log_test(f"API {endpoint}", "PASS", f"Working but not explicitly demo mode")
                    except:
                        self.log_test(f"API {endpoint}", "PASS", "Returns data (non-JSON)")
                elif response.status_code == 401:
                    self.log_test(f"API {endpoint}", "FAIL", "Still requires authentication!")
                    all_passed = False
                else:
                    self.log_test(f"API {endpoint}", "WARN", f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API {endpoint}", "FAIL", f"Error: {e}")
                all_passed = False
                
        return all_passed
        
    def test_no_authentication_loops(self):
        """Test that there are no authentication redirect loops"""
        try:
            # Test with session that doesn't allow redirects to catch loops
            session = requests.Session()
            session.max_redirects = 3
            
            response = session.get(f"{self.base_url}/app", allow_redirects=True, timeout=10)
            
            # If we get redirected to login, that's OK, but should not loop
            if response.url.endswith('/login') or response.url.endswith('/'):
                self.log_test("No Auth Loops", "PASS", "Proper redirect without loops")
                return True
            elif response.status_code == 200:
                self.log_test("No Auth Loops", "PASS", "App accessible or proper landing")
                return True
            else:
                self.log_test("No Auth Loops", "WARN", f"Unexpected behavior: {response.status_code}")
                return False
                
        except requests.exceptions.TooManyRedirects:
            self.log_test("No Auth Loops", "FAIL", "Authentication redirect loop detected!")
            return False
        except Exception as e:
            self.log_test("No Auth Loops", "FAIL", f"Error: {e}")
            return False
            
    def test_demo_functionality(self):
        """Test that demo functionality works end-to-end"""
        try:
            # Test demo chat API
            payload = {"message": "Test message from verification suite"}
            response = requests.post(
                f"{self.base_url}/api/demo/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('demo_mode') and data.get('message'):
                    self.log_test("Demo Chat Functionality", "PASS", "Demo chat works end-to-end")
                    return True
                else:
                    self.log_test("Demo Chat Functionality", "WARN", "Demo chat responds but format unexpected")
                    return False
            else:
                self.log_test("Demo Chat Functionality", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Demo Chat Functionality", "FAIL", f"Error: {e}")
            return False
            
    def run_all_tests(self):
        """Run all public access verification tests"""
        print("🧪 RUNNING PUBLIC ACCESS VERIFICATION TESTS")
        print("=" * 60)
        
        tests = [
            ("Landing Page Access", self.test_landing_page),
            ("Public Demo Page", self.test_public_demo_page),
            ("Health Endpoints", self.test_health_endpoints),
            ("Public API Endpoints", self.test_public_api_endpoints),
            ("No Authentication Loops", self.test_no_authentication_loops),
            ("Demo Functionality", self.test_demo_functionality)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "ERROR", f"Test crashed: {e}")
                
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Application is publicly accessible!")
            return True
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Minor issues may exist.")
            return False
        else:
            print("❌ CRITICAL ISSUES FOUND! Application may not be publicly accessible.")
            return False
            
    def generate_report(self):
        """Generate verification report"""
        report = {
            'verification_timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r['status'] == 'PASS']),
            'failed_tests': len([r for r in self.results if r['status'] == 'FAIL']),
            'warning_tests': len([r for r in self.results if r['status'] == 'WARN']),
            'results': self.results
        }
        
        with open('public_access_verification_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📋 Verification report saved to public_access_verification_report.json")
        return report

def main():
    """Run public access verification"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = PublicAccessTester(base_url)
    success = tester.run_all_tests()
    tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())