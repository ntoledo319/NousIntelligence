#!/usr/bin/env python3
"""
Security Fixes Script
Applies critical security fixes to NOUS application
"""

import os
import re
import shutil
from datetime import datetime

def fix_hardcoded_secret():
    """Fix hardcoded secret in app.py"""
    print("🔧 Fixing hardcoded secret vulnerability...")
    
    # Read current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix the SECRET_KEY configuration
    old_pattern = r"SECRET_KEY = os\.environ\.get\('SESSION_SECRET', '[^']*'\)"
    new_code = """SECRET_KEY = os.environ.get('SESSION_SECRET')
        
        if not SECRET_KEY:
            raise RuntimeError("SESSION_SECRET environment variable is required for security")"""
    
    # Replace the hardcoded secret
    content = re.sub(old_pattern, new_code, content)
    
    # Write back
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed hardcoded secret vulnerability")

def fix_debug_mode():
    """Fix debug mode configuration"""
    print("🔧 Fixing debug mode configuration...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix debug mode
    content = re.sub(
        r"DEBUG = True",
        "DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'",
        content
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed debug mode configuration")

def add_security_headers():
    """Add basic security headers"""
    print("🔧 Adding security headers...")
    
    security_code = '''
# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add basic security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
'''
    
    # Read app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add security headers before the final create_app call
    if 'add_security_headers' not in content:
        # Find a good place to insert (before def create_app or at the end)
        if 'def create_app' in content:
            content = content.replace('def create_app', security_code + '\ndef create_app')
        else:
            content += security_code
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added basic security headers")

def create_env_example():
    """Create env.example with secure defaults"""
    print("🔧 Creating env.example with secure configuration...")
    
    env_example = """# NOUS Application Environment Variables
# Copy this file to .env and set your actual values

# Security (REQUIRED)
SESSION_SECRET=your-32-character-or-longer-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Google OAuth (REQUIRED for authentication)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Application Configuration
FLASK_DEBUG=false
PORT=5000
HOST=0.0.0.0

# Optional: AI Service API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
"""
    
    with open('env.example', 'w') as f:
        f.write(env_example)
    
    print("✅ Created env.example with secure configuration")

def run_final_security_check():
    """Run final security validation"""
    print("🔍 Running final security check...")
    
    issues = []
    
    # Check for remaining hardcoded secrets
    with open('app.py', 'r') as f:
        content = f.read()
        if 'dev-secret-key' in content:
            issues.append("Hardcoded secret still present")
        if 'DEBUG = True' in content:
            issues.append("Debug mode still hardcoded")
        if 'add_security_headers' not in content:
            issues.append("Security headers not added")
    
    # Check environment variables
    if not os.environ.get('SESSION_SECRET'):
        issues.append("SESSION_SECRET not set")
    
    if issues:
        print("⚠️ Remaining security issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ All critical security issues resolved")
        return True

def main():
    """Apply all security fixes"""
    print("🔐 Applying critical security fixes...")
    print("=" * 50)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app_backup_{timestamp}.py"
    shutil.copy2('app.py', backup_file)
    print(f"📄 Created backup: {backup_file}")
    
    try:
        # Apply fixes
        fix_hardcoded_secret()
        fix_debug_mode()
        add_security_headers()
        create_env_example()
        
        # Final check
        success = run_final_security_check()
        
        if success:
            print("\n🎉 Security fixes applied successfully!")
            print("Security improvements:")
            print("  • Removed hardcoded secret fallback")
            print("  • Fixed debug mode configuration")
            print("  • Added basic security headers")
            print("  • Created secure environment template")
            print("\nRecommendations:")
            print("  • Ensure SESSION_SECRET is set in production")
            print("  • Disable debug mode in production (FLASK_DEBUG=false)")
            print("  • Regular security audits")
        else:
            print("\n⚠️ Some security issues remain - manual review needed")
            
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        # Restore backup
        shutil.copy2(backup_file, 'app.py')
        print(f"Restored backup from {backup_file}")

if __name__ == '__main__':
    main()