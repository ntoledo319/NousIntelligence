import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Quick Audit System - Fast, focused testing and issue detection
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import requests
import re
import ast

class QuickAuditor:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'fixes_applied': [],
            'health_score': 0
        }
    
    def run_quick_audit(self):
        """Run focused audit on critical areas"""
        logger.info(🔍 Starting Quick Audit System)
        
        # Critical checks
        self.check_app_startup()
        self.check_critical_syntax()
        self.check_auth_barriers()
        self.check_api_endpoints()
        self.check_database_connection()
        
        # Calculate health score
        self.calculate_health_score()
        
        logger.info(✅ Quick Audit Complete - Health Score: {self.results['health_score']}/100)
        return self.results
    
    def check_app_startup(self):
        """Test if the Flask app can start without errors"""
        logger.info(🚀 Checking app startup...)
        
        try:
            # Test import of main app components
            sys.path.insert(0, '.')
            
            # Try importing key modules
            critical_imports = [
                'app',
                'models',
                'routes',
                'utils.auth_compat'
            ]
            
            for module in critical_imports:
                try:
                    __import__(module)
                    logger.info(✅ {module} imports successfully)
                except Exception as e:
                    self.results['issues'].append({
                        'category': 'import_error',
                        'severity': 'critical',
                        'issue': f'Cannot import {module}: {str(e)}'
                    })
                    logger.info(❌ {module} import failed: {e})
        
        except Exception as e:
            self.results['issues'].append({
                'category': 'startup_error',
                'severity': 'critical',
                'issue': f'App startup check failed: {str(e)}'
            })
    
    def check_critical_syntax(self):
        """Check syntax of critical Python files"""
        logger.info(🐍 Checking critical file syntax...)
        
        critical_files = [
            'app.py',
            'main.py',
            'models.py',
            'utils/auth_compat.py'
        ]
        
        for file_path in critical_files:
            if not os.path.exists(file_path):
                self.results['issues'].append({
                    'category': 'missing_file',
                    'severity': 'critical',
                    'issue': f'Critical file missing: {file_path}'
                })
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse with AST
                ast.parse(content, filename=file_path)
                logger.info(✅ {file_path} syntax OK)
                
            except SyntaxError as e:
                self.results['issues'].append({
                    'category': 'syntax_error',
                    'severity': 'critical',
                    'issue': f'Syntax error in {file_path} line {e.lineno}: {str(e)}'
                })
                logger.error(❌ Syntax error in {file_path}: {e})
            except Exception as e:
                self.results['issues'].append({
                    'category': 'file_error',
                    'severity': 'high',
                    'issue': f'Error reading {file_path}: {str(e)}'
                })
    
    def check_auth_barriers(self):
        """Check for authentication barriers that block public access"""
        logger.info(🔐 Checking authentication barriers...)
        
        barrier_count = 0
        barrier_files = []
        
        # Check route files for Flask-Login barriers
        routes_dir = Path('routes')
        if routes_dir.exists():
            for route_file in routes_dir.glob('*.py'):
                try:
                    with open(route_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for problematic patterns
                    barriers = [
                        '@login_required',
                        'abort(401)',
                        'abort(403)',
                        'You must be logged in'
                    ]
                    
                    file_barriers = []
                    for barrier in barriers:
                        if barrier in content:
                            file_barriers.append(barrier)
                            barrier_count += content.count(barrier)
                    
                    if file_barriers:
                        barrier_files.append({
                            'file': str(route_file),
                            'barriers': file_barriers
                        })
                        
                except Exception as e:
                    logger.warning(Warning: Could not check {route_file}: {e})
        
        if barrier_count > 0:
            self.results['issues'].append({
                'category': 'auth_barriers',
                'severity': 'high',
                'issue': f'Found {barrier_count} authentication barriers in {len(barrier_files)} files',
                'details': barrier_files
            })
            logger.info(⚠️ Found {barrier_count} authentication barriers)
        else:
            logger.info(✅ No authentication barriers detected)
    
    def check_api_endpoints(self):
        """Test critical API endpoints"""
        logger.info(🔌 Testing API endpoints...)
        
        base_url = "http://localhost:8080"
        endpoints = [
            ('/health', 'GET'),
            ('/api/health', 'GET'),
            ('/api/v1/chat', 'POST'),
            ('/api/v1/user', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == 'POST':
                    response = requests.post(f"{base_url}{endpoint}", 
                                           json={'message': 'test'}, timeout=3)
                else:
                    response = requests.get(f"{base_url}{endpoint}", timeout=3)
                
                if response.status_code >= 400:
                    self.results['issues'].append({
                        'category': 'api_error',
                        'severity': 'high' if response.status_code >= 500 else 'medium',
                        'issue': f'{endpoint} returned {response.status_code}'
                    })
                    logger.info(❌ {endpoint}: {response.status_code})
                else:
                    logger.info(✅ {endpoint}: {response.status_code})
                    
            except Exception as e:
                self.results['issues'].append({
                    'category': 'api_error',
                    'severity': 'high',
                    'issue': f'{endpoint} failed: {str(e)}'
                })
                logger.info(❌ {endpoint}: {e})
    
    def check_database_connection(self):
        """Test database connectivity"""
        logger.info(🗄️ Checking database connection...)
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            self.results['issues'].append({
                'category': 'database_error',
                'severity': 'critical',
                'issue': 'DATABASE_URL environment variable not set'
            })
            logger.info(❌ DATABASE_URL not set)
            return
        
        try:
            if database_url.startswith('postgres'):
                import psycopg2
                conn = psycopg2.connect(database_url)
                conn.close()
                logger.info(✅ PostgreSQL connection OK)
            elif database_url.startswith('sqlite'):
                import sqlite3
                conn = sqlite3.connect(database_url.replace('sqlite:///', ''))
                conn.close()
                logger.info(✅ SQLite connection OK)
            else:
                logger.info(⚠️ Unknown database type: {database_url[:20]}...)
                
        except Exception as e:
            self.results['issues'].append({
                'category': 'database_error',
                'severity': 'critical',
                'issue': f'Database connection failed: {str(e)}'
            })
            logger.info(❌ Database connection failed: {e})
    
    def calculate_health_score(self):
        """Calculate health score based on issues found"""
        base_score = 100
        
        for issue in self.results['issues']:
            severity = issue.get('severity', 'medium')
            if severity == 'critical':
                base_score -= 20
            elif severity == 'high':
                base_score -= 10
            elif severity == 'medium':
                base_score -= 5
            else:
                base_score -= 2
        
        self.results['health_score'] = max(0, base_score)
    
    def fix_critical_issues(self):
        """Attempt to fix critical issues automatically"""
        logger.info(🔧 Attempting to fix critical issues...)
        
        fixes_applied = []
        
        # Fix authentication barriers
        auth_issues = [i for i in self.results['issues'] if i['category'] == 'auth_barriers']
        if auth_issues:
            fixes_applied.extend(self._fix_auth_barriers())
        
        # Fix syntax errors
        syntax_issues = [i for i in self.results['issues'] if i['category'] == 'syntax_error']
        if syntax_issues:
            fixes_applied.extend(self._fix_syntax_issues(syntax_issues))
        
        self.results['fixes_applied'] = fixes_applied
        return fixes_applied
    
    def _fix_auth_barriers(self):
        """Fix authentication barriers by replacing with session-based auth"""
        fixes = []
        
        routes_dir = Path('routes')
        if not routes_dir.exists():
            return fixes
        
        for route_file in routes_dir.glob('*.py'):
            try:
                with open(route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace @login_required with @require_authentication
                if '@login_required' in content:
                    content = content.replace('@login_required', '@require_authentication')
                    
                    # Add import if needed
                    if 'from utils.auth_compat import require_authentication' not in content:
                        import_line = 'from utils.auth_compat import require_authentication\n'
                        # Find a good place to insert the import
                        lines = content.split('\n')
                        insert_index = 0
                        for i, line in enumerate(lines):
                            if line.startswith('from ') or line.startswith('import '):
                                insert_index = i + 1
                            elif line.strip() == '':
                                continue
                            else:
                                break
                        lines.insert(insert_index, import_line.strip())
                        content = '\n'.join(lines)
                
                # Replace abort(401) and abort(403) with redirect to demo
                content = re.sub(r'abort\(40[13]\)', 'redirect(url_for("main.demo"))', content)
                
                # Add redirect import if needed
                if 'redirect(url_for(' in content and 'from flask import' in content:
                    # Check if redirect is already imported
                    if not re.search(r'from flask import.*redirect', content):
                        content = re.sub(r'from flask import ([^\\n]+)', 
                                       r'from flask import \1, redirect', content)
                
                if content != original_content:
                    with open(route_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixes.append(f"Fixed authentication barriers in {route_file}")
                    
            except Exception as e:
                logger.warning(Warning: Could not fix auth barriers in {route_file}: {e})
        
        return fixes
    
    def _fix_syntax_issues(self, syntax_issues):
        """Fix simple syntax issues"""
        fixes = []
        
        for issue in syntax_issues:
            issue_text = issue['issue']
            if 'line' in issue_text:
                # Extract file path and line number
                parts = issue_text.split(' line ')
                if len(parts) >= 2:
                    file_path = parts[0].split(' in ')[-1]
                    try:
                        line_num = int(parts[1].split(':')[0])
                        
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                            
                            if 0 <= line_num - 1 < len(lines):
                                line = lines[line_num - 1]
                                
                                # Simple fixes
                                if line.strip().endswith('def ') or line.strip().endswith('class '):
                                    lines[line_num - 1] = line.rstrip() + ':\n'
                                    fixes.append(f"Added missing colon in {file_path} line {line_num}")
                                
                                # Fix unmatched parentheses
                                if line.count('(') > line.count(')'):
                                    lines[line_num - 1] = line.rstrip() + ')\n'
                                    fixes.append(f"Fixed unmatched parentheses in {file_path} line {line_num}")
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.writelines(lines)
                    
                    except (ValueError, IndexError, OSError) as e:
                        logger.info(Could not fix syntax issue: {e})
        
        return fixes
    
    def generate_report(self):
        """Generate quick audit report"""
        logger.info(\n)
        logger.info(QUICK AUDIT REPORT)
        logger.info(=)
        logger.info(Timestamp: {self.results['timestamp']})
        logger.info(Health Score: {self.results['health_score']}/100)
        logger.info(Issues Found: {len(self.results['issues'])})
        logger.info(Fixes Applied: {len(self.results['fixes_applied'])})
        
        if self.results['issues']:
            logger.info(\nISSUES DETECTED:)
            for issue in self.results['issues']:
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢'
                }.get(issue['severity'], '🔵')
                logger.info({severity_emoji} [{issue['severity'].upper()}] {issue['issue']})
        
        if self.results['fixes_applied']:
            logger.info(\nFIXES APPLIED:)
            for fix in self.results['fixes_applied']:
                logger.info(✅ {fix})
        
        logger.info(=)
        
        return self.results

def main():
    """Run quick audit cycles"""
    auditor = QuickAuditor()
    
    for cycle in range(1, 4):
        logger.info(\n{'='*40})
        logger.info(QUICK AUDIT CYCLE {cycle}/3)
        logger.info({'='*40})
        
        # Run audit
        results = auditor.run_quick_audit()
        
        # Fix issues
        fixes = auditor.fix_critical_issues()
        
        # Generate report
        auditor.generate_report()
        
        # Break if health is good enough
        if results['health_score'] >= 85:
            logger.info(\n✅ Good health score achieved: {results['health_score']}/100)
            break
            
        logger.info(\nCycle {cycle} complete. Preparing for next cycle...)

if __name__ == "__main__":
    main()