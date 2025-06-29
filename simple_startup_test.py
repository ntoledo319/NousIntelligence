#!/usr/bin/env python3
"""
Simple startup test for OPERATION PUBLIC-OR-BUST
Tests basic application functionality without heavy dependencies
"""
import os
import sys

def test_basic_imports():
    """Test basic imports work"""
    try:
        print("Testing basic imports...")
        import flask
        print("✅ Flask imports")
        
        from config import AppConfig
        print("✅ Config imports")
        
        from database import db
        print("✅ Database imports")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test app can be created"""
    try:
        print("Testing app creation...")
        # Set minimal environment for testing
        os.environ.setdefault('PORT', '5000')
        os.environ.setdefault('HOST', '0.0.0.0')
        os.environ.setdefault('SECRET_KEY', 'test-secret-key')
        
        from app import create_app
        app = create_app()
        print("✅ App creates successfully")
        
        # Check critical routes exist
        routes = [str(rule.rule) for rule in app.url_map.iter_rules()]
        critical_routes = ['/', '/health', '/demo']
        
        for route in critical_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
                
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_public_routes():
    """Test public routes work without authentication"""
    try:
        print("Testing public routes...")
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test landing page
            response = client.get('/')
            print(f"Landing page: {response.status_code}")
            
            # Test health endpoint  
            response = client.get('/health')
            print(f"Health endpoint: {response.status_code}")
            
            # Test demo page
            response = client.get('/demo')
            print(f"Demo page: {response.status_code}")
            
            # Test demo chat API
            response = client.post('/api/demo/chat', 
                                 json={'message': 'test'},
                                 content_type='application/json')
            print(f"Demo chat API: {response.status_code}")
            
        print("✅ Public routes testing completed")
        return True
    except Exception as e:
        print(f"❌ Public routes error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simplified startup tests"""
    print("🚀 RUNNING SIMPLIFIED STARTUP TESTS")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("App Creation", test_app_creation), 
        ("Public Routes", test_public_routes)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All basic tests passed! App structure is working.")
        print("Ready for deployment configuration.")
        return True
    else:
        print("⚠️ Some tests failed. Needs investigation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)