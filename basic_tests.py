#!/usr/bin/env python3
"""
Simple test suite for basic functionality
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that main modules can be imported"""
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False
    
    try:
        import config
        print("✅ config.py imports successfully")
    except Exception as e:
        print(f"❌ config.py import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test that the app can be created"""
    try:
        # Try to import and create app
        from minimal_public_app import create_app
        app = create_app()
        print("✅ App creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_config():
    """Test database configuration"""
    try:
        import database
        print("✅ Database module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running basic functionality tests...")
    
    tests = [
        test_imports,
        test_app_creation,
        test_database_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    main()
