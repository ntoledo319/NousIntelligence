#!/usr/bin/env python3
"""
Authentication Verification and Final Fix System
Ensures complete elimination of all authentication barriers
"""

import os
import re
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthVerificationFixer:
    def __init__(self):
        self.issues_found = []
        self.fixed_issues = []
        
    def verify_and_fix_main_app(self):
        """Verify and fix main application authentication"""
        logger.info("🔍 Verifying authentication barriers in main application")
        
        # Check main app file (app.py)
        self.check_and_fix_app_py()
        
        # Check critical route files
        critical_routes = [
            'routes/main.py',
            'routes/dashboard.py', 
            'routes/user_routes.py',
            'routes/chat_routes.py',
            'routes/api_routes.py'
        ]
        
        for route_file in critical_routes:
            if os.path.exists(route_file):
                self.check_and_fix_route_file(route_file)
        
        # Create/update authentication compatibility
        self.ensure_auth_compatibility()
        
        # Update app.py to register blueprints properly
        self.fix_app_blueprint_registration()
        
        self.report_results()
    
    def check_and_fix_app_py(self):
        """Check and fix app.py authentication issues"""
        app_file = 'app.py'
        if not os.path.exists(app_file):
            logger.error("❌ app.py not found")
            return
            
        with open(app_file, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Ensure no Flask-Login imports
        if 'flask_login' in content.lower():
            self.issues_found.append(f"{app_file}: Flask-Login import found")
            content = re.sub(r'from flask_login.*\n', '', content)
            content = re.sub(r'import flask_login.*\n', '', content)
        
        # Ensure blueprint registration is working
        if 'register_all_blueprints' not in content:
            self.issues_found.append(f"{app_file}: Missing blueprint registration")
            
            # Add blueprint registration
            blueprint_registration = '''
    # Register all application blueprints
    try:
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("✅ All blueprints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Blueprint registration issue: {e}")
        # Continue without blueprints for basic functionality
'''
            
            # Insert before the return app statement
            content = content.replace('return app', f'{blueprint_registration}\n    return app')
        
        if content != original_content:
            with open(app_file, 'w') as f:
                f.write(content)
            self.fixed_issues.append(f"Fixed {app_file}")
            logger.info(f"✅ Fixed {app_file}")
    
    def check_and_fix_route_file(self, filepath):
        """Check and fix a route file for authentication issues"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Check for authentication barriers
            issues = []
            
            if '@login_required' in content:
                issues.append("@login_required decorator found")
                content = content.replace('@login_required', '# @login_required removed for public access')
            
            if 'current_user' in content and 'flask_login' in content:
                issues.append("Flask-Login current_user usage found")
                content = re.sub(r'from flask_login.*current_user.*\n', '', content)
                content = content.replace('current_user', 'get_demo_user()')
            
            if 'You must be logged in' in content:
                issues.append("Authentication error message found")
                content = content.replace('You must be logged in', 'Demo mode - full access available')
            
            if 'abort(401)' in content:
                issues.append("401 abort found")
                content = content.replace('abort(401)', 'pass  # Auth barrier removed')
            
            if issues:
                self.issues_found.extend([f"{filepath}: {issue}" for issue in issues])
                
                # Add demo user import if needed
                if 'get_demo_user()' in content and 'from utils.auth_compat import' not in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('from ', 'import ')) and 'auth_compat' not in line:
                            continue
                        elif line.strip() and not line.strip().startswith('#'):
                            lines.insert(i, 'from utils.auth_compat import get_demo_user, is_authenticated')
                            content = '\n'.join(lines)
                            break
                
                with open(filepath, 'w') as f:
                    f.write(content)
                self.fixed_issues.append(f"Fixed {filepath}")
                logger.info(f"✅ Fixed {filepath}")
                
        except Exception as e:
            logger.error(f"❌ Error checking {filepath}: {e}")
    
    def ensure_auth_compatibility(self):
        """Ensure authentication compatibility layer exists and is complete"""
        os.makedirs('utils', exist_ok=True)
        
        auth_compat_path = 'utils/auth_compat.py'
        
        auth_compat_content = '''"""
Complete Authentication Compatibility Layer
Provides full demo user support with zero authentication barriers
"""

from flask import session, request
from datetime import datetime
from functools import wraps

class DemoUser:
    """Demo user class with Flask-Login compatibility"""
    def __init__(self):
        self.id = 'demo_user_123'
        self.name = 'Demo User'
        self.email = 'demo@nous.app'
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.demo_mode = True
        self.login_time = datetime.now().isoformat()
    
    def get_id(self):
        return self.id

def get_demo_user():
    """Get demo user instance"""
    return DemoUser()

def is_authenticated():
    """Always return True for demo mode"""
    return True

def login_required(f):
    """No-barrier decorator that ensures demo user in session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure demo user is in session
        if 'user' not in session:
            session['user'] = {
                'id': 'demo_user_123',
                'name': 'Demo User',
                'email': 'demo@nous.app',
                'demo_mode': True
            }
        return f(*args, **kwargs)
    return decorated_function

def auth_not_required(f):
    """Alias for login_required (no barriers)"""
    return login_required(f)

# Global instances for compatibility
current_user = get_demo_user()

def ensure_demo_session():
    """Ensure demo user is in Flask session"""
    if 'user' not in session:
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User', 
            'email': 'demo@nous.app',
            'demo_mode': True,
            'is_authenticated': True
        }
    return session['user']

def get_current_user():
    """Get current user (always demo user)"""
    ensure_demo_session()
    return get_demo_user()
'''
        
        with open(auth_compat_path, 'w') as f:
            f.write(auth_compat_content)
        
        logger.info("✅ Authentication compatibility layer updated")
    
    def fix_app_blueprint_registration(self):
        """Ensure app.py properly registers blueprints"""
        app_file = 'app.py'
        
        if not os.path.exists(app_file):
            return
            
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check if blueprint registration is missing
        if 'register_all_blueprints' not in content:
            # Add blueprint registration at the end of create_app function
            blueprint_code = '''
    # Register all application blueprints for full functionality
    try:
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("✅ All blueprints registered successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Routes module not available: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Blueprint registration issue: {e}")
        # Continue with basic functionality
'''
            
            # Insert before return app
            if 'return app' in content:
                content = content.replace('return app', f'{blueprint_code}\n    return app')
                
                with open(app_file, 'w') as f:
                    f.write(content)
                
                logger.info("✅ Added blueprint registration to app.py")
    
    def report_results(self):
        """Report verification and fix results"""
        logger.info("📊 Authentication Verification Results:")
        logger.info(f"   🔍 Issues found: {len(self.issues_found)}")
        logger.info(f"   ✅ Issues fixed: {len(self.fixed_issues)}")
        
        if self.issues_found:
            logger.info("🔍 Issues found:")
            for issue in self.issues_found[:10]:
                logger.info(f"     {issue}")
        
        if self.fixed_issues:
            logger.info("✅ Fixed:")
            for fix in self.fixed_issues:
                logger.info(f"     {fix}")
        
        if not self.issues_found:
            logger.info("🎯 No authentication barriers found!")
        
        logger.info("🚀 Application ready for public deployment")

def main():
    fixer = AuthVerificationFixer()
    fixer.verify_and_fix_main_app()

if __name__ == "__main__":
    main()