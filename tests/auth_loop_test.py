"""
Operation Zero-Redirect: Smoke Test Suite
Tests authentication flow to prevent redirect loops
"""
import requests
import sys
import json
from urllib.parse import urljoin

class AuthLoopTester:
    def __init__(self, base_url=None):
        if base_url is None:
            from config import PORT, HOST
            base_url = f'http://{HOST}:{PORT}'
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_public_landing_page(self):
        """Test 1: GET / should return 200"""
        try:
            response = self.session.get(self.base_url + '/')
            success = response.status_code == 200
            self.log_test(
                "Public Landing Page",
                success,
                f"Status: {response.status_code}, Content length: {len(response.text)}"
            )
            return success
        except Exception as e:
            self.log_test("Public Landing Page", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_page_unauthenticated(self):
        """Test 2: GET /app.html unauth should return 401 or 302"""
        try:
            response = self.session.get(self.base_url + '/app.html')
            success = response.status_code in [401, 302]
            self.log_test(
                "Protected Page (Unauth)",
                success,
                f"Status: {response.status_code} (Expected: 401 or 302)"
            )
            return success
        except Exception as e:
            self.log_test("Protected Page (Unauth)", False, f"Exception: {str(e)}")
            return False
    
    def test_login_creates_session(self):
        """Test 3: POST /api/login should return 200 + Set-Cookie"""
        try:
            login_data = {
                'username': 'test_user',
                'password': 'test_password'
            }
            response = self.session.post(
                self.base_url + '/api/login',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = (
                response.status_code == 200 and
                'Set-Cookie' in response.headers
            )
            
            cookie_info = "Set-Cookie present" if 'Set-Cookie' in response.headers else "No Set-Cookie"
            
            self.log_test(
                "Login Creates Session",
                success,
                f"Status: {response.status_code}, Cookie: {cookie_info}"
            )
            return success
        except Exception as e:
            self.log_test("Login Creates Session", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_page_authenticated(self):
        """Test 4: GET /app.html with cookie should return 200"""
        try:
            response = self.session.get(self.base_url + '/app.html')
            success = response.status_code == 200
            self.log_test(
                "Protected Page (Auth)",
                success,
                f"Status: {response.status_code}, Content length: {len(response.text)}"
            )
            return success
        except Exception as e:
            self.log_test("Protected Page (Auth)", False, f"Exception: {str(e)}")
            return False
    
    def test_me_endpoint_authenticated(self):
        """Test 5: GET /api/me with session should return user data"""
        try:
            response = self.session.get(self.base_url + '/api/me')
            success = response.status_code == 200
            
            if success and response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    user_info = f"User: {data.get('user', {}).get('username', 'unknown')}"
                except:
                    user_info = "JSON parse error"
            else:
                user_info = "No JSON response"
            
            self.log_test(
                "Me Endpoint (Auth)",
                success,
                f"Status: {response.status_code}, {user_info}"
            )
            return success
        except Exception as e:
            self.log_test("Me Endpoint (Auth)", False, f"Exception: {str(e)}")
            return False
    
    def test_logout_destroys_session(self):
        """Test 6: POST /api/logout should return 204"""
        try:
            response = self.session.post(self.base_url + '/api/logout')
            success = response.status_code == 204
            self.log_test(
                "Logout Destroys Session",
                success,
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.log_test("Logout Destroys Session", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_page_after_logout(self):
        """Test 7: GET /app.html after logout should return 401/302"""
        try:
            response = self.session.get(self.base_url + '/app.html')
            success = response.status_code in [401, 302]
            self.log_test(
                "Protected Page (After Logout)",
                success,
                f"Status: {response.status_code} (Expected: 401 or 302)"
            )
            return success
        except Exception as e:
            self.log_test("Protected Page (After Logout)", False, f"Exception: {str(e)}")
            return False
    
    def test_health_endpoint(self):
        """Test 8: Health endpoint should always be accessible"""
        try:
            response = self.session.get(self.base_url + '/health')
            success = response.status_code == 200
            
            if success:
                try:
                    data = response.json()
                    health_status = data.get('status', 'unknown')
                except:
                    health_status = 'JSON parse error'
            else:
                health_status = 'No response'
            
            self.log_test(
                "Health Endpoint",
                success,
                f"Status: {response.status_code}, Health: {health_status}"
            )
            return success
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 OPERATION ZERO-REDIRECT: SMOKE TEST SUITE")
        print("=" * 60)
        
        tests = [
            self.test_public_landing_page,
            self.test_protected_page_unauthenticated,
            self.test_login_creates_session,
            self.test_protected_page_authenticated,
            self.test_me_endpoint_authenticated,
            self.test_logout_destroys_session,
            self.test_protected_page_after_logout,
            self.test_health_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 60)
        print(f"📊 RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Zero redirect loops confirmed!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Authentication flow needs attention")
            return False

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auth Loop Smoke Tests')
    parser.add_argument('--url', default=None, 
                       help='Base URL to test (default: auto-detect from config)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    tester = AuthLoopTester(args.url)
    success = tester.run_all_tests()
    
    if args.json:
        print(json.dumps({
            'success': success,
            'results': tester.test_results
        }, indent=2))
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()