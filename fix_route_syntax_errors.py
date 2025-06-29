#!/usr/bin/env python3
"""
Fix Route Syntax Errors
Systematically fixes syntax errors introduced by authentication fixes
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouteSyntaxFixer:
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        
    def fix_all_route_syntax_errors(self):
        """Fix syntax errors in all route files"""
        logger.info("🔧 Fixing syntax errors in route files...")
        
        route_files = [
            'routes/main.py',
            'routes/simple_auth_api.py', 
            'routes/api_routes.py',
            'routes/chat_routes.py',
            'routes/dashboard.py',
            'routes/user_routes.py',
            'routes/dbt_routes.py',
            'routes/cbt_routes.py',
            'routes/aa_routes.py',
            'routes/financial_routes.py',
            'routes/search_routes.py',
            'routes/analytics_routes.py',
            'routes/notification_routes.py',
            'routes/maps_routes.py',
            'routes/weather_routes.py',
            'routes/tasks_routes.py'
        ]
        
        for route_file in route_files:
            if os.path.exists(route_file):
                self.fix_route_file(route_file)
        
        self.report_results()
    
    def fix_route_file(self, filepath):
        """Fix syntax errors in a specific route file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix common syntax errors from authentication fixes
            fixes = [
                # Fix duplicate imports and malformed function calls
                (r'from utils\.auth_compat import.*get_demo_user\(\).*', 
                 'from utils.auth_compat import login_required, get_demo_user, is_authenticated'),
                
                # Fix duplicate get_demo_user calls
                (r'get_get_demo_user\(\)', 'get_demo_user()'),
                (r'get_demo_user\(\)\.', 'get_demo_user().'),
                
                # Fix malformed imports
                (r'from utils\.auth_compat import.*,.*,.*,.*,.*', 
                 'from utils.auth_compat import login_required, get_demo_user, is_authenticated'),
                
                # Fix docstring placement issues
                (r'"""\nfrom utils\.auth_compat.*\n(.*)\n"""', r'"""\n\1\n"""'),
                
                # Remove duplicate import lines
                (r'from utils\.auth_compat import get_demo_user\nfrom utils\.auth_compat import.*', 
                 'from utils.auth_compat import login_required, get_demo_user, is_authenticated'),
            ]
            
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Ensure proper import structure
            lines = content.split('\n')
            cleaned_lines = []
            import_section = []
            docstring_complete = False
            
            for i, line in enumerate(lines):
                # Handle docstring
                if line.strip().startswith('"""') and not docstring_complete:
                    cleaned_lines.append(line)
                    if line.count('"""') == 2:
                        docstring_complete = True
                    continue
                elif not docstring_complete and '"""' in line:
                    cleaned_lines.append(line)
                    docstring_complete = True
                    continue
                elif not docstring_complete:
                    cleaned_lines.append(line)
                    continue
                
                # Handle imports
                if line.strip().startswith(('from ', 'import ')) and 'auth_compat' in line:
                    if line not in import_section:
                        import_section.append('from utils.auth_compat import login_required, get_demo_user, is_authenticated')
                elif line.strip().startswith(('from ', 'import ')):
                    cleaned_lines.append(line)
                else:
                    # Add auth_compat import if we haven't added it yet
                    if import_section and not any('auth_compat' in existing_line for existing_line in cleaned_lines):
                        cleaned_lines.extend(import_section)
                        import_section = []
                    cleaned_lines.append(line)
            
            content = '\n'.join(cleaned_lines)
            
            # Remove duplicate empty lines
            content = re.sub(r'\n\n\n+', '\n\n', content)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(filepath)
                logger.info(f"✅ Fixed syntax errors in {filepath}")
            
        except Exception as e:
            self.failed_files.append(f"{filepath}: {e}")
            logger.error(f"❌ Failed to fix {filepath}: {e}")
    
    def report_results(self):
        """Report fix results"""
        logger.info(f"📊 Route Syntax Fix Results:")
        logger.info(f"   ✅ Files fixed: {len(self.fixed_files)}")
        logger.info(f"   ❌ Files failed: {len(self.failed_files)}")
        
        if self.fixed_files:
            logger.info("✅ Fixed files:")
            for file in self.fixed_files:
                logger.info(f"     {file}")
        
        if self.failed_files:
            logger.info("❌ Failed files:")
            for file in self.failed_files:
                logger.info(f"     {file}")

def main():
    fixer = RouteSyntaxFixer()
    fixer.fix_all_route_syntax_errors()

if __name__ == "__main__":
    main()