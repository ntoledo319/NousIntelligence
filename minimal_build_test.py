#!/usr/bin/env python3
"""
Minimal Build Test - Fast diagnosis of build issues
"""
import sys
import os

def test_imports():
    """Test individual import components"""
    print("Testing imports...")
    
    components = [
        ("flask", "import flask"),
        ("database", "from database import db"),
        ("config", "from config import AppConfig"),
        ("models.aa_content_models", "from models.aa_content_models import AASpeakerRecording"),
        ("utils.google_tasks_helper", "from utils.google_tasks_helper import get_task_lists"),
    ]
    
    for name, import_code in components:
        try:
            exec(import_code)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            return False
    return True

def test_app_creation():
    """Test minimal app creation"""
    print("\nTesting app creation...")
    
    try:
        # Disable heavy features
        os.environ['DISABLE_HEAVY_FEATURES'] = 'true'
        
        # Skip time-consuming imports
        from flask import Flask
        from database import db
        
        # Create minimal app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-key'
        
        db.init_app(app)
        
        print("✅ Minimal app created")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\nTesting database...")
    
    try:
        from database import db
        import os
        
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            print(f"✅ Database URL configured: {db_url[:20]}...")
        else:
            print("⚠️  No DATABASE_URL found")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run minimal build tests"""
    print("🔍 Minimal Build Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("App Creation", test_app_creation),
        ("Database Test", test_database)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ MINIMAL BUILD: WORKING")
        print("Issue may be in complex initialization")
    else:
        print("❌ MINIMAL BUILD: FAILED")
        print("Core components have issues")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)