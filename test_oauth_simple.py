#!/usr/bin/env python3
"""
Simple OAuth Configuration Tester
Tests OAuth setup without dependencies
"""

import os
import sys
import json
import re
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print("{}".format(title))
    print("="*60)

def check_env_vars():
    """Check environment variables"""
    print_header("ENVIRONMENT VARIABLES CHECK")
    
    required_vars = {
        'GOOGLE_CLIENT_ID': {
            'pattern': r'\d{10,15}-[a-zA-Z0-9]+\.apps\.googleusercontent\.com',
            'example': '123456789012-abcdef.apps.googleusercontent.com'
        },
        'GOOGLE_CLIENT_SECRET': {
            'pattern': r'GOCSPX-[a-zA-Z0-9_-]+',
            'example': 'GOCSPX-abc123def456'
        },
        'SESSION_SECRET': {
            'min_length': 32,
            'example': 'your-very-long-random-secret-key-here-minimum-32-chars'
        },
        'DATABASE_URL': {
            'pattern': r'(postgresql|sqlite|mysql)',
            'example': 'postgresql://user:pass@localhost/dbname'
        }
    }
    
    issues = []
    
    for var_name, requirements in required_vars.items():
        value = os.environ.get(var_name)
        
        if not value:
            print("\n[FAIL] {} is not set".format(var_name))
            print("   Example: {}".format(requirements.get('example')))
            issues.append("{} not set".format(var_name))
        else:
            # Validate format
            if 'pattern' in requirements:
                if re.match(requirements['pattern'], value):
                    print("\n[PASS] {} is set and valid format".format(var_name))
                else:
                    print("\n[FAIL] {} format may be invalid".format(var_name))
                    print("   Current length: {}".format(len(value)))
                    print("   Expected pattern: {}".format(requirements['example']))
                    issues.append("{} format invalid".format(var_name))
            elif 'min_length' in requirements:
                if len(value) >= requirements['min_length']:
                    print("\n[PASS] {}: Set (length: {})".format(var_name, len(value)))
                else:
                    print("\n[FAIL] {}: Too short (length: {}, min: {})".format(
                        var_name, len(value), requirements['min_length']))
                    issues.append("{} too short".format(var_name))
            else:
                print("\n[PASS] {}: Set".format(var_name))
    
    return issues

def check_oauth_files():
    """Check if OAuth files exist"""
    print_header("OAUTH FILES CHECK")
    
    critical_files = [
        'utils/google_oauth.py',
        'routes/auth_routes.py',
        'models/user.py',
        'templates/auth/login.html'
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print("[PASS] {}".format(file_path))
        else:
            print("[FAIL] {} - Missing!".format(file_path))
            missing_files.append(file_path)
    
    return missing_files

def generate_setup_script():
    """Generate setup script for environment variables"""
    print_header("GENERATING SETUP SCRIPT")
    
    setup_script = '''#!/bin/bash
# OAuth Setup Script for NOUS Intelligence

echo "Setting up OAuth environment variables..."

# Generate secure session secret
export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Set your Google OAuth credentials here
export GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-YOUR_SECRET_HERE"

# Database URL (adjust as needed)
export DATABASE_URL="sqlite:///nous.db"

echo "Environment variables set!"
echo "SESSION_SECRET: ${SESSION_SECRET:0:10}... (truncated)"
echo "GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
echo "GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:10}... (truncated)"
echo "DATABASE_URL: $DATABASE_URL"

# Create .env file
cat > .env << EOF
SESSION_SECRET=$SESSION_SECRET
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
DATABASE_URL=$DATABASE_URL
EOF

echo "Created .env file"
'''
    
    with open('setup_oauth_env.sh', 'w') as f:
        f.write(setup_script)
    os.chmod('setup_oauth_env.sh', 0o755)
    
    print("✅ Created setup_oauth_env.sh")
    print("   Edit the file to add your OAuth credentials, then run:")
    print("   source ./setup_oauth_env.sh")

def generate_test_commands():
    """Generate test commands"""
    print_header("🧪 TEST COMMANDS")
    
    print("1. Test environment variables:")
    print("   python3 -c \"import os; print('CLIENT_ID:', os.getenv('GOOGLE_CLIENT_ID', 'NOT SET'))\"")
    
    print("\n2. Test OAuth service:")
    print("   python3 -c \"from utils.google_oauth import oauth_service; print('Configured:', oauth_service.is_configured())\"")
    
    print("\n3. Run Flask app:")
    print("   python3 app.py")
    
    print("\n4. Test login page:")
    print("   curl -s http://localhost:8080/auth/login | grep -i google")

def main():
    """Run all checks"""
    print("🚀 NOUS Intelligence OAuth Setup Checker")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment variables
    env_issues = check_env_vars()
    
    # Check files
    missing_files = check_oauth_files()
    
    # Generate setup script
    generate_setup_script()
    
    # Show test commands
    generate_test_commands()
    
    # Summary
    print_header("📊 SUMMARY")
    
    total_issues = len(env_issues) + len(missing_files)
    
    if total_issues == 0:
        print("✅ All checks passed! OAuth should be working.")
    else:
        print(f"❌ Found {total_issues} issues that need fixing:")
        
        if env_issues:
            print(f"\n🔧 Environment Issues ({len(env_issues)}):")
            for issue in env_issues:
                print(f"   • {issue}")
                
        if missing_files:
            print(f"\n📁 Missing Files ({len(missing_files)}):")
            for file in missing_files:
                print(f"   • {file}")
    
    print("\n📚 Next Steps:")
    print("1. Fix any issues identified above")
    print("2. Set environment variables using setup_oauth_env.sh")
    print("3. Configure Google Cloud Console with redirect URIs")
    print("4. Test the OAuth flow")

if __name__ == "__main__":
    main() 