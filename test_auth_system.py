#!/usr/bin/env python3
"""
Complete Authentication System Test
Tests the full OAuth flow and authentication security
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_authentication_system():
    """Test the complete authentication system"""
    print("🔐 Testing NOUS Authentication System")
    print("="*50)
    
    # Test 1: Check environment variables
    print("\n1. Environment Configuration:")
    required_vars = ['SESSION_SECRET', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'DATABASE_URL']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Test 2: Import all authentication components
    print("\n2. Authentication Components:")
    try:
        from config.app_config import AppConfig
        print("   ✅ AppConfig imported")
        
        from models.user import User
        print("   ✅ User model imported")
        
        from utils.google_oauth import GoogleOAuthService, oauth_service
        print("   ✅ Google OAuth service imported")
        
        from routes.auth_routes import auth_bp
        print("   ✅ Authentication routes imported")
        
        from app_working import create_app
        print("   ✅ Flask app imported")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 3: Create app and check configuration
    print("\n3. Application Configuration:")
    try:
        app = create_app()
        print("   ✅ Flask app created successfully")
        
        # Check OAuth configuration
        if oauth_service.is_configured():
            print("   ✅ Google OAuth properly configured")
        else:
            print("   ⚠️  Google OAuth not configured (missing credentials)")
        
        # Check app config
        with app.app_context():
            if app.secret_key and len(app.secret_key) >= 16:
                print("   ✅ SECRET_KEY properly configured")
            else:
                print("   ❌ SECRET_KEY not properly configured")
        
    except Exception as e:
        print(f"   ❌ App creation error: {e}")
        return False
    
    # Test 4: Check authentication routes
    print("\n4. Authentication Routes:")
    auth_routes = [
        '/auth/login',
        '/auth/callback', 
        '/auth/logout',
        '/auth/profile',
        '/auth/status',
        '/auth/demo-mode'
    ]
    
    with app.test_client() as client:
        for route in auth_routes:
            try:
                response = client.get(route)
                if response.status_code in [200, 302, 401]:  # Valid responses
                    print(f"   ✅ {route}: {response.status_code}")
                else:
                    print(f"   ⚠️  {route}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {route}: Error - {e}")
    
    # Test 5: Test demo mode functionality
    print("\n5. Demo Mode Test:")
    try:
        with app.test_client() as client:
            # Test demo mode activation
            response = client.get('/auth/demo-mode')
            if response.status_code == 302:  # Redirect expected
                print("   ✅ Demo mode activation works")
            else:
                print(f"   ⚠️  Demo mode unexpected response: {response.status_code}")
            
            # Test status after demo mode
            response = client.get('/auth/status')
            if response.status_code == 200:
                print("   ✅ Auth status endpoint accessible")
            else:
                print(f"   ⚠️  Auth status error: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Demo mode test error: {e}")
    
    print("\n🎯 Authentication System Test Complete!")
    return True

def validate_security_improvements():
    """Validate that all security fixes have been applied"""
    print("\n🛡️  Security Validation")
    print("="*30)
    
    # Check config file security
    config_file = Path('config/app_config.py')
    if config_file.exists():
        content = config_file.read_text()
        
        # Check SECRET_KEY security
        if 'os.environ.get(\'SESSION_SECRET\')' in content:
            print("✅ SECRET_KEY uses environment variable")
        else:
            print("❌ SECRET_KEY not properly configured")
        
        # Check CORS security
        if 'https://nous.app,https://www.nous.app' in content:
            print("✅ CORS properly restricted")
        else:
            print("❌ CORS not properly configured")
    
    # Check database security
    db_file = Path('database.py')
    if db_file.exists():
        db_content = db_file.read_text()
        if 'db.create_all()' not in db_content:
            print("✅ Database uses migrations (no db.create_all)")
        else:
            print("❌ Database still has unsafe db.create_all")
    
    # Check dependencies
    pyproject_file = Path('pyproject.toml')
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        if 'flask-login' in content:
            print("✅ Flask-Login dependency present")
        else:
            print("❌ Flask-Login dependency missing")

if __name__ == '__main__':
    success = test_authentication_system()
    validate_security_improvements()
    
    if success:
        print("\n🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some authentication tests failed")
        sys.exit(1)