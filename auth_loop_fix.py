#!/usr/bin/env python3
"""
REPO SHERLOCK + AUTH EXORCIST - Emergency Fix Script

This script implements the complete auth loop elimination checklist.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Phase 1: Environment Variables Audit
print("🔍 PHASE 1: ENVIRONMENT VARIABLES INVENTORY")
required_vars = {
    'SESSION_SECRET': os.environ.get('SESSION_SECRET'),
    'DATABASE_URL': os.environ.get('DATABASE_URL'),
    'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
    'PORT': os.environ.get('PORT', '5000'),
}

missing_vars = []
for var, value in required_vars.items():
    if value:
        print(f"✓ {var}: {'*' * min(len(str(value)), 20)}")
    else:
        print(f"❌ {var}: MISSING")
        missing_vars.append(var)

# Optional OAuth vars
oauth_vars = {
    'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET'),
}

for var, value in oauth_vars.items():
    if value:
        print(f"✓ {var}: {'*' * min(len(str(value)), 20)}")
    else:
        print(f"⚠️  {var}: Not set (OAuth disabled)")

# Phase 2: Authentication Guards Audit
print("\n🔍 PHASE 2: AUTHENTICATION GUARDS AUDIT")
auth_files = []
for py_file in Path('.').rglob('*.py'):
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if any(guard in content for guard in ['login_required', '@login_required', 'requireLogin', 'ensureAuth', 'withAuth']):
                auth_files.append(str(py_file))
    except Exception:
        continue

print(f"Found {len(auth_files)} files with authentication guards:")
for file in auth_files[:10]:  # Show first 10
    print(f"  - {file}")

# Phase 3: Cookie/Session Configuration
print("\n🔍 PHASE 3: COOKIE/SESSION CONFIGURATION AUDIT")
config_files = list(Path('.').glob('*config*')) + list(Path('.').glob('*settings*'))
print(f"Found {len(config_files)} configuration files:")
for file in config_files:
    if file.is_file():
        print(f"  - {file}")

print("\n✅ AUDIT COMPLETE - Ready for fixes")