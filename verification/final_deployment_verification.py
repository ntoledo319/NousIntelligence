#!/usr/bin/env python3
"""
Final Deployment Verification
Comprehensive verification that all remediation work is complete and deployment-ready
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def verify_deployment_readiness():
    """Verify the application is deployment-ready after comprehensive remediation"""
    print("🔍 Running final deployment verification...")
    
    checks_passed = []
    checks_failed = []
    
    # 1. Verify authentication system
    try:
        from utils.unified_auth import init_auth, get_current_user, require_auth
        checks_passed.append("Unified authentication system verified")
    except ImportError as e:
        checks_failed.append(f"Authentication system import failed: {e}")
    
    # 2. Verify no hardcoded secrets
    secret_files = ['app.py', 'config/production.py', 'utils/unified_auth.py']
    hardcoded_secrets = []
    
    for file_path in secret_files:
        if Path(file_path).exists():
            content = Path(file_path).read_text()
            if 'os.environ.get' in content and 'SECRET_KEY' in content:
                continue  # Good - using environment variables
            elif any(word in content.lower() for word in ['secret_key = "', "secret_key = '"]):
                hardcoded_secrets.append(file_path)
    
    if not hardcoded_secrets:
        checks_passed.append("No hardcoded secrets detected")
    else:
        checks_failed.append(f"Hardcoded secrets found in: {hardcoded_secrets}")
    
    # 3. Verify single entry point
    if Path('app.py').exists() and not Path('app_working.py').exists():
        checks_passed.append("Single entry point established (app.py only)")
    else:
        checks_failed.append("Multiple entry points detected")
    
    # 4. Verify security utilities
    security_files = [
        'utils/comprehensive_validation.py',
        'utils/rate_limiting.py',
        'utils/security_headers.py'
    ]
    
    missing_security = [f for f in security_files if not Path(f).exists()]
    if not missing_security:
        checks_passed.append("All security utilities present")
    else:
        checks_failed.append(f"Missing security files: {missing_security}")
    
    # 5. Verify testing framework
    test_files = ['tests/conftest.py', 'tests/test_basic.py']
    missing_tests = [f for f in test_files if not Path(f).exists()]
    if not missing_tests:
        checks_passed.append("Testing framework established")
    else:
        checks_failed.append(f"Missing test files: {missing_tests}")
    
    # 6. Verify application startup
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-c', 
            'from app import create_app; app = create_app(); print("SUCCESS")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'SUCCESS' in result.stdout:
            checks_passed.append("Application startup verified")
        else:
            checks_failed.append(f"Application startup failed: {result.stderr}")
    except Exception as e:
        checks_failed.append(f"Could not verify startup: {e}")
    
    # 7. Verify environment configuration
    required_env_vars = ['DATABASE_URL', 'SESSION_SECRET']
    missing_env_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if not missing_env_vars:
        checks_passed.append("Required environment variables configured")
    else:
        checks_failed.append(f"Missing environment variables: {missing_env_vars}")
    
    # Generate final report
    total_checks = len(checks_passed) + len(checks_failed)
    success_rate = (len(checks_passed) / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n📊 Final Verification Results:")
    print(f"Checks passed: {len(checks_passed)}/{total_checks}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if checks_passed:
        print(f"\n✅ Passed checks:")
        for check in checks_passed:
            print(f"  - {check}")
    
    if checks_failed:
        print(f"\n❌ Failed checks:")
        for check in checks_failed:
            print(f"  - {check}")
    
    # Overall status
    deployment_ready = len(checks_failed) == 0
    status = "DEPLOYMENT READY" if deployment_ready else "ISSUES DETECTED"
    
    print(f"\n🚀 Status: {status}")
    
    if deployment_ready:
        print("The application has passed all verification checks and is ready for production deployment.")
    else:
        print("Some issues were detected. Please address the failed checks before deployment.")
    
    return deployment_ready

if __name__ == '__main__':
    success = verify_deployment_readiness()
    exit(0 if success else 1)