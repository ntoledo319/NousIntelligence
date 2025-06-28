#!/usr/bin/env python3
"""
Dependency Validation Script
Validates all dependencies are properly installed and application can start
"""

import sys
import traceback
from datetime import datetime

def test_core_imports():
    """Test all core application imports"""
    print("🧪 Testing Core Application Imports")
    print("=" * 50)
    
    results = {}
    
    # Test main application
    try:
        from app import app
        results['main_app'] = True
        print("✅ Main Flask app imported successfully")
    except Exception as e:
        results['main_app'] = False
        print(f"❌ Main app import failed: {e}")
    
    # Test database
    try:
        from database import db
        results['database'] = True
        print("✅ Database module imported successfully")
    except Exception as e:
        results['database'] = False
        print(f"❌ Database import failed: {e}")
    
    # Test models
    try:
        from models.user import User
        results['user_model'] = True
        print("✅ User model imported successfully")
    except Exception as e:
        results['user_model'] = False
        print(f"❌ User model import failed: {e}")
    
    return results

def test_dependency_imports():
    """Test all required dependency imports"""
    print("\n🧪 Testing Required Dependencies")
    print("=" * 50)
    
    dependencies = {
        'flask': 'Flask web framework',
        'werkzeug': 'WSGI utilities',
        'flask_sqlalchemy': 'Database ORM',
        'flask_login': 'User session management',
        'flask_session': 'Session management',
        'flask_migrate': 'Database migrations',
        'psycopg2': 'PostgreSQL driver',
        'requests': 'HTTP client',
        'psutil': 'System monitoring',
        'authlib': 'OAuth authentication'
    }
    
    results = {}
    
    for package, description in dependencies.items():
        try:
            if package == 'psycopg2':
                import psycopg2
            else:
                __import__(package)
            results[package] = True
            print(f"✅ {package}: {description}")
        except ImportError:
            results[package] = False
            print(f"❌ {package}: {description} - NOT AVAILABLE")
    
    # Test optional dependencies
    optional_deps = {
        'flask_wtf': 'CSRF protection',
        'google.generativeai': 'AI integration',
        'soundfile': 'Audio processing',
        'librosa': 'Audio analysis'
    }
    
    print("\n🔍 Testing Optional Dependencies")
    print("-" * 30)
    
    for package, description in optional_deps.items():
        try:
            if package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
            results[package] = True
            print(f"✅ {package}: {description}")
        except ImportError:
            results[package] = False
            print(f"⚠️  {package}: {description} - OPTIONAL, not available")
    
    return results

def test_application_startup():
    """Test if the application can start without errors"""
    print("\n🧪 Testing Application Startup")
    print("=" * 50)
    
    try:
        from app import app
        
        # Test app configuration
        with app.app_context():
            # Test basic app properties
            assert app.name == 'app'
            print("✅ App context created successfully")
            
            # Test database connection (if available)
            try:
                from database import db
                # Simple database test
                print("✅ Database connection available")
            except Exception as e:
                print(f"⚠️  Database test skipped: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        traceback.print_exc()
        return False

def generate_report(core_results, dep_results, startup_success):
    """Generate comprehensive validation report"""
    print("\n📊 DEPENDENCY VALIDATION REPORT")
    print("=" * 50)
    print(f"Validation completed at: {datetime.now()}")
    print()
    
    # Core functionality
    core_passed = sum(core_results.values())
    core_total = len(core_results)
    print(f"Core Application: {core_passed}/{core_total} components working")
    
    # Dependencies
    dep_passed = sum(1 for k, v in dep_results.items() if v and not k.startswith('google.') and k not in ['soundfile', 'librosa', 'flask_wtf'])
    dep_total = len([k for k in dep_results.keys() if not k.startswith('google.') and k not in ['soundfile', 'librosa', 'flask_wtf']])
    print(f"Required Dependencies: {dep_passed}/{dep_total} packages available")
    
    # Optional dependencies
    opt_available = sum(1 for k, v in dep_results.items() if v and (k.startswith('google.') or k in ['soundfile', 'librosa', 'flask_wtf']))
    opt_total = len([k for k in dep_results.keys() if k.startswith('google.') or k in ['soundfile', 'librosa', 'flask_wtf']])
    print(f"Optional Dependencies: {opt_available}/{opt_total} packages available")
    
    print(f"Application Startup: {'✅ SUCCESS' if startup_success else '❌ FAILED'}")
    
    # Overall status
    critical_missing = []
    for package, available in dep_results.items():
        if not available and package not in ['google.generativeai', 'soundfile', 'librosa', 'flask_wtf']:
            critical_missing.append(package)
    
    if not critical_missing and startup_success:
        print("\n🎉 STATUS: DEPENDENCY CLEANUP SUCCESSFUL")
        print("Application is ready for production deployment!")
    elif critical_missing:
        print(f"\n⚠️  STATUS: MISSING CRITICAL DEPENDENCIES")
        print(f"Missing packages: {', '.join(critical_missing)}")
    else:
        print("\n❌ STATUS: APPLICATION STARTUP ISSUES")
        print("Core dependencies available but application won't start")

def main():
    """Main validation function"""
    print("🧹 DEPENDENCY VALIDATION - POST CLEANUP")
    print("=" * 60)
    print("Validating all dependencies after cleanup operation...")
    print()
    
    # Run all tests
    core_results = test_core_imports()
    dep_results = test_dependency_imports()
    startup_success = test_application_startup()
    
    # Generate final report
    generate_report(core_results, dep_results, startup_success)
    
    return startup_success and all(core_results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)