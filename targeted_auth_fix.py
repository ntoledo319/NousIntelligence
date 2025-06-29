#!/usr/bin/env python3
"""
Targeted Authentication Fix for Main Application Files
Focuses on routes/, utils/, and main app files to eliminate authentication barriers
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TargetedAuthFix:
    def __init__(self):
        self.fixed_files = []
        self.target_directories = ['routes', 'utils', 'services', '.']
        self.target_files = ['app.py', 'main.py', 'enhanced_app.py']
        
    def fix_main_app_files(self):
        """Fix authentication in main application files"""
        logger.info("🎯 Targeting main application files for authentication fixes")
        
        # Process target directories
        for directory in self.target_directories:
            if os.path.exists(directory):
                self.process_directory(directory)
        
        # Process specific files
        for filename in self.target_files:
            if os.path.exists(filename):
                self.fix_file(Path(filename))
        
        # Create authentication compatibility
        self.create_auth_compatibility()
        
        logger.info(f"✅ Fixed {len(self.fixed_files)} files")
        
    def process_directory(self, directory):
        """Process all Python files in a directory"""
        for root, dirs, files in os.walk(directory):
            # Skip cache and backup directories
            dirs[:] = [d for d in dirs if not d.startswith(('__pycache__', 'backup_', '.git'))]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    self.fix_file(filepath)
    
    def fix_file(self, filepath):
        """Fix authentication barriers in a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Flask-Login elimination patterns
            patterns = [
                # Remove Flask-Login imports
                (r'# Flask-Login removed for public access
                (r'# Flask-Login removed for public access', '# Flask-Login removed for public access'),
                
                # Replace login_required decorator
                (r'# Authentication barrier removed\s*\n', '# Authentication barrier removed\n'),
                (r'# Authentication barrier removed', '# Authentication barrier removed'),
                
                # Replace get_demo_user() references
                (r'get_demo_user()\.', 'get_demo_user().'),
                (r'get_demo_user()', 'get_demo_user()'),
                
                # Remove authentication checks
                (r'if False:  # Auth check removed  # Auth check removed'),
                (r'abort\(401\)', 'pass  # Auth barrier removed'),
                (r'abort\(403\)', 'pass  # Auth barrier removed'),
                
                # Replace error messages
                (r'"Demo mode - full access available"'),
                (r"'Demo mode - full access available'"),
                
                # Replace redirects to login
                (r'redirect\(.*login.*\)', 'redirect("/demo")'),
                (r'url_for\(["\'].*login.*["\']\)', '"/demo"'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Add demo user support if get_demo_user() was replaced
            if 'get_demo_user()' in content and 'get_demo_user()' not in original_content:
                # Add import at top
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith(('from ', 'import ')) and 'get_demo_user' not in line:
                        continue
                    elif line.strip() and not line.strip().startswith(('#', '"""', "'''")):
                        lines.insert(i, 'from utils.auth_compat import get_demo_user')
                        content = '\n'.join(lines)
                        break
            
            # Save if changes were made
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(filepath))
                logger.info(f"✅ Fixed {filepath}")
                
        except Exception as e:
            logger.error(f"❌ Error fixing {filepath}: {e}")
    
    def create_auth_compatibility(self):
        """Create authentication compatibility layer"""
        os.makedirs('utils', exist_ok=True)
        
        auth_compat = '''"""
Authentication Compatibility Layer
Provides demo user support and removes all authentication barriers
"""

from flask import session
from datetime import datetime

def get_demo_user():
    """Get demo user object"""
    return type('DemoUser', (), {
        'id': 'demo_user_123',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'is_authenticated': True,
        'is_active': True,
        'is_anonymous': False,
        'demo_mode': True
    })()

def is_authenticated():
    """Always return True for demo mode"""
    return True

def login_required(f):
    """No-op decorator for public access"""
    return f

# Ensure demo user in session
def ensure_demo_user():
    """Ensure demo user is in session"""
    if 'user' not in session:
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True
        }
    return session['user']

# Global demo user
get_demo_user() = get_demo_user()
'''
        
        with open('utils/auth_compat.py', 'w') as f:
            f.write(auth_compat)
        
        logger.info("✅ Created authentication compatibility layer")

def main():
    fixer = TargetedAuthFix()
    fixer.fix_main_app_files()

if __name__ == "__main__":
    main()