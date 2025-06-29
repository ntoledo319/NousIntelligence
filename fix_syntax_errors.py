#!/usr/bin/env python3
"""
Fix Syntax Errors Caused by Mass Authentication Fix
Repairs corrupted route files with proper structure
"""

import os
import re
import ast

def fix_corrupted_route_file(file_path):
    """Fix a route file that was corrupted by the mass authentication fix"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if file has syntax errors
        try:
            ast.parse(content)
            print(f"✅ {file_path} - No syntax errors")
            return True
        except SyntaxError as e:
            print(f"🔧 {file_path} - Fixing syntax error: {e}")
        
        # Common fixes needed
        original_content = content
        
        # Fix missing imports at start of file
        if not content.startswith('"""') and not content.startswith('from ') and not content.startswith('import '):
            # Find the blueprint name from file path
            blueprint_name = os.path.basename(file_path).replace('.py', '')
            if blueprint_name.endswith('_routes'):
                blueprint_name = blueprint_name[:-7]  # Remove _routes
            
            # Add proper header
            header = f'''"""
{blueprint_name.title()} routes
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, session

# Create blueprint
{blueprint_name}_bp = Blueprint('{blueprint_name}', __name__)

'''
            content = header + content
        
        # Fix broken function definitions
        # Look for patterns like:
        # """
        # def require_authentication():
        # Should be:
        # """
        # 
        # def require_authentication():
        
        # Fix missing newlines after docstrings
        content = re.sub(r'"""([^"]*?)"""(\s*)def ', r'"""\1"""\n\n\2def ', content)
        
        # Fix authentication helper functions that got mangled
        if 'def require_authentication():' in content and 'from flask import session' in content:
            # Find and fix the require_authentication function
            auth_pattern = r'def require_authentication\(\):(.*?)(?=def |\n@|\nclass |\Z)'
            match = re.search(auth_pattern, content, re.DOTALL)
            if match:
                auth_func = '''def require_authentication():
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
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    if 'user' in session:
        return session['user']
    return {'name': 'Demo User', 'email': 'demo@example.com', 'demo': True}

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user']

'''
                content = content.replace(match.group(0), auth_func)
        
        # Fix broken route decorators
        content = re.sub(r'@([a-zA-Z_]+)\.route\([^)]+\)\s*@\s*([a-zA-Z_]+)\s*', r'@\1.route\2\ndef ', content)
        
        # Remove any orphaned decorators (decorators not followed by function definitions)
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith('@') and i + 1 < len(lines):
                next_line = lines[i + 1]
                # If decorator is not followed by def or class, skip it
                if not next_line.strip().startswith('def ') and not next_line.strip().startswith('class '):
                    print(f"  Removing orphaned decorator: {line.strip()}")
                    i += 1
                    continue
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        # Try parsing again
        try:
            ast.parse(content)
            # Write back the fixed content
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ {file_path} - Fixed successfully")
            return True
        except SyntaxError as e:
            print(f"❌ {file_path} - Could not fix: {e}")
            # Restore original content
            with open(file_path, 'w') as f:
                f.write(original_content)
            return False
            
    except Exception as e:
        print(f"❌ {file_path} - Error: {e}")
        return False

def main():
    """Fix all route files with syntax errors"""
    print("🔧 FIXING SYNTAX ERRORS FROM MASS AUTHENTICATION FIX")
    print("=" * 60)
    
    routes_dir = "routes"
    fixed_count = 0
    error_count = 0
    
    # Get all Python files in routes directory
    for root, dirs, files in os.walk(routes_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_corrupted_route_file(file_path):
                    fixed_count += 1
                else:
                    error_count += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"Files fixed: {fixed_count}")
    print(f"Files with errors: {error_count}")
    
    if error_count == 0:
        print("🎉 All syntax errors fixed!")
    else:
        print("⚠️  Some files still have errors - manual review needed")

if __name__ == "__main__":
    main()