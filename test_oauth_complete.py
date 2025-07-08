#!/usr/bin/env python3
"""
Complete OAuth Testing Framework
Tests every aspect of the OAuth implementation
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OAuthTester:
    """Comprehensive OAuth testing"""
    
    def __init__(self):
        self.results = {
            'environment': {},
            'oauth_service': {},
            'database': {},
            'routes': {},
            'templates': {}
        }
        
    def test_all(self):
        """Run all tests"""
        print("\n🧪 NOUS Intelligence OAuth Testing Framework")
        print("=" * 60)
        
        # Test 1: Environment
        self.test_environment()
        
        # Test 2: OAuth Service
        self.test_oauth_service()
        
        # Test 3: Database
        self.test_database()
        
        # Test 4: Routes
        self.test_routes()
        
        # Test 5: Templates
        self.test_templates()
        
        # Generate report
        self.generate_report()
        
    def test_environment(self):
        """Test environment variables"""
        print("\n1️⃣ Testing Environment Variables...")
        
        vars_to_check = {
            'GOOGLE_CLIENT_ID': lambda x: x and '.apps.googleusercontent.com' in x,
            'GOOGLE_CLIENT_SECRET': lambda x: x and (x.startswith('GOCSPX-') or len(x) > 20),
            'SESSION_SECRET': lambda x: x and len(x) >= 32,
            'DATABASE_URL': lambda x: x and ('sqlite' in x or 'postgresql' in x)
        }
        
        for var_name, validator in vars_to_check.items():
            value = os.environ.get(var_name)
            if value and validator(value):
                self.results['environment'][var_name] = 'PASS'
                print(f"   ✅ {var_name}: Valid")
            else:
                self.results['environment'][var_name] = 'FAIL'
                print(f"   ❌ {var_name}: Invalid or not set")
                
    def test_oauth_service(self):
        """Test OAuth service initialization"""
        print("\n2️⃣ Testing OAuth Service...")
        
        try:
            from utils.google_oauth import oauth_service
            
            # Test configuration
            if oauth_service.is_configured():
                self.results['oauth_service']['configured'] = 'PASS'
                print("   ✅ OAuth service is configured")
            else:
                self.results['oauth_service']['configured'] = 'FAIL'
                print("   ❌ OAuth service is not configured")
                
            # Test OAuth client
            if hasattr(oauth_service, 'google') and oauth_service.google:
                self.results['oauth_service']['client'] = 'PASS'
                print("   ✅ OAuth client initialized")
            else:
                self.results['oauth_service']['client'] = 'FAIL'
                print("   ❌ OAuth client not initialized")
                
        except Exception as e:
            self.results['oauth_service']['error'] = str(e)
            print(f"   ❌ Failed to load OAuth service: {e}")
            
    def test_database(self):
        """Test database and User model"""
        print("\n3️⃣ Testing Database...")
        
        try:
            from models.user import User
            from database import db
            from app import app
            
            with app.app_context():
                # Check User model fields
                required_fields = ['email', 'google_id', 'google_access_token', 'google_refresh_token']
                user_fields = [col.name for col in User.__table__.columns]
                
                for field in required_fields:
                    if field in user_fields:
                        self.results['database'][f'user_{field}'] = 'PASS'
                        print(f"   ✅ User.{field} exists")
                    else:
                        self.results['database'][f'user_{field}'] = 'FAIL'
                        print(f"   ❌ User.{field} missing")
                        
        except Exception as e:
            self.results['database']['error'] = str(e)
            print(f"   ❌ Database test failed: {e}")
            
    def test_routes(self):
        """Test OAuth routes"""
        print("\n4️⃣ Testing OAuth Routes...")
        
        try:
            from app import app
            
            with app.test_client() as client:
                # Test login page
                response = client.get('/auth/login')
                if response.status_code == 200:
                    self.results['routes']['login_page'] = 'PASS'
                    print("   ✅ Login page accessible")
                else:
                    self.results['routes']['login_page'] = 'FAIL'
                    print(f"   ❌ Login page returned {response.status_code}")
                    
                # Test OAuth initiation
                response = client.get('/auth/google', follow_redirects=False)
                if response.status_code in [302, 303]:
                    self.results['routes']['oauth_init'] = 'PASS'
                    print("   ✅ OAuth initiation redirects")
                    
                    # Check redirect location
                    if 'accounts.google.com' in response.location:
                        print("   ✅ Redirects to Google")
                    else:
                        print(f"   ⚠️  Unexpected redirect: {response.location}")
                else:
                    self.results['routes']['oauth_init'] = 'FAIL'
                    print(f"   ❌ OAuth initiation returned {response.status_code}")
                    
        except Exception as e:
            self.results['routes']['error'] = str(e)
            print(f"   ❌ Route testing failed: {e}")
            
    def test_templates(self):
        """Test template rendering"""
        print("\n5️⃣ Testing Templates...")
        
        try:
            from app import app
            
            with app.test_client() as client:
                response = client.get('/auth/login')
                if b'Sign in with Google' in response.data or b'google' in response.data.lower():
                    self.results['templates']['google_button'] = 'PASS'
                    print("   ✅ Google login button found in template")
                else:
                    self.results['templates']['google_button'] = 'FAIL'
                    print("   ❌ Google login button not found in template")
                    
        except Exception as e:
            self.results['templates']['error'] = str(e)
            print(f"   ❌ Template testing failed: {e}")
            
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            print(f"\n{category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result == 'PASS':
                    passed_tests += 1
                    print(f"  ✅ {test_name}")
                else:
                    print(f"  ❌ {test_name}: {result}")
                    
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! OAuth should be working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please fix the issues above.")
            
        # Provide specific recommendations
        self.provide_recommendations()
        
    def provide_recommendations(self):
        """Provide specific recommendations based on test results"""
        print("\n📝 RECOMMENDATIONS:")
        
        # Check environment
        if any(r == 'FAIL' for r in self.results['environment'].values()):
            print("\n1. Set missing environment variables:")
            print("   export GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'")
            print("   export GOOGLE_CLIENT_SECRET='GOCSPX-your-secret'")
            print("   export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')")
            print("   export DATABASE_URL='sqlite:///nous.db'")
            
        # Check OAuth service
        if self.results.get('oauth_service', {}).get('configured') == 'FAIL':
            print("\n2. OAuth service not configured:")
            print("   - Check that environment variables are set")
            print("   - Restart the application after setting variables")
            print("   - Check logs for initialization errors")
            
        # Check database
        if any('FAIL' in str(r) for r in self.results.get('database', {}).values()):
            print("\n3. Database issues detected:")
            print("   - Run database migrations")
            print("   - Initialize database: python3 -c \"from app import app, db; app.app_context().push(); db.create_all()\"")
            
        # Check routes
        if self.results.get('routes', {}).get('oauth_init') == 'FAIL':
            print("\n4. OAuth routes not working:")
            print("   - Ensure Flask app is running")
            print("   - Check for route registration errors")
            print("   - Verify auth blueprint is registered")

def main():
    """Run OAuth tests"""
    tester = OAuthTester()
    tester.test_all()
    
    # Create quick test script
    print("\n" + "=" * 60)
    print("🚀 QUICK TEST SCRIPT")
    print("=" * 60)
    print("\nSave and run this script for quick OAuth testing:")
    print("""
#!/bin/bash
# quick_oauth_test.sh

echo "=== OAuth Quick Test ==="
echo "1. Environment Check:"
env | grep -E "GOOGLE|SESSION|DATABASE" | sed 's/=.*$/=***/'

echo -e "\\n2. OAuth Service Check:"
python3 -c "from utils.google_oauth import oauth_service; print('Configured:', oauth_service.is_configured())"

echo -e "\\n3. Start App:"
echo "Run: python3 app.py"
echo "Then visit: http://localhost:8080/auth/login"
    """)

if __name__ == "__main__":
    main()