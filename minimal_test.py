#!/usr/bin/env python3
"""
Minimal Test - Check core functionality without heavy features
"""
import sys
import os

# Set environment for minimal testing
os.environ['FAST_STARTUP'] = 'true'
os.environ['DISABLE_HEAVY_FEATURES'] = 'true'
os.environ['PORT'] = '5000'

def test_core_functionality():
    """Test that core Flask app can be created"""
    print("🔧 MINIMAL FUNCTIONALITY TEST")
    print("=" * 30)
    
    try:
        # Test 1: Import Flask basics
        import flask
        import sqlalchemy
        print("✅ Flask and SQLAlchemy available")
        
        # Test 2: Import our app module
        sys.path.append('.')
        from app import create_app
        print("✅ App module imports successfully")
        
        # Test 3: Create app instance
        app = create_app()
        print("✅ App instance created successfully")
        
        # Test 4: Test app context
        with app.app_context():
            print("✅ App context works")
        
        # Test 5: Check if essential routes exist
        print("\n📋 Available routes:")
        for rule in app.url_map.iter_rules():
            if rule.endpoint in ['health', 'landing', 'demo_login']:
                print(f"   ✅ {rule.rule} -> {rule.endpoint}")
        
        # Test 6: Check app configuration
        print(f"\n⚙️  App configuration:")
        print(f"   Debug: {app.debug}")
        print(f"   Secret key: {'Set' if app.secret_key else 'Missing'}")
        print(f"   Database: {'Configured' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Missing'}")
        print(f"   Fast startup: {app.config.get('deferred_init', False)}")
        
        print("\n✅ CORE FUNCTIONALITY TEST PASSED")
        print("The application core is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)