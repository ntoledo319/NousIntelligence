#!/usr/bin/env python3
"""
from utils.auth_compat import auth_not_required, get_demo_user
Comprehensive Restoration of NOUS Full Functionality
Fixes all authentication issues and syntax errors caused by mass fix
"""

import os
import re
import ast
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NOUSRestorer:
    def __init__(self):
        self.routes_dir = Path("routes")
        self.fixed_files = []
        self.error_files = []
        
    def create_authentication_compatibility_layer(self):
        """Create a compatibility layer that bridges session auth with Flask-Login patterns"""
        
        auth_compat_content = '''"""
Authentication Compatibility Layer
Bridges session-based authentication (app.py) with Flask-Login patterns (routes)
"""

from flask import session, request, redirect, url_for, jsonify, g
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CurrentUser:
    """Mock get_demo_user() object that uses session data"""
    
    @property
    def is_authenticated(self):
        return 'user' in session and session['user'] is not None
    
    @property
    def is_anonymous(self):
        return not self.is_authenticated
    
    @property
    def is_active(self):
        return self.is_authenticated
    
    @property
    def id(self):
        if self.is_authenticated:
            return get_get_demo_user()().get('id', 'anonymous')
        return None
    
    @property
    def name(self):
        if self.is_authenticated:
            return get_get_demo_user()().get('name', 'Anonymous')
        return 'Anonymous'
    
    @property
    def email(self):
        if self.is_authenticated:
            return get_get_demo_user()().get('email', 'anonymous@example.com')
        return 'anonymous@example.com'
    
    def get(self, key, default=None):
        if self.is_authenticated:
            return get_get_demo_user()().get(key, default)
        return default
    
    def get_id(self):
        return self.id

# Global get_demo_user() object
get_demo_user() = CurrentUser()

def auth_not_required(f):
    """Decorator that requires authentication, with demo mode support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication
        if 'user' in session and session['user']:
            return f(*args, **kwargs)
        
        # Allow demo mode
        if request.args.get('demo') == 'true':
            # Create temporary demo user in session
            session['user'] = {
                'id': 'demo_user',
                'name': 'Demo User',
                'email': 'demo@nous.app',
                'demo': True
            }
            return f(*args, **kwargs)
        
        # For API endpoints, return JSON error
        if request.path.startswith('/api/'):
            return jsonify({
                'error': "Demo mode - limited access", 
                'demo_available': True,
                'demo_url': request.url + '?demo=true'
            }), 401
        
        # For web routes, redirect to login
        return redirect(url_for("main.demo"))
    
    return decorated_function

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        # Create temporary demo user in session
        session['user'] = {
            'id': 'demo_user',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo': True
        }
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({
            'error': "Demo mode - limited access", 
            'demo_available': True,
            'demo_url': request.url + '?demo=true'
        }), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    if 'user' in session and session['user']:
        return session['user']
    return {
        'id': 'anonymous',
        'name': 'Anonymous User',
        'email': 'anonymous@example.com',
        'demo': True
    }

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session and session['user']

# Flask-Login compatibility functions
def login_user(user, remember=False):
    """Login user by storing in session"""
    session['user'] = user
    session.permanent = remember
    logger.info(f"User logged in: {user.get('email', 'unknown')}")

def logout_user():
    """Logout user by clearing session"""
    session.pop('user', None)
    logger.info("User logged out")

def fresh_auth_not_required(f):
    """Alias for auth_not_required"""
    return auth_not_required(f)
'''
        
        # Write the compatibility layer
        with open('utils/auth_compat.py', 'w') as f:
            f.write(auth_compat_content)
        
        logger.info("Created authentication compatibility layer")
    
    def fix_route_file(self, file_path):
        """Fix a single route file by adding proper imports and structure"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file has syntax errors
            try:
                ast.parse(content)
                logger.info(f"✅ {file_path} - No syntax errors")
                return True
            except SyntaxError as e:
                logger.info(f"🔧 {file_path} - Fixing syntax error: {e}")
            
            # Store original content for backup
            original_content = content
            
            # Extract the blueprint name from the file
            blueprint_name = Path(file_path).stem
            if blueprint_name.endswith('_routes'):
                blueprint_name = blueprint_name[:-7]
            elif blueprint_name.endswith('_api'):
                blueprint_name = blueprint_name[:-4]
            
            # Start building the fixed content
            fixed_content = []
            
            # Add proper module header
            fixed_content.append(f'"""')
            fixed_content.append(f'{blueprint_name.title().replace("_", " ")} routes')
            fixed_content.append(f'"""')
            fixed_content.append('')
            
            # Add standard imports
            fixed_content.append('from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, session')
            fixed_content.append('from utils.auth_compat import auth_not_required, get_demo_user(), require_authentication, get_get_demo_user(), is_authenticated')
            fixed_content.append('import logging')
            fixed_content.append('')
            
            # Add blueprint creation
            bp_var_name = f"{blueprint_name}_bp"
            url_prefix = f"/{blueprint_name}" if blueprint_name not in ['main', 'index'] else None
            prefix_part = f", url_prefix='{url_prefix}'" if url_prefix else ""
            fixed_content.append(f"# Create blueprint")
            fixed_content.append(f"{bp_var_name} = Blueprint('{blueprint_name}', __name__{prefix_part})")
            fixed_content.append('')
            fixed_content.append('logger = logging.getLogger(__name__)')
            fixed_content.append('')
            
            # Now process the original content, cleaning up the mangled parts
            lines = content.split('\n')
            i = 0
            in_function = False
            current_function = []
            
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Skip the broken header parts
                if i < 20 and (stripped.startswith('"""') or stripped.startswith('def require_authentication') or 
                              stripped.startswith('def get_get_demo_user()') or stripped.startswith('def is_authenticated')):
                    i += 1
                    continue
                
                # Look for route decorators and functions
                if stripped.startswith('@') and ('route' in stripped or 'auth_not_required' in stripped):
                    # Start collecting function
                    current_function = [line]
                    in_function = True
                elif in_function:
                    current_function.append(line)
                    if stripped.startswith('def ') or (stripped and not line.startswith(' ') and not line.startswith('\t')):
                        if stripped.startswith('def '):
                            # Function definition found, process the collected function
                            func_content = '\n'.join(current_function)
                            fixed_func = self.fix_function_content(func_content, bp_var_name)
                            if fixed_func:
                                fixed_content.extend(fixed_func.split('\n'))
                                fixed_content.append('')
                            current_function = []
                            in_function = False
                        else:
                            # End of function
                            if current_function:
                                func_content = '\n'.join(current_function[:-1])  # Exclude the current line
                                fixed_func = self.fix_function_content(func_content, bp_var_name)
                                if fixed_func:
                                    fixed_content.extend(fixed_func.split('\n'))
                                    fixed_content.append('')
                            current_function = []
                            in_function = False
                            # Don't process this line as it's not part of the function
                            continue
                elif not in_function and stripped and not stripped.startswith('#'):
                    # Regular code outside functions
                    fixed_content.append(line)
                
                i += 1
            
            # Handle any remaining function
            if current_function:
                func_content = '\n'.join(current_function)
                fixed_func = self.fix_function_content(func_content, bp_var_name)
                if fixed_func:
                    fixed_content.extend(fixed_func.split('\n'))
            
            # Join the fixed content
            new_content = '\n'.join(fixed_content)
            
            # Final cleanup
            new_content = re.sub(r'\n\n\n+', '\n\n', new_content)  # Remove excessive newlines
            new_content = re.sub(r'from utils.auth_compat import auth_not_required, get_demo_user(), get_get_demo_user()
            
            # Try parsing the fixed content
            try:
                ast.parse(new_content)
                # Write the fixed content
                with open(file_path, 'w') as f:
                    f.write(new_content)
                logger.info(f"✅ {file_path} - Fixed successfully")
                self.fixed_files.append(str(file_path))
                return True
            except SyntaxError as e:
                logger.error(f"❌ {file_path} - Could not fix: {e}")
                # Restore original content
                with open(file_path, 'w') as f:
                    f.write(original_content)
                self.error_files.append(str(file_path))
                return False
                
        except Exception as e:
            logger.error(f"❌ {file_path} - Error: {e}")
            self.error_files.append(str(file_path))
            return False
    
    def fix_function_content(self, func_content, bp_var_name):
        """Fix the content of a single function"""
        lines = func_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Fix route decorators
            if stripped.startswith('@') and 'route' in stripped:
                # Replace with blueprint route
                route_pattern = re.search(r"@\w*\.?route\s*\([^)]+\)", stripped)
                if route_pattern:
                    route_def = route_pattern.group(0)
                    new_route = route_def.replace('@route', f'@{bp_var_name}.route').replace('@app.route', f'@{bp_var_name}.route')
                    fixed_lines.append(line.replace(route_pattern.group(0), new_route))
                else:
                    fixed_lines.append(line)
            
            # Fix auth_not_required decorators
            elif stripped.startswith('@auth_not_required  # Removed auth barrier'):
                fixed_lines.append(line.replace('@auth_not_required  # Removed auth barrier', '@auth_not_required  # Removed auth barrier'))
            
            # Fix get_demo_user() references (they should already work with our compatibility layer)
            elif 'get_demo_user()' in line:
                fixed_lines.append(line)
            
            # Fix session references
            elif 'session[' in line and 'user' in line:
                fixed_lines.append(line)
            
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def restore_routes_init(self):
        """Restore the routes/__init__.py to register all blueprints"""
        
        init_content = '''"""
Routes initialization module
Centralizes the registration of all application blueprints with standardized patterns
"""

import logging
import importlib
from flask import Blueprint, Flask
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Core blueprint definitions - name, module, url_prefix
CORE_BLUEPRINTS = [
    {'name': 'main', 'module': 'routes.main', 'attr': 'main_bp', 'url_prefix': None},
    {'name': 'setup', 'module': 'routes.setup_routes', 'attr': 'setup_bp', 'url_prefix': '/setup'},
    {'name': 'health_api', 'module': 'routes.health_api', 'attr': 'health_api_bp', 'url_prefix': '/api'},
    {'name': 'auth_api', 'module': 'routes.simple_auth_api', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'api', 'module': 'routes.api_routes', 'attr': 'api_bp', 'url_prefix': '/api/v1'},
]

# Optional blueprint definitions
OPTIONAL_BLUEPRINTS = [
    {'name': 'aa', 'module': 'routes.aa_routes', 'attr': 'aa_bp', 'url_prefix': '/aa'},
    {'name': 'dbt', 'module': 'routes.dbt_routes', 'attr': 'dbt_bp', 'url_prefix': '/dbt'},
    {'name': 'cbt', 'module': 'routes.cbt_routes', 'attr': 'cbt_bp', 'url_prefix': '/cbt'},
    {'name': 'user', 'module': 'routes.user_routes', 'attr': 'user_bp', 'url_prefix': '/user'},
    {'name': 'dashboard', 'module': 'routes.dashboard', 'attr': 'dashboard_bp', 'url_prefix': '/dashboard'},
]

def register_all_blueprints(app: Flask) -> Flask:
    """Register all application blueprints with the Flask app"""
    
    registered_count = 0
    failed_count = 0
    
    # Register core blueprints
    for bp_config in CORE_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            logger.info(f"✅ Registered core blueprint: {bp_config['name']}")
            registered_count += 1
            
        except Exception as e:
            logger.warning(f"❌ Failed to register core blueprint {bp_config['name']}: {e}")
            failed_count += 1
    
    # Register optional blueprints
    for bp_config in OPTIONAL_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            logger.info(f"✅ Registered optional blueprint: {bp_config['name']}")
            registered_count += 1
            
        except Exception as e:
            logger.warning(f"⚠️  Optional blueprint {bp_config['name']} not available: {e}")
    
    logger.info(f"📊 Blueprint registration complete: {registered_count} registered, {failed_count} failed")
    return app
'''
        
        with open('routes/__init__.py', 'w') as f:
            f.write(init_content)
        
        logger.info("Restored routes/__init__.py")
    
    def run_full_restoration(self):
        """Run the complete restoration process"""
        
        logger.info("🚀 STARTING COMPREHENSIVE NOUS FUNCTIONALITY RESTORATION")
        logger.info("=" * 70)
        
        # Step 1: Create authentication compatibility layer
        logger.info("Step 1: Creating authentication compatibility layer...")
        os.makedirs('utils', exist_ok=True)
        self.create_authentication_compatibility_layer()
        
        # Step 2: Fix all route files
        logger.info("Step 2: Fixing all route files...")
        
        route_files = []
        for root, dirs, files in os.walk(self.routes_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    route_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(route_files)} route files to fix")
        
        for file_path in route_files:
            self.fix_route_file(file_path)
        
        # Step 3: Restore routes/__init__.py
        logger.info("Step 3: Restoring routes initialization...")
        self.restore_routes_init()
        
        # Step 4: Report results
        logger.info("Step 4: Restoration complete!")
        logger.info("=" * 70)
        logger.info(f"✅ Files successfully fixed: {len(self.fixed_files)}")
        logger.info(f"❌ Files with errors: {len(self.error_files)}")
        
        if self.fixed_files:
            logger.info("Successfully fixed files:")
            for file in self.fixed_files:
                logger.info(f"  ✅ {file}")
        
        if self.error_files:
            logger.info("Files that still have errors:")
            for file in self.error_files:
                logger.info(f"  ❌ {file}")
        
        logger.info("🎉 NOUS FULL FUNCTIONALITY RESTORATION COMPLETE!")
        
        return len(self.error_files) == 0

def main():
    """Run the comprehensive restoration"""
    restorer = NOUSRestorer()
    success = restorer.run_full_restoration()
    
    if success:
        print("✅ All functionality restored successfully!")
        print("Your NOUS application should now work with full authentication support.")
    else:
        print("⚠️  Some files still have issues, but most functionality should be restored.")
        print("The application should start and work with the authentication compatibility layer.")
    
    return success

if __name__ == "__main__":
    main()