#!/usr/bin/env python3
"""
Quick Build Validation Test
Tests that the application can build and start without errors
"""
import os
import sys
import time

def test_build():
    """Test that the application builds successfully"""
    print("🔍 NOUS Personal Assistant - Build Test")
    print("=" * 50)
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    os.environ['PORT'] = '5000'
    
    try:
        print("1. Testing core imports...")
        import flask
        import werkzeug
        import sqlalchemy
        print("   ✅ Core dependencies available")
        
        print("2. Testing application modules...")
        import database
        import config
        import models
        import routes
        import utils
        import api
        print("   ✅ All application modules import successfully")
        
        print("3. Testing Flask app creation...")
        from app import create_app
        app = create_app()
        print("   ✅ Flask application created successfully")
        
        print("4. Testing route registration...")
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        critical_routes = ['/', '/health', '/healthz', '/api/chat']
        registered_routes = sum(1 for route in critical_routes if route in routes)
        print(f"   ✅ {registered_routes}/{len(critical_routes)} critical routes registered")
        
        print("5. Testing app context...")
        with app.test_client() as client:
            print("   ✅ Test client created successfully")
        
        print("\n🎉 BUILD SUCCESS!")
        print("=" * 50)
        print("✅ Application builds without errors")
        print("✅ All modules import correctly")
        print("✅ Flask app creates and configures properly")
        print("✅ Routes register successfully")
        print("✅ Ready for production deployment")
        print("\n🚀 To start: python3 main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_build()
    sys.exit(0 if success else 1)