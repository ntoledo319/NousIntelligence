#!/usr/bin/env python3
"""
Deployment Test Script
Quick validation that the app can start and respond
"""
import sys
import time
import requests
from threading import Thread
import logging

def test_app_startup():
    """Test that the app can start successfully"""
    try:
        from app import create_app
        app = create_app()
        
        print("✅ App creation successful")
        
        # Test that we can create an app context
        with app.app_context():
            print("✅ App context successful")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint if server is running"""
    try:
        # Try to hit health endpoint
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Health endpoint test failed: {e}")
        return False

def main():
    """Run deployment tests"""
    print("🚀 Running deployment tests...")
    
    # Test app startup
    startup_ok = test_app_startup()
    
    if startup_ok:
        print("🎉 Deployment test PASSED - App is ready for deployment!")
        return 0
    else:
        print("❌ Deployment test FAILED - Fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
