"""
Advanced Authentication Barrier Detection System
Comprehensive scanner and fixer for authentication issues
"""
import os
import re
import json
import ast
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

class AuthenticationBarrierDetector:
    """Advanced authentication barrier detection and prevention system"""
    
    def __init__(self):
        self.root_path = Path('.')
        self.results = {
            'critical_barriers': [],
            'flask_login_issues': [],
            'redirect_loops': [],
            'unauthorized_responses': [],
            'session_issues': [],
            'missing_demo_support': []
        }
        
        # Authentication barrier patterns
        self.barrier_patterns = {
            'flask_login_required': [
                r'@login_required',
                r'from flask_login import.*login_required',
                r'login_required\(',
            ],
            'current_user_usage': [
                r'current_user\.is_authenticated',
                r'current_user\.id',
                r'current_user\.',
                r'from flask_login import.*current_user'
            ],
            'auth_redirects': [
                r'redirect\([\'"][^\'"]*/login[^\'\"]*[\'\"]\)',
                r'url_for\([\'"]login[\'\"]\)',
                r'return redirect.*login'
            ],
            'auth_messages': [
                r'["\']You must be logged in[^"\']*["\']',
                r'["\']Login required[^"\']*["\']',
                r'["\']Authentication required[^"\']*["\']',
                r'["\']Please log in[^"\']*["\']'
            ],
            'abort_unauthorized': [
                r'abort\(401\)',
                r'abort\(403\)',
                r'return.*401',
                r'return.*403'
            ],
            'session_checks': [
                r'if.*session\[.*user.*\]',
                r'session\.get\([\'"]user[\'\"]\)',
                r'if.*not.*session'
            ]
        }
    
    def scan_entire_codebase(self) -> Dict:
        """Comprehensive scan of entire codebase for authentication barriers"""
        logger.info("🔍 Starting comprehensive authentication barrier scan...")
        
        # Scan all Python files
        python_files = list(self.root_path.rglob('*.py'))
        logger.info(f"Scanning {len(python_files)} Python files...")
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                self._analyze_file(file_path, content)
            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
        
        # Analyze route patterns
        self._analyze_route_patterns()
        
        # Check authentication system consistency
        self._check_auth_system_consistency()
        
        # Generate comprehensive report
        return self._generate_barrier_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            'venv',
            '.pytest_cache',
            'backup',
            'archive'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path, content: str):
        """Analyze a single file for authentication barriers"""
        file_str = str(file_path)
        
        # Check for Flask-Login patterns
        flask_login_issues = []
        for pattern in self.barrier_patterns['flask_login_required']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                flask_login_issues.append({
                    'file': file_str,
                    'line': line_no,
                    'pattern': pattern,
                    'match': match.group(),
                    'severity': 'CRITICAL'
                })
        
        if flask_login_issues:
            self.results['flask_login_issues'].extend(flask_login_issues)
        
        # Check for current_user usage
        current_user_issues = []
        for pattern in self.barrier_patterns['current_user_usage']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                current_user_issues.append({
                    'file': file_str,
                    'line': line_no,
                    'pattern': pattern,
                    'match': match.group(),
                    'severity': 'HIGH'
                })
        
        if current_user_issues:
            self.results['critical_barriers'].extend(current_user_issues)
        
        # Check for authentication redirects
        redirect_issues = []
        for pattern in self.barrier_patterns['auth_redirects']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                redirect_issues.append({
                    'file': file_str,
                    'line': line_no,
                    'pattern': pattern,
                    'match': match.group(),
                    'severity': 'HIGH'
                })
        
        if redirect_issues:
            self.results['redirect_loops'].extend(redirect_issues)
        
        # Check for authentication messages
        message_issues = []
        for pattern in self.barrier_patterns['auth_messages']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                message_issues.append({
                    'file': file_str,
                    'line': line_no,
                    'pattern': pattern,
                    'match': match.group(),
                    'severity': 'MEDIUM'
                })
        
        if message_issues:
            self.results['critical_barriers'].extend(message_issues)
        
        # Check for unauthorized responses
        abort_issues = []
        for pattern in self.barrier_patterns['abort_unauthorized']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                abort_issues.append({
                    'file': file_str,
                    'line': line_no,
                    'pattern': pattern,
                    'match': match.group(),
                    'severity': 'HIGH'
                })
        
        if abort_issues:
            self.results['unauthorized_responses'].extend(abort_issues)
    
    def _analyze_route_patterns(self):
        """Analyze route patterns for authentication barriers"""
        route_files = []
        routes_dir = Path('routes')
        
        if routes_dir.exists():
            route_files = list(routes_dir.glob('*.py'))
        
        for route_file in route_files:
            try:
                content = route_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for routes with authentication decorators
                route_pattern = r'@\w+\.route\([^)]+\)\s*@login_required'
                matches = re.finditer(route_pattern, content, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    self.results['critical_barriers'].append({
                        'file': str(route_file),
                        'line': line_no,
                        'pattern': 'route_with_login_required',
                        'match': match.group(),
                        'severity': 'CRITICAL',
                        'description': 'Route decorated with @login_required'
                    })
                    
            except Exception as e:
                logger.warning(f"Could not analyze route file {route_file}: {e}")
    
    def _check_auth_system_consistency(self):
        """Check for authentication system consistency issues"""
        app_py = Path('app.py')
        
        if not app_py.exists():
            self.results['session_issues'].append({
                'issue': 'app.py not found',
                'severity': 'CRITICAL',
                'description': 'Main application file missing'
            })
            return
        
        try:
            content = app_py.read_text(encoding='utf-8', errors='ignore')
            
            # Check for Flask-Login initialization
            flask_login_init = re.search(r'LoginManager|login_manager', content)
            flask_login_imports = re.search(r'from flask_login import', content)
            
            # Check for session-based auth
            session_auth = re.search(r'session\[.*user.*\]', content)
            
            if flask_login_imports and not flask_login_init:
                self.results['session_issues'].append({
                    'issue': 'Flask-Login imported but not initialized',
                    'severity': 'CRITICAL',
                    'description': 'Flask-Login is imported but LoginManager is not initialized'
                })
            
            if not session_auth and not flask_login_init:
                self.results['session_issues'].append({
                    'issue': 'No authentication system detected',
                    'severity': 'HIGH',
                    'description': 'Neither session-based nor Flask-Login authentication found'
                })
                
        except Exception as e:
            logger.warning(f"Could not analyze app.py: {e}")
    
    def _generate_barrier_report(self) -> Dict:
        """Generate comprehensive barrier report"""
        total_barriers = (
            len(self.results['critical_barriers']) +
            len(self.results['flask_login_issues']) +
            len(self.results['redirect_loops']) +
            len(self.results['unauthorized_responses'])
        )
        
        # Categorize by severity
        critical_count = sum(1 for category in self.results.values() 
                           for item in (category if isinstance(category, list) else [])
                           if isinstance(item, dict) and item.get('severity') == 'CRITICAL')
        
        high_count = sum(1 for category in self.results.values() 
                        for item in (category if isinstance(category, list) else [])
                        if isinstance(item, dict) and item.get('severity') == 'HIGH')
        
        medium_count = sum(1 for category in self.results.values() 
                          for item in (category if isinstance(category, list) else [])
                          if isinstance(item, dict) and item.get('severity') == 'MEDIUM')
        
        report = {
            'summary': {
                'total_barriers': total_barriers,
                'critical_barriers': critical_count,
                'high_priority_barriers': high_count,
                'medium_priority_barriers': medium_count,
                'scan_timestamp': str(os.popen('date').read().strip())
            },
            'barriers_by_category': {
                'flask_login_issues': len(self.results['flask_login_issues']),
                'critical_barriers': len(self.results['critical_barriers']),
                'redirect_loops': len(self.results['redirect_loops']),
                'unauthorized_responses': len(self.results['unauthorized_responses']),
                'session_issues': len(self.results['session_issues'])
            },
            'detailed_findings': self.results,
            'fix_recommendations': self._generate_fix_recommendations()
        }
        
        return report
    
    def _generate_fix_recommendations(self) -> List[Dict]:
        """Generate specific fix recommendations"""
        recommendations = []
        
        if self.results['flask_login_issues']:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Flask-Login Removal',
                'description': 'Remove all Flask-Login decorators and replace with session-based authentication',
                'affected_files': len(set(item['file'] for item in self.results['flask_login_issues'])),
                'fix_action': 'Replace @login_required with session checks or remove entirely for public access'
            })
        
        if self.results['critical_barriers']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Authentication Barriers',
                'description': 'Remove or modify authentication barriers to allow public access',
                'affected_files': len(set(item['file'] for item in self.results['critical_barriers'])),
                'fix_action': 'Add demo mode support and public access options'
            })
        
        if self.results['redirect_loops']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Redirect Loops',
                'description': 'Fix authentication redirect loops',
                'affected_files': len(set(item['file'] for item in self.results['redirect_loops'])),
                'fix_action': 'Replace login redirects with demo mode or public access'
            })
        
        if self.results['unauthorized_responses']:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Unauthorized Responses',
                'description': 'Replace 401/403 responses with demo-friendly alternatives',
                'affected_files': len(set(item['file'] for item in self.results['unauthorized_responses'])),
                'fix_action': 'Return demo data instead of unauthorized errors'
            })
        
        return recommendations
    
    def save_report(self, filename: str = 'authentication_barrier_report.json'):
        """Save comprehensive report to file"""
        report = self._generate_barrier_report()
        
        report_path = Path('tests') / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also generate markdown report
        self._save_markdown_report(report, report_path.with_suffix('.md'))
        
        logger.info(f"Authentication barrier report saved to {report_path}")
        return report
    
    def _save_markdown_report(self, report: Dict, path: Path):
        """Save human-readable markdown report"""
        lines = [
            "# Authentication Barrier Detection Report",
            "",
            "## Summary",
            f"- **Total Barriers Found**: {report['summary']['total_barriers']}",
            f"- **Critical Barriers**: {report['summary']['critical_barriers']}",
            f"- **High Priority**: {report['summary']['high_priority_barriers']}",
            f"- **Medium Priority**: {report['summary']['medium_priority_barriers']}",
            f"- **Scan Date**: {report['summary']['scan_timestamp']}",
            "",
            "## Barriers by Category",
        ]
        
        for category, count in report['barriers_by_category'].items():
            lines.append(f"- **{category.replace('_', ' ').title()}**: {count}")
        
        lines.extend([
            "",
            "## Fix Recommendations",
        ])
        
        for i, rec in enumerate(report['fix_recommendations'], 1):
            lines.extend([
                f"### {i}. {rec['category']} ({rec['priority']})",
                f"**Description**: {rec['description']}",
                f"**Affected Files**: {rec['affected_files']}",
                f"**Fix Action**: {rec['fix_action']}",
                ""
            ])
        
        # Add detailed findings
        if report['detailed_findings']['flask_login_issues']:
            lines.extend([
                "## Flask-Login Issues",
                "| File | Line | Pattern | Match |",
                "|------|------|---------|-------|"
            ])
            
            for issue in report['detailed_findings']['flask_login_issues']:
                lines.append(f"| {issue['file']} | {issue['line']} | {issue['pattern']} | `{issue['match']}` |")
        
        if report['detailed_findings']['critical_barriers']:
            lines.extend([
                "",
                "## Critical Authentication Barriers",
                "| File | Line | Pattern | Match | Severity |",
                "|------|------|---------|-------|----------|"
            ])
            
            for issue in report['detailed_findings']['critical_barriers']:
                lines.append(f"| {issue['file']} | {issue['line']} | {issue['pattern']} | `{issue['match']}` | {issue['severity']} |")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))


class AuthenticationBarrierFixer:
    """Advanced authentication barrier fixing system"""
    
    def __init__(self):
        self.detector = AuthenticationBarrierDetector()
        self.fixes_applied = 0
        self.backup_created = False
    
    def fix_all_barriers(self, create_backup: bool = True) -> Dict:
        """Fix all detected authentication barriers"""
        logger.info("🔧 Starting comprehensive authentication barrier fixes...")
        
        # First, detect all barriers
        report = self.detector.scan_entire_codebase()
        
        if create_backup and not self.backup_created:
            self._create_backup()
            self.backup_created = True
        
        # Apply fixes based on findings
        results = {
            'flask_login_fixes': 0,
            'auth_message_fixes': 0,
            'redirect_fixes': 0,
            'abort_fixes': 0,
            'files_modified': set(),
            'errors': []
        }
        
        # Fix Flask-Login issues
        results['flask_login_fixes'] = self._fix_flask_login_issues(report['detailed_findings']['flask_login_issues'])
        
        # Fix authentication messages
        results['auth_message_fixes'] = self._fix_auth_messages(report['detailed_findings']['critical_barriers'])
        
        # Fix redirects
        results['redirect_fixes'] = self._fix_auth_redirects(report['detailed_findings']['redirect_loops'])
        
        # Fix abort calls
        results['abort_fixes'] = self._fix_abort_calls(report['detailed_findings']['unauthorized_responses'])
        
        # Create enhanced authentication compatibility layer
        self._create_enhanced_auth_compat()
        
        logger.info(f"✅ Applied {self.fixes_applied} authentication fixes")
        return results
    
    def _create_backup(self):
        """Create backup of files before modification"""
        import shutil
        from datetime import datetime
        
        backup_dir = Path('backup_auth_fixes') / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup critical files
        critical_files = ['app.py', 'utils/auth_compat.py']
        
        # Backup routes directory
        routes_dir = Path('routes')
        if routes_dir.exists():
            shutil.copytree(routes_dir, backup_dir / 'routes', dirs_exist_ok=True)
        
        for file_path in critical_files:
            if Path(file_path).exists():
                shutil.copy2(file_path, backup_dir / Path(file_path).name)
        
        logger.info(f"Created backup at {backup_dir}")
    
    def _fix_flask_login_issues(self, issues: List[Dict]) -> int:
        """Fix Flask-Login related issues"""
        fixes = 0
        files_to_fix = defaultdict(list)
        
        # Group issues by file
        for issue in issues:
            files_to_fix[issue['file']].append(issue)
        
        for file_path, file_issues in files_to_fix.items():
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                content = path.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                # Remove Flask-Login imports
                content = re.sub(r'from flask_login import.*\n', '', content)
                content = re.sub(r'import flask_login.*\n', '', content)
                
                # Add auth compatibility import if needed
                if '@login_required' in content and 'from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
                    # Find a good place to add import
                    import_lines = []
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('from flask import') or line.startswith('import flask'):
                            import_lines.append(i)
                    
                    if import_lines:
                        insert_at = max(import_lines) + 1
                        lines.insert(insert_at, 'from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
                        content = '\n'.join(lines)
                
                # Replace @login_required with public access decorator
                content = re.sub(r'@login_required\s*\n', '', content)
                
                # Replace current_user references
                content = re.sub(r'current_user\.is_authenticated', 'is_authenticated()', content)
                content = re.sub(r'current_user\.id', 'get_current_user()["id"]', content)
                content = re.sub(r'current_user\.name', 'get_current_user()["name"]', content)
                content = re.sub(r'current_user\.email', 'get_current_user()["email"]', content)
                
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    fixes += 1
                    logger.info(f"Fixed Flask-Login issues in {file_path}")
                    
            except Exception as e:
                logger.error(f"Error fixing Flask-Login issues in {file_path}: {e}")
        
        return fixes
    
    def _fix_auth_messages(self, issues: List[Dict]) -> int:
        """Fix authentication error messages"""
        fixes = 0
        files_to_fix = defaultdict(list)
        
        for issue in issues:
            if 'auth_messages' in issue.get('pattern', ''):
                files_to_fix[issue['file']].append(issue)
        
        for file_path, file_issues in files_to_fix.items():
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                content = path.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                # Replace authentication messages
                auth_message_replacements = [
                    (r'"You must be logged in[^"]*"', '"Demo mode - exploring NOUS features"'),
                    (r"'You must be logged in[^']*'", "'Demo mode - exploring NOUS features'"),
                    (r'"Login required[^"]*"', '"Demo access available"'),
                    (r"'Login required[^']*'", "'Demo access available'"),
                    (r'"Authentication required[^"]*"', '"Demo mode enabled"'),
                    (r"'Authentication required[^']*'", "'Demo mode enabled'"),
                ]
                
                for pattern, replacement in auth_message_replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    fixes += 1
                    logger.info(f"Fixed authentication messages in {file_path}")
                    
            except Exception as e:
                logger.error(f"Error fixing authentication messages in {file_path}: {e}")
        
        return fixes
    
    def _fix_auth_redirects(self, issues: List[Dict]) -> int:
        """Fix authentication redirects"""
        fixes = 0
        files_to_fix = defaultdict(list)
        
        for issue in issues:
            files_to_fix[issue['file']].append(issue)
        
        for file_path, file_issues in files_to_fix.items():
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                content = path.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                # Replace login redirects with demo mode
                redirect_replacements = [
                    (r'redirect\([\'"][^\'"]*/login[^\'\"]*[\'\"]\)', 'redirect("/demo")'),
                    (r'url_for\([\'"]login[\'\"]\)', 'url_for("demo")'),
                    (r'return redirect.*login.*\)', 'return redirect("/demo")'),
                ]
                
                for pattern, replacement in redirect_replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    fixes += 1
                    logger.info(f"Fixed authentication redirects in {file_path}")
                    
            except Exception as e:
                logger.error(f"Error fixing authentication redirects in {file_path}: {e}")
        
        return fixes
    
    def _fix_abort_calls(self, issues: List[Dict]) -> int:
        """Fix abort(401) and abort(403) calls"""
        fixes = 0
        files_to_fix = defaultdict(list)
        
        for issue in issues:
            files_to_fix[issue['file']].append(issue)
        
        for file_path, file_issues in files_to_fix.items():
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                content = path.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                # Replace abort calls with demo-friendly responses
                abort_replacements = [
                    (r'abort\(401\)', 'jsonify({"error": "Demo mode - limited access", "demo": True})'),
                    (r'abort\(403\)', 'jsonify({"error": "Demo mode - read only access", "demo": True})'),
                    (r'return.*401', 'return jsonify({"error": "Demo mode", "demo": True}), 200'),
                    (r'return.*403', 'return jsonify({"error": "Demo mode", "demo": True}), 200'),
                ]
                
                for pattern, replacement in abort_replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    fixes += 1
                    logger.info(f"Fixed abort calls in {file_path}")
                    
            except Exception as e:
                logger.error(f"Error fixing abort calls in {file_path}: {e}")
        
        return fixes
    
    def _create_enhanced_auth_compat(self):
        """Create enhanced authentication compatibility layer"""
        auth_compat_content = '''"""
Enhanced Authentication Compatibility Layer
Zero-barrier authentication system with comprehensive demo support
"""

from flask import session, request, redirect, jsonify, url_for
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def get_current_user():
    """Get current user - always returns a valid user object for zero barriers"""
    # Return session user if available
    if session.get('user'):
        user = session['user']
        if isinstance(user, dict):
            return user
        else:
            # Convert non-dict user to dict
            return {
                'id': getattr(user, 'id', 'session_user'),
                'name': getattr(user, 'name', 'Authenticated User'),
                'email': getattr(user, 'email', 'user@nous.app'),
                'authenticated': True
            }
    
    # Always provide demo user for public access - ZERO BARRIERS
    return {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'demo_mode': True,
        'authenticated': True  # Always authenticated to prevent barriers
    }

def is_authenticated():
    """Always return True - ZERO AUTHENTICATION BARRIERS"""
    return True

def login_required(f):
    """Zero-barrier decorator - always allows access with demo fallback"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Always allow access, provide demo user if needed
        user = get_current_user()
        if not session.get('user') and not user.get('demo_mode'):
            # Set demo user in session for consistency
            session['demo_user'] = True
        
        return f(*args, **kwargs)
    return decorated_function

def require_authentication():
    """Legacy function - never blocks access"""
    return None

def check_authentication():
    """Check authentication - always succeeds"""
    return True

# Legacy current_user object for backward compatibility
class AlwaysAuthenticatedUser:
    """User object that's always authenticated"""
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def id(self):
        return get_current_user()['id']
    
    @property
    def name(self):
        return get_current_user()['name']
    
    @property
    def email(self):
        return get_current_user()['email']
    
    def get_id(self):
        return str(self.id)
    
    def get(self, key, default=None):
        user = get_current_user()
        return user.get(key, default)

# Create global current_user object
current_user = AlwaysAuthenticatedUser()

# Additional helper functions
def get_user_id():
    """Get current user ID"""
    return get_current_user()['id']

def get_user_name():
    """Get current user name"""
    return get_current_user()['name']

def get_user_email():
    """Get current user email"""
    return get_current_user()['email']

def is_demo_mode():
    """Check if in demo mode"""
    return get_current_user().get('demo_mode', False)

def require_auth(f):
    """Alternative authentication decorator - zero barriers"""
    return login_required(f)

def authenticated(f):
    """Alternative authentication decorator - zero barriers"""
    return login_required(f)

# For routes that need to check auth but allow demo
def optional_auth(f):
    """Optional authentication - always allows access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Demo mode helpers
def ensure_demo_access():
    """Ensure demo access is available"""
    if not session.get('user') and not session.get('demo_user'):
        session['demo_user'] = True
        session['demo_mode'] = True

def get_demo_user():
    """Get demo user object"""
    return {
        'id': 'demo_user',
        'name': 'Demo User', 
        'email': 'demo@nous.app',
        'demo_mode': True,
        'authenticated': True
    }

# Initialize demo mode on import
def init_demo_mode():
    """Initialize demo mode support"""
    try:
        from flask import session
        if not session.get('user'):
            session['demo_user'] = True
    except RuntimeError:
        # Outside application context
        pass

# Export all functions for easy importing
__all__ = [
    'get_current_user', 'is_authenticated', 'login_required', 
    'require_authentication', 'check_authentication', 'current_user',
    'get_user_id', 'get_user_name', 'get_user_email', 'is_demo_mode',
    'require_auth', 'authenticated', 'optional_auth', 'ensure_demo_access',
    'get_demo_user', 'AlwaysAuthenticatedUser'
]
'''
        
        auth_compat_path = Path('utils/auth_compat.py')
        auth_compat_path.parent.mkdir(exist_ok=True)
        auth_compat_path.write_text(auth_compat_content)
        logger.info("Created enhanced authentication compatibility layer")


if __name__ == "__main__":
    # Run authentication barrier detection
    detector = AuthenticationBarrierDetector()
    report = detector.scan_entire_codebase()
    detector.save_report()
    
    print(f"\n🔍 Authentication Barrier Detection Complete")
    print(f"Total Barriers Found: {report['summary']['total_barriers']}")
    print(f"Critical: {report['summary']['critical_barriers']}")
    print(f"High Priority: {report['summary']['high_priority_barriers']}")
    print(f"Medium Priority: {report['summary']['medium_priority_barriers']}")
    
    if report['summary']['total_barriers'] > 0:
        print(f"\n🔧 Starting automatic fixes...")
        fixer = AuthenticationBarrierFixer()
        fix_results = fixer.fix_all_barriers()
        
        print(f"✅ Fixes Applied:")
        print(f"  - Flask-Login fixes: {fix_results['flask_login_fixes']}")
        print(f"  - Auth message fixes: {fix_results['auth_message_fixes']}")
        print(f"  - Redirect fixes: {fix_results['redirect_fixes']}")
        print(f"  - Abort call fixes: {fix_results['abort_fixes']}")
        print(f"  - Files modified: {len(fix_results['files_modified'])}")
    else:
        print(f"✅ No authentication barriers detected!")