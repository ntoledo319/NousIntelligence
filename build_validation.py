#!/usr/bin/env python3
"""
Build Validation Script - Quick test to ensure build works
"""
import sys
import os
import traceback
from pathlib import Path

def test_critical_imports():
    """Test that critical imports work"""
    print("🔍 Testing critical imports...")
    
    try:
        # Test basic Flask imports
        import flask
        print("✅ Flask imports successfully")
        
        # Test database imports
        from database import db, init_database
        print("✅ Database module imports successfully")
        
        # Test config imports
        from config import AppConfig
        print("✅ Config module imports successfully")
        
        # Test if app can be created
        from app import create_app
        app = create_app()
        print("✅ App creates successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that essential files exist"""
    print("\n🔍 Testing file structure...")
    
    essential_files = [
        "main.py",
        "app.py", 
        "database.py",
        "pyproject.toml",
        "replit.toml"
    ]
    
    all_exist = True
    for file in essential_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
            
    return all_exist

def test_database_connection():
    """Test database connectivity"""
    print("\n🔍 Testing database connection...")
    
    try:
        from database import db, init_database
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Try to initialize database
            init_database(app)
            print("✅ Database initialization successful")
            
            # Try a simple query
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database query successful")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_app_startup():
    """Test that app can start (without actually running)"""
    print("\n🔍 Testing app startup...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Test basic app configuration
        if app.config.get('SECRET_KEY'):
            print("✅ Secret key configured")
        else:
            print("⚠️  Secret key not configured")
            
        # Test routes are registered
        if len(app.url_map._rules) > 0:
            print(f"✅ {len(app.url_map._rules)} routes registered")
        else:
            print("❌ No routes registered")
            
        return True
        
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all build validation tests"""
    print("🚀 Starting Build Validation...")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Critical Imports", test_critical_imports),
        ("Database Connection", test_database_connection),
        ("App Startup", test_app_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 BUILD VALIDATION RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 BUILD VALIDATION SUCCESSFUL - Application is ready!")
        return True
    else:
        print("⚠️  BUILD VALIDATION FAILED - Issues need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)