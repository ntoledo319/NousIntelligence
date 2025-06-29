#!/usr/bin/env python3
"""
Deployment validation for OPERATION PUBLIC-OR-BUST
Quick check that deployment will work
"""
import os
import sys

def validate_deployment():
    """Validate deployment readiness"""
    print("🔍 VALIDATING DEPLOYMENT READINESS")
    
    checks = []
    
    # Check 1: Required files exist
    required_files = ['main.py', 'app.py', 'replit.toml']
    for file in required_files:
        if os.path.exists(file):
            checks.append(f"✅ {file} exists")
        else:
            checks.append(f"❌ {file} missing")
            
    # Check 2: Environment variables
    env_vars = ['PORT', 'HOST']
    for var in env_vars:
        if os.environ.get(var):
            checks.append(f"✅ {var} set")
        else:
            checks.append(f"⚠️ {var} using default")
            
    # Check 3: Public access configuration
    if os.path.exists('replit.toml'):
        with open('replit.toml', 'r') as f:
            content = f.read()
            if 'pageEnabled = false' in content:
                checks.append("✅ Replit auth disabled")
            else:
                checks.append("❌ Replit auth may be enabled")
    
    # Check 4: Try basic app import
    try:
        from app import create_app
        checks.append("✅ App imports successfully")
    except Exception as e:
        checks.append(f"❌ App import failed: {e}")
        
    print("\n".join(checks))
    
    failed_checks = len([c for c in checks if c.startswith("❌")])
    if failed_checks == 0:
        print("\n🎉 DEPLOYMENT READY!")
        return True
    else:
        print(f"\n⚠️ {failed_checks} issues found")
        return False

if __name__ == "__main__":
    success = validate_deployment()
    sys.exit(0 if success else 1)
