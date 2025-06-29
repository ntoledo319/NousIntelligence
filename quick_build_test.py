#!/usr/bin/env python3
"""
Quick Build Test - Immediate validation without full startup
"""
import sys
import os

def quick_test():
    """Quick test of core functionality"""
    print("🔍 Quick Build Test")
    
    # Test 1: Basic imports
    try:
        import flask
        import database
        import config
        from app import create_app
        print("✅ Core imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: App creation (without full initialization)
    try:
        os.environ['DISABLE_HEAVY_FEATURES'] = 'true'
        app = create_app()
        print("✅ App creation successful")
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    # Test 3: Basic configuration
    try:
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            print("✅ Database configuration found")
        else:
            print("⚠️  Database configuration missing")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    print("🎉 Quick build test passed!")
    return True

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n✅ BUILD STATUS: WORKING")
        print("The application builds successfully and is ready to run.")
    else:
        print("\n❌ BUILD STATUS: FAILED")
        print("Issues need to be resolved before deployment.")
        sys.exit(1)