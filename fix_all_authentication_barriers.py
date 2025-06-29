#!/usr/bin/env python3
"""
Mass Authentication Barrier Fix
Systematically removes Flask-Login dependencies from all route files
"""

import os
import re
from pathlib import Path

class AuthenticationFixer:
    def __init__(self):
        self.files_processed = 0
        self.changes_made = 0
        
    def fix_file(self, file_path):
        """Fix authentication barriers in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Remove Flask-Login imports
            content = re.sub(r'from flask_login import[^\n]*', '', content)
            content = re.sub(r'import flask_login[^\n]*', '', content)
            
            # 2. Remove @login_required decorators
            content = re.sub(r'@login_required\s*\n', '', content)
            
            # 3. Replace current_user.id with session user id
            content = re.sub(r'current_user\.id', "session.get('user', {}).get('id', 'demo_user')", content)
            content = re.sub(r'current_user\.is_authenticated', "('user' in session and session['user'])", content)
            content = re.sub(r'current_user\.', "session.get('user', {}).get('", content)
            content = re.sub(r'current_user', "session.get('user')", content)
            
            # 4. Add session-based authentication helper at the top of each file
            auth_helper = '''
def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None
'''
            
            # Add helper functions after imports
            if 'def require_authentication():' not in content:
                # Find the end of imports
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if (line.strip().startswith('from ') or 
                        line.strip().startswith('import ') or
                        line.strip().startswith('#') or
                        line.strip() == '' or
                        line.strip().startswith('"""') or
                        line.strip().startswith("'''")):
                        import_end = i
                    else:
                        break
                
                lines.insert(import_end + 1, auth_helper)
                content = '\n'.join(lines)
            
            # 5. Add authentication checks to route functions
            def add_auth_check(match):
                func_def = match.group(0)
                func_name = match.group(1)
                
                # Skip if already has auth check
                if 'require_authentication()' in func_def:
                    return func_def
                
                # Add auth check after function definition
                auth_check = '''
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
'''
                
                # Insert after the function definition line
                lines = func_def.split('\n')
                if len(lines) > 1:
                    lines.insert(1, auth_check)
                    return '\n'.join(lines)
                
                return func_def
            
            # Add auth checks to route functions (but skip helper functions)
            content = re.sub(
                r'(@\w+\.route\([^)]+\)[^\n]*\ndef\s+(\w+)\([^)]*\):[^}]*?)(?=\n\s*@|\n\s*def|\nclass|\n$|\Z)',
                add_auth_check,
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # 6. Clean up multiple blank lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.changes_made += 1
                print(f"✅ Fixed: {file_path}")
            else:
                print(f"⏩ Skipped: {file_path} (no changes needed)")
                
            self.files_processed += 1
            
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    def fix_all_routes(self):
        """Fix all route files"""
        print("🔧 MASS AUTHENTICATION BARRIER FIX")
        print("=" * 50)
        
        # Find all route files
        route_files = []
        for root, dirs, files in os.walk('routes'):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    route_files.append(Path(root) / file)
        
        print(f"Found {len(route_files)} route files to fix")
        print()
        
        for file_path in route_files:
            self.fix_file(file_path)
        
        print()
        print(f"📊 SUMMARY:")
        print(f"Files processed: {self.files_processed}")
        print(f"Files modified: {self.changes_made}")
        print(f"Authentication barriers removed: ✅")

def main():
    fixer = AuthenticationFixer()
    fixer.fix_all_routes()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Test the application startup")
    print("2. Verify public routes are accessible")
    print("3. Check that demo mode works")
    print("4. Confirm authenticated routes still work")

if __name__ == "__main__":
    main()