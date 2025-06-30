#!/usr/bin/env python3
"""
Google Login Security Validation Script
Tests that all critical security issues from the audit report have been resolved
"""

import os
import sys
import json
import importlib
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleLoginSecurityValidator:
    """Validates Google Login security fixes"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'critical_issues_resolved': [],
            'remaining_issues': [],
            'security_score': 0
        }
    
    def run_validation(self):
        """Run all security validation tests"""
        logger.info("🔍 Starting Google Login Security Validation...")
        
        # Test 1: Blueprint naming consistency
        self.test_blueprint_naming()
        
        # Test 2: OAuth configuration security
        self.test_oauth_configuration()
        
        # Test 3: Token storage security
        self.test_token_storage()
        
        # Test 4: Demo mode security
        self.test_demo_mode_security()
        
        # Test 5: Error handling security
        self.test_error_handling()
        
        # Test 6: CSRF protection
        self.test_csrf_protection()
        
        # Test 7: Username collision handling
        self.test_username_collision_handling()
        
        # Calculate security score
        self.calculate_security_score()
        
        # Generate report
        self.generate_report()
        
        return self.results
    
    def test_blueprint_naming(self):
        """Test blueprint naming consistency"""
        try:
            # Check auth routes blueprint name
            from routes.auth_routes import auth_bp
            
            if auth_bp.name == 'auth':
                self.log_success("Blueprint naming consistency", "auth_bp correctly named 'auth'")
            else:
                self.log_failure("Blueprint naming consistency", f"auth_bp has incorrect name: {auth_bp.name}")
                
            # Check app configuration
            self.check_login_view_configuration()
            
        except Exception as e:
            self.log_failure("Blueprint naming consistency", f"Import error: {str(e)}")
    
    def check_login_view_configuration(self):
        """Check Flask-Login configuration"""
        try:
            # Check if app_working.py has correct login_view
            with open('app_working.py', 'r') as f:
                content = f.read()
                
            if "login_view = 'auth.login'" in content:
                self.log_success("Login view configuration", "Flask-Login correctly configured with 'auth.login'")
            elif "login_view = 'google_auth.login'" in content:
                self.log_failure("Login view configuration", "Flask-Login still using old 'google_auth.login'")
            else:
                self.log_failure("Login view configuration", "Login view configuration not found")
                
        except Exception as e:
            self.log_failure("Login view configuration", f"File read error: {str(e)}")
    
    def test_oauth_configuration(self):
        """Test OAuth configuration security"""
        try:
            from utils.google_oauth import GoogleOAuthService
            
            # Check if refresh token support is configured
            service = GoogleOAuthService()
            
            if hasattr(service, 'refresh_token'):
                self.log_success("OAuth refresh token", "Refresh token method implemented")
            else:
                self.log_failure("OAuth refresh token", "Refresh token method missing")
                
            # Check OAuth configuration method
            if hasattr(service, 'is_configured'):
                self.log_success("OAuth configuration check", "Configuration validation method exists")
            else:
                self.log_failure("OAuth configuration check", "Configuration validation missing")
                
        except Exception as e:
            self.log_failure("OAuth configuration", f"Import/test error: {str(e)}")
    
    def test_token_storage(self):
        """Test secure token storage"""
        try:
            from models.user import User
            
            # Check if User model has OAuth token fields
            user = User()
            
            required_fields = ['google_access_token', 'google_refresh_token', 'google_token_expires_at']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(user, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_success("Token storage", "All OAuth token fields present in User model")
            else:
                self.log_failure("Token storage", f"Missing fields: {missing_fields}")
                
        except Exception as e:
            self.log_failure("Token storage", f"Model test error: {str(e)}")
    
    def test_demo_mode_security(self):
        """Test demo mode security restrictions"""
        try:
            # Check demo mode route configuration
            with open('routes/auth_routes.py', 'r') as f:
                content = f.read()
            
            # Check if demo mode is POST only
            if "@auth_bp.route('/demo-mode', methods=['POST'])" in content:
                self.log_success("Demo mode security", "Demo mode restricted to POST method")
            else:
                self.log_failure("Demo mode security", "Demo mode not restricted to POST method")
            
            # Check for environment variable protection
            if "os.environ.get('ENABLE_DEMO_MODE')" in content:
                self.log_success("Demo mode environment check", "Demo mode requires environment variable")
            else:
                self.log_failure("Demo mode environment check", "Demo mode lacks environment protection")
                
        except Exception as e:
            self.log_failure("Demo mode security", f"File check error: {str(e)}")
    
    def test_error_handling(self):
        """Test secure error handling"""
        try:
            # Check auth routes for secure error handling
            with open('routes/auth_routes.py', 'r') as f:
                content = f.read()
            
            # Check for secure error messages
            if "Authentication failed. Please try again." in content:
                self.log_success("Error handling security", "Generic error messages implemented")
            else:
                self.log_failure("Error handling security", "Detailed error messages may leak information")
            
            # Check for secure logging
            if "logger.error(" in content and "str(e)" not in content:
                self.log_success("Secure logging", "Error logging doesn't expose sensitive data")
            else:
                self.log_warning("Secure logging", "Review error logging for sensitive data exposure")
                
        except Exception as e:
            self.log_failure("Error handling", f"File check error: {str(e)}")
    
    def test_csrf_protection(self):
        """Test CSRF protection on logout"""
        try:
            # Check logout route configuration
            with open('routes/auth_routes.py', 'r') as f:
                content = f.read()
            
            if "@auth_bp.route('/logout', methods=['POST'])" in content:
                self.log_success("CSRF protection", "Logout restricted to POST method (CSRF protected)")
            else:
                self.log_failure("CSRF protection", "Logout vulnerable to CSRF attacks")
                
        except Exception as e:
            self.log_failure("CSRF protection", f"File check error: {str(e)}")
    
    def test_username_collision_handling(self):
        """Test username collision handling"""
        try:
            from utils.google_oauth import oauth_service
            
            if hasattr(oauth_service, '_generate_unique_username'):
                self.log_success("Username collision handling", "Unique username generation implemented")
            else:
                self.log_failure("Username collision handling", "Username collision handling missing")
                
        except Exception as e:
            self.log_failure("Username collision handling", f"Test error: {str(e)}")
    
    def log_success(self, test_name, description):
        """Log a successful test"""
        self.results['tests_passed'] += 1
        self.results['critical_issues_resolved'].append({
            'test': test_name,
            'status': 'RESOLVED',
            'description': description
        })
        logger.info(f"✅ {test_name}: {description}")
    
    def log_failure(self, test_name, description):
        """Log a failed test"""
        self.results['tests_failed'] += 1
        self.results['remaining_issues'].append({
            'test': test_name,
            'status': 'FAILED',
            'description': description,
            'severity': 'HIGH'
        })
        logger.error(f"❌ {test_name}: {description}")
    
    def log_warning(self, test_name, description):
        """Log a warning"""
        self.results['remaining_issues'].append({
            'test': test_name,
            'status': 'WARNING',
            'description': description,
            'severity': 'MEDIUM'
        })
        logger.warning(f"⚠️ {test_name}: {description}")
    
    def calculate_security_score(self):
        """Calculate overall security score"""
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        if total_tests > 0:
            self.results['security_score'] = round((self.results['tests_passed'] / total_tests) * 100, 1)
        else:
            self.results['security_score'] = 0
    
    def generate_report(self):
        """Generate final validation report"""
        logger.info("\n" + "="*60)
        logger.info("🔒 GOOGLE LOGIN SECURITY VALIDATION REPORT")
        logger.info("="*60)
        
        logger.info(f"Tests Passed: {self.results['tests_passed']}")
        logger.info(f"Tests Failed: {self.results['tests_failed']}")
        logger.info(f"Security Score: {self.results['security_score']}%")
        
        if self.results['security_score'] >= 90:
            logger.info("🟢 SECURITY STATUS: EXCELLENT")
        elif self.results['security_score'] >= 75:
            logger.info("🟡 SECURITY STATUS: GOOD")
        else:
            logger.info("🔴 SECURITY STATUS: NEEDS IMPROVEMENT")
        
        logger.info("\n📋 Critical Issues Resolved:")
        for issue in self.results['critical_issues_resolved']:
            logger.info(f"  ✅ {issue['test']}: {issue['description']}")
        
        if self.results['remaining_issues']:
            logger.info("\n⚠️ Remaining Issues:")
            for issue in self.results['remaining_issues']:
                logger.info(f"  {issue['status']}: {issue['test']} - {issue['description']}")
        
        logger.info("="*60)
        
        # Save results to file
        with open('tests/google_login_security_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info("📄 Detailed results saved to: tests/google_login_security_results.json")

def main():
    """Main validation function"""
    validator = GoogleLoginSecurityValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results['tests_failed'] == 0:
        logger.info("🎉 All security tests passed!")
        sys.exit(0)
    else:
        logger.error(f"❌ {results['tests_failed']} security tests failed")
        sys.exit(1)

if __name__ == '__main__':
    main()