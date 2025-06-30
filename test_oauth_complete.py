#!/usr/bin/env python3
"""
Complete OAuth System Test
Tests all authentication components and identifies remaining issues
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add the current directory to the path to import from our project
sys.path.insert(0, '.')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OAuthSystemTester:
    def __init__(self):
        self.test_results = []
        self.issues_found = []
        
    def log_test(self, test_name, passed, details=None):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if not passed:
            self.issues_found.append({
                'issue': test_name,
                'details': details
            })
    
    def test_environment_variables(self):
        """Test OAuth environment variables"""
        logger.info("=== Testing Environment Variables ===")
        
        # Test GOOGLE_CLIENT_ID
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        if client_id:
            if 'apps.googleusercontent.com' in client_id:
                self.log_test("GOOGLE_CLIENT_ID format", True, f"Valid format: {client_id[:50]}...")
            else:
                self.log_test("GOOGLE_CLIENT_ID format", False, f"Invalid format: {client_id[:50]}...")
        else:
            self.log_test("GOOGLE_CLIENT_ID existence", False, "Environment variable not set")
        
        # Test GOOGLE_CLIENT_SECRET
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        if client_secret:
            if client_secret.startswith('GOCSPX-'):
                self.log_test("GOOGLE_CLIENT_SECRET format", True, "Valid GOCSPX format")
            else:
                self.log_test("GOOGLE_CLIENT_SECRET format", False, f"Invalid format: {client_secret[:20]}...")
        else:
            self.log_test("GOOGLE_CLIENT_SECRET existence", False, "Environment variable not set")
        
        # Test SESSION_SECRET
        session_secret = os.environ.get('SESSION_SECRET')
        if session_secret and len(session_secret) >= 16:
            self.log_test("SESSION_SECRET", True, f"Valid length: {len(session_secret)} chars")
        else:
            self.log_test("SESSION_SECRET", False, f"Invalid or missing: {len(session_secret) if session_secret else 0} chars")
    
    def test_oauth_service_import(self):
        """Test OAuth service import and initialization"""
        logger.info("=== Testing OAuth Service Import ===")
        
        try:
            from utils.google_oauth import oauth_service, GoogleOAuthService
            self.log_test("OAuth service import", True, "Successfully imported oauth_service")
            
            # Test if oauth_service is initialized
            if oauth_service:
                self.log_test("OAuth service initialization", True, "oauth_service instance exists")
                
                # Test credential extraction
                if hasattr(oauth_service, '_extract_client_id'):
                    self.log_test("OAuth credential extraction methods", True, "Extraction methods available")
                else:
                    self.log_test("OAuth credential extraction methods", False, "Methods missing")
                
                # Test configuration check
                try:
                    is_configured = oauth_service.is_configured()
                    self.log_test("OAuth configuration check", True, f"Configuration status: {is_configured}")
                except Exception as e:
                    self.log_test("OAuth configuration check", False, f"Error: {str(e)}")
                    
            else:
                self.log_test("OAuth service initialization", False, "oauth_service is None")
                
        except Exception as e:
            self.log_test("OAuth service import", False, f"Import error: {str(e)}")
    
    def test_auth_routes(self):
        """Test authentication routes import"""
        logger.info("=== Testing Auth Routes ===")
        
        try:
            from routes.auth_routes import auth_bp
            self.log_test("Auth routes import", True, "Successfully imported auth_bp")
            
            # Check routes
            routes = []
            for rule in auth_bp.url_map.iter_rules():
                routes.append(f"{rule.rule} ({', '.join(rule.methods)})")
            
            self.log_test("Auth routes registration", True, f"Found {len(routes)} routes")
            logger.info(f"   Routes: {routes}")
            
        except Exception as e:
            self.log_test("Auth routes import", False, f"Import error: {str(e)}")
    
    def test_user_model(self):
        """Test User model"""
        logger.info("=== Testing User Model ===")
        
        try:
            from models.user import User
            self.log_test("User model import", True, "Successfully imported User model")
            
            # Check if User has required OAuth fields
            required_fields = ['google_id', 'google_access_token', 'google_refresh_token', 'google_token_expires_at']
            missing_fields = []
            
            for field in required_fields:
                if hasattr(User, field):
                    logger.info(f"   ✅ {field}: Found")
                else:
                    missing_fields.append(field)
                    logger.info(f"   ❌ {field}: Missing")
            
            if missing_fields:
                self.log_test("User model OAuth fields", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("User model OAuth fields", True, "All OAuth fields present")
                
        except Exception as e:
            self.log_test("User model import", False, f"Import error: {str(e)}")
    
    def test_app_initialization(self):
        """Test app initialization with OAuth"""
        logger.info("=== Testing App Initialization ===")
        
        try:
            from app import create_app
            app = create_app()
            self.log_test("App creation", True, "App created successfully")
            
            # Test OAuth configuration in app
            oauth_enabled = app.config.get('OAUTH_ENABLED', False)
            self.log_test("OAuth enabled in app", oauth_enabled, f"OAUTH_ENABLED: {oauth_enabled}")
            
            # Test if Flask-Login is configured
            if hasattr(app, 'login_manager'):
                self.log_test("Flask-Login configuration", True, "LoginManager found")
            else:
                self.log_test("Flask-Login configuration", False, "LoginManager not found")
                
        except Exception as e:
            self.log_test("App initialization", False, f"Error: {str(e)}")
    
    def test_credential_extraction(self):
        """Test credential extraction from malformed environment variables"""
        logger.info("=== Testing Credential Extraction ===")
        
        try:
            from utils.google_oauth import oauth_service
            
            # Test client ID extraction
            raw_client_id = os.environ.get('GOOGLE_CLIENT_ID')
            if raw_client_id:
                extracted_id = oauth_service._extract_client_id(raw_client_id)
                if extracted_id and 'apps.googleusercontent.com' in extracted_id:
                    self.log_test("Client ID extraction", True, f"Extracted: {extracted_id}")
                else:
                    self.log_test("Client ID extraction", False, f"Failed to extract from: {raw_client_id[:50]}...")
            
            # Test client secret extraction
            raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            if raw_client_secret:
                extracted_secret = oauth_service._extract_client_secret(raw_client_secret)
                if extracted_secret and extracted_secret.startswith('GOCSPX-'):
                    self.log_test("Client secret extraction", True, f"Extracted: {extracted_secret[:20]}...")
                else:
                    self.log_test("Client secret extraction", False, f"Failed to extract from: {raw_client_secret[:50]}...")
                    
        except Exception as e:
            self.log_test("Credential extraction", False, f"Error: {str(e)}")
    
    def test_oauth_endpoints(self):
        """Test OAuth endpoints accessibility"""
        logger.info("=== Testing OAuth Endpoints ===")
        
        try:
            import requests
            base_url = "http://localhost:8080"
            
            # Test auth status endpoint
            try:
                response = requests.get(f"{base_url}/auth/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Auth status endpoint", True, f"Status: {response.status_code}")
                    logger.info(f"   Response: {json.dumps(data, indent=2)}")
                else:
                    self.log_test("Auth status endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Auth status endpoint", False, f"Connection error: {str(e)}")
            
            # Test Google login endpoint
            try:
                response = requests.get(f"{base_url}/auth/google", timeout=5, allow_redirects=False)
                # Should redirect to Google or return error
                if response.status_code in [302, 400, 500]:
                    self.log_test("Google login endpoint", True, f"Status: {response.status_code}")
                else:
                    self.log_test("Google login endpoint", False, f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test("Google login endpoint", False, f"Connection error: {str(e)}")
                
        except ImportError:
            self.log_test("OAuth endpoints", False, "requests library not available")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("=== OAUTH SYSTEM TEST REPORT ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.issues_found:
            logger.info("\n=== CRITICAL ISSUES FOUND ===")
            for i, issue in enumerate(self.issues_found, 1):
                logger.info(f"{i}. {issue['issue']}")
                if issue['details']:
                    logger.info(f"   Details: {issue['details']}")
        
        # Save detailed report
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'test_results': self.test_results,
            'issues_found': self.issues_found
        }
        
        with open('oauth_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: oauth_test_report.json")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all OAuth system tests"""
        logger.info("Starting comprehensive OAuth system test...")
        
        self.test_environment_variables()
        self.test_oauth_service_import()
        self.test_auth_routes()
        self.test_user_model()
        self.test_app_initialization()
        self.test_credential_extraction()
        self.test_oauth_endpoints()
        
        return self.generate_report()

def main():
    """Run OAuth system tests"""
    tester = OAuthSystemTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("🎉 All OAuth tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ OAuth system has issues that need to be addressed")
        sys.exit(1)

if __name__ == "__main__":
    main()