#!/usr/bin/env python3
"""
Quick Deployment Check - Fast validation for deployment readiness
"""
import sys
import os
from pathlib import Path

def quick_check():
    """Run a quick deployment readiness check"""
    print("🚀 QUICK DEPLOYMENT CHECK")
    print("=" * 40)
    
    issues = []
    
    # Check 1: Required files
    required_files = ['main.py', 'app.py', 'replit.toml', 'pyproject.toml']
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"Missing required file: {file}")
    
    # Check 2: App can import
    try:
        from app import create_app
        print("✅ App import successful")
    except Exception as e:
        issues.append(f"App import failed: {e}")
    
    # Check 3: App can be created
    try:
        app = create_app()
        print("✅ App creation successful")
    except Exception as e:
        issues.append(f"App creation failed: {e}")
    
    # Check 4: Main.py is executable
    main_py = Path('main.py')
    if main_py.exists():
        content = main_py.read_text()
        if '__name__ == "__main__"' in content:
            print("✅ main.py is executable")
        else:
            issues.append("main.py missing executable section")
    
    # Check 5: replit.toml has proper configuration
    replit_toml = Path('replit.toml')
    if replit_toml.exists():
        content = replit_toml.read_text()
        if 'python3' in content and 'main.py' in content:
            print("✅ replit.toml properly configured")
        else:
            issues.append("replit.toml missing key configurations")
    
    print("=" * 40)
    
    if issues:
        print("❌ DEPLOYMENT NOT READY")
        print("Issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ DEPLOYMENT READY!")
        print("Your app is ready for deployment")
        return True

if __name__ == "__main__":
    success = quick_check()
    sys.exit(0 if success else 1)