#!/usr/bin/env python3
"""
Quick Build Test - Fast validation without timeouts
Tests essential components that must work for deployment
"""

import sys
import os
import traceback
from datetime import datetime

def test_basic_imports():
    """Test that basic Python imports work"""
    print("Testing basic imports...")
    
    try:
        import flask
        import sqlalchemy
        import werkzeug
        print("✅ Core Flask dependencies available")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_app_creation():
    """Test app creation without full initialization"""
    print("Testing app creation...")
    
    try:
        # Import without triggering full initialization
        import sys
        sys.path.append('.')
        
        # Test minimal app creation
        from flask import Flask
        test_app = Flask(__name__)
        test_app.secret_key = "test_key"
        print("✅ Basic Flask app creation works")
        
        # Test our app module exists
        import app
        print("✅ App module imports successfully")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def test_models():
    """Test model imports"""
    print("Testing models...")
    
    try:
        from models.user import User
        print("✅ User model imports")
        
        # Test UserMixin compatibility
        user_instance = User()
        print("✅ User model instantiation works")
        return True
        
    except Exception as e:
        print(f"❌ Models failed: {e}")
        return False

def test_auth_system():
    """Test authentication system"""
    print("Testing auth system...")
    
    try:
        from utils.auth_compat import get_current_user, is_authenticated, login_required
        print("✅ Auth functions import successfully")
        
        # Test that functions exist and are callable
        assert callable(get_current_user)
        assert callable(is_authenticated) 
        assert callable(login_required)
        print("✅ Auth functions are callable")
        return True
        
    except Exception as e:
        print(f"❌ Auth system failed: {e}")
        return False

def test_route_structure():
    """Test route structure"""
    print("Testing route structure...")
    
    try:
        import routes
        print("✅ Routes package imports")
        
        # Test specific route files
        from routes.user_routes import user_bp
        from routes.dashboard import dashboard_bp
        print("✅ Critical route blueprints available")
        return True
        
    except Exception as e:
        print(f"❌ Route structure failed: {e}")
        return False

def test_critical_files_exist():
    """Test that critical files exist"""
    print("Testing critical files...")
    
    critical_files = [
        'app.py',
        'main.py', 
        'models/user.py',
        'utils/auth_compat.py',
        'routes/__init__.py',
        'routes/user_routes.py'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing critical files: {missing_files}")
        return False
    else:
        print("✅ All critical files exist")
        return True

def main():
    """Run quick build test"""
    print("🚀 QUICK BUILD TEST")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    tests = [
        ("Critical Files", test_critical_files_exist),
        ("Basic Imports", test_basic_imports),
        ("App Creation", test_app_creation),
        ("Models", test_models),
        ("Auth System", test_auth_system),
        ("Route Structure", test_route_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 20)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 BUILD SUCCESS - Ready for deployment!")
        return True
    else:
        print("⚠️  BUILD ISSUES - Need fixes before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)