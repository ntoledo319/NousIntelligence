#!/usr/bin/env python3
"""
Package Structure Validation Script
Tests that setuptools package discovery issues are resolved
"""

import os
import sys
from pathlib import Path

def test_package_discovery():
    """Test that package discovery works correctly"""
    print("🔍 Testing package discovery...")
    
    try:
        from setuptools import setup, find_packages
        
        # Test the exact configuration from pyproject.toml
        packages = find_packages(
            include=[
                "models*", 
                "routes*", 
                "utils*", 
                "config*", 
                "api*", 
                "services*", 
                "handlers*", 
                "core*", 
                "voice_interface*"
            ],
            exclude=[
                "backup*", 
                "logs*", 
                "uploads*", 
                "instance*", 
                "flask_session*", 
                "static*", 
                "templates*",
                "tests*",
                "scripts*",
                "docs*",
                "build_assets*",
                "project_files*",
                "__pycache__*",
                "*.tests*",
                "*.egg-info*"
            ]
        )
        
        print(f"✅ Package discovery successful")
        print(f"📦 Found {len(packages)} packages: {packages}")
        
        if len(packages) <= 15:  # Should be much less than the problematic 17
            print("✅ Package count within acceptable limits")
            return True
        else:
            print(f"❌ Too many packages found: {len(packages)}")
            return False
            
    except Exception as e:
        print(f"❌ Package discovery failed: {e}")
        return False

def test_import_structure():
    """Test that core imports still work"""
    print("\n🔍 Testing core imports...")
    
    try:
        # Test critical imports
        import app
        print("✅ app.py imports successfully")
        
        import database  
        print("✅ database.py imports successfully")
        
        # Test main packages
        import models
        print("✅ models package imports successfully")
        
        import routes
        print("✅ routes package imports successfully")
        
        import utils
        print("✅ utils package imports successfully")
        
        import config
        print("✅ config package imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_build_files():
    """Test that build configuration files exist"""
    print("\n🔍 Testing build configuration files...")
    
    files_to_check = [
        "pyproject.toml",
        "MANIFEST.in", 
        "setup.py"
    ]
    
    all_exist = True
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all package structure tests"""
    print("🚀 NOUS Package Structure Validation")
    print("=" * 50)
    
    tests = [
        ("Package Discovery", test_package_discovery),
        ("Import Structure", test_import_structure), 
        ("Build Files", test_build_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All package structure fixes applied successfully!")
        print("🚀 Deployment should now work without setuptools errors")
        return True
    else:
        print("\n⚠️  Some issues remain - check the failed tests above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)