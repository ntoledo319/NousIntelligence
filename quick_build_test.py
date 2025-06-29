#!/usr/bin/env python3
"""
Quick Build Test - Find what's breaking the build
"""
import sys
import os
import signal
import subprocess
import time

def timeout_handler(signum, frame):
    """Handle timeout gracefully"""
    print("❌ BUILD TIMEOUT - App startup taking too long")
    raise TimeoutError("Build process timed out")

def test_build_step_by_step():
    """Test build in isolated steps to find the issue"""
    print("🔍 DIAGNOSING BUILD ISSUE")
    print("=" * 40)
    
    # Step 1: Basic imports
    print("Step 1: Testing basic imports...")
    try:
        import flask
        import sqlalchemy
        print("✅ Flask/SQLAlchemy imports work")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Step 2: App module import
    print("Step 2: Testing app module import...")
    try:
        sys.path.append('.')
        import app
        print("✅ App module imports successfully")
    except Exception as e:
        print(f"❌ App module import failed: {e}")
        return False
    
    # Step 3: Create app function
    print("Step 3: Testing create_app function...")
    try:
        app_instance = app.create_app()
        print("✅ create_app() works")
    except Exception as e:
        print(f"❌ create_app() failed: {e}")
        return False
    
    # Step 4: Test app context
    print("Step 4: Testing app context...")
    try:
        with app_instance.app_context():
            print("✅ App context works")
    except Exception as e:
        print(f"❌ App context failed: {e}")
        return False
    
    # Step 5: Check if app runs (with timeout)
    print("Step 5: Testing app startup (with 10 second timeout)...")
    try:
        # Set up signal handler for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        # Try to create app without running it
        test_app = app.create_app()
        print("✅ App creation without running works")
        
        # Clear timeout
        signal.alarm(0)
        
    except TimeoutError:
        print("❌ App startup times out - there's a blocking operation")
        return False
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        signal.alarm(0)  # Clear timeout
        return False
    
    print("✅ ALL BUILD STEPS PASS - App should work")
    return True

def check_common_issues():
    """Check for common issues that cause build failures"""
    print("\n🔍 CHECKING COMMON ISSUES")
    print("=" * 30)
    
    # Check for missing dependencies
    print("Checking critical dependencies...")
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    try:
        import sqlalchemy
    except ImportError:
        missing_deps.append("sqlalchemy")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        return False
    else:
        print("✅ All critical dependencies available")
    
    # Check for configuration issues
    print("Checking configuration...")
    try:
        from config import AppConfig
        print("✅ Configuration loads successfully")
    except Exception as e:
        print(f"❌ Configuration issue: {e}")
        return False
    
    # Check database configuration
    print("Checking database...")
    try:
        from database import db
        print("✅ Database module loads")
    except Exception as e:
        print(f"❌ Database issue: {e}")
        return False
    
    return True

def main():
    """Run comprehensive build diagnosis"""
    print("🚀 BUILD DIAGNOSTIC TOOL")
    print("=" * 25)
    
    # Check common issues first
    if not check_common_issues():
        print("\n❌ COMMON ISSUES FOUND - Fix these first")
        return False
    
    # Test build step by step
    if not test_build_step_by_step():
        print("\n❌ BUILD STEP FAILURE - Check specific step above")
        return False
    
    print("\n✅ BUILD DIAGNOSIS COMPLETE")
    print("All components work individually. Issue may be in app.run() call.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)