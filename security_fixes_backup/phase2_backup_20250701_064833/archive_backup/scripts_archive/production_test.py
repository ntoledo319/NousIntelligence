#!/usr/bin/env python3
"""
Production Deployment Test
Validates that NOUS is ready for full production deployment
"""
import os
import sys
import json
import subprocess
import time
from pathlib import Path

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing environment configuration...")
    
    required_vars = ['DATABASE_URL', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

def test_imports():
    """Test critical imports"""
    print("📦 Testing critical imports...")
    
    try:
        from app import create_app
        from config.app_config import AppConfig
        from database import db
        print("✅ All critical imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("🚀 Testing Flask app creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test database connection
            from database import db
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()
            if result == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        
        print("✅ Flask app creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_production_config():
    """Test production configuration"""
    print("⚙️ Testing production configuration...")
    
    # Check replit.toml
    if not Path('replit.toml').exists():
        print("❌ replit.toml missing")
        return False
    
    # Check main.py
    if not Path('main.py').exists():
        print("❌ main.py missing")
        return False
    
    print("✅ Production configuration files present")
    return True

def main():
    """Run complete production test suite"""
    print("🎯 NOUS Production Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Critical Imports", test_imports),
        ("Flask App Creation", test_app_creation),
        ("Production Config", test_production_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        if test_func():
            passed += 1
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 PRODUCTION DEPLOYMENT READY!")
        print("\n🚀 Next Steps:")
        print("1. Click 'Deploy' button in Replit")
        print("2. Choose 'CloudRun' as deployment target")
        print("3. Monitor deployment logs")
        print("4. Test deployed app at provided URL")
        return 0
    else:
        print("❌ Production deployment not ready")
        print("Please fix the failing tests before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())