#!/usr/bin/env python3
"""
Comprehensive Authentication Barrier Scanner
Scans entire NOUS codebase for ALL authentication barriers preventing public access
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

class AuthBarrierScanner:
    def __init__(self):
        self.barriers = {
            'flask_login_decorators': [],
            'flask_login_imports': [],
            'current_user_references': [],
            'auth_required_decorators': [],
            'redirect_to_login': [],
            'session_checks': [],
            'is_authenticated_checks': [],
            '401_responses': [],
            'authentication_middleware': []
        }
        self.total_files_scanned = 0
        self.problematic_files = set()
        
    def scan_file(self, file_path):
        """Scan a single Python file for authentication barriers"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            self.total_files_scanned += 1
            file_has_issues = False
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # 1. Flask-Login decorators
                if re.search(r'@login_required', line):
                    self.barriers['flask_login_decorators'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 2. Flask-Login imports
                if re.search(r'from flask_login import|import flask_login', line):
                    self.barriers['flask_login_imports'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 3. current_user references
                if re.search(r'current_user\.', line) or re.search(r'current_user\s', line):
                    self.barriers['current_user_references'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 4. Auth required decorators
                if re.search(r'@.*auth.*required|@require_auth', line, re.IGNORECASE):
                    self.barriers['auth_required_decorators'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 5. Redirect to login
                if re.search(r'redirect.*login|url_for.*login', line, re.IGNORECASE):
                    self.barriers['redirect_to_login'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 6. Session authentication checks
                if re.search(r'if.*session.*user|if.*user.*session', line, re.IGNORECASE):
                    self.barriers['session_checks'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 7. is_authenticated checks
                if re.search(r'if.*not.*authenticated|is_authenticated\(\)', line, re.IGNORECASE):
                    self.barriers['is_authenticated_checks'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 8. 401 responses
                if re.search(r'401|unauthorized|authentication.*required', line, re.IGNORECASE):
                    self.barriers['401_responses'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
                
                # 9. Authentication middleware patterns
                if re.search(r'@.*before_request|@.*middleware', line, re.IGNORECASE):
                    self.barriers['authentication_middleware'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line_stripped
                    })
                    file_has_issues = True
            
            if file_has_issues:
                self.problematic_files.add(str(file_path))
                
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    def scan_codebase(self):
        """Scan entire codebase for authentication barriers"""
        print("🔍 COMPREHENSIVE AUTHENTICATION BARRIER SCAN")
        print("=" * 60)
        
        # Scan all Python files
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '__pycache__', '.cache', 'node_modules', '.pytest_cache']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self.scan_file(file_path)
        
        print(f"📊 Scanned {self.total_files_scanned} Python files")
        print(f"🚨 Found {len(self.problematic_files)} files with authentication barriers")
        print()
    
    def generate_report(self):
        """Generate comprehensive report of all authentication barriers"""
        print("🚨 AUTHENTICATION BARRIERS FOUND:")
        print("=" * 60)
        
        total_barriers = 0
        
        for barrier_type, items in self.barriers.items():
            if items:
                count = len(items)
                total_barriers += count
                print(f"\n{barrier_type.upper().replace('_', ' ')}: {count} instances")
                print("-" * 40)
                
                # Group by file for better readability
                files_dict = {}
                for item in items:
                    file_name = item['file']
                    if file_name not in files_dict:
                        files_dict[file_name] = []
                    files_dict[file_name].append(item)
                
                for file_name, file_items in files_dict.items():
                    print(f"📁 {file_name}")
                    for item in file_items[:3]:  # Show first 3 items per file
                        print(f"   Line {item['line']}: {item['content'][:80]}...")
                    if len(file_items) > 3:
                        print(f"   ... and {len(file_items) - 3} more instances")
                    print()
        
        print(f"\n🎯 SUMMARY:")
        print(f"Total authentication barriers found: {total_barriers}")
        print(f"Files requiring fixes: {len(self.problematic_files)}")
        print()
        
        # Priority files (most barriers)
        file_barrier_count = {}
        for barrier_type, items in self.barriers.items():
            for item in items:
                file_name = item['file']
                file_barrier_count[file_name] = file_barrier_count.get(file_name, 0) + 1
        
        print("🔥 TOP PRIORITY FILES (most barriers):")
        print("-" * 40)
        sorted_files = sorted(file_barrier_count.items(), key=lambda x: x[1], reverse=True)
        for file_name, count in sorted_files[:10]:
            print(f"   {count:2d} barriers: {file_name}")
        
        return {
            'total_barriers': total_barriers,
            'problematic_files': len(self.problematic_files),
            'barriers_by_type': {k: len(v) for k, v in self.barriers.items()},
            'top_files': sorted_files[:10],
            'detailed_barriers': self.barriers
        }
    
    def generate_fix_plan(self):
        """Generate specific fix plan for each file"""
        print("\n🔧 AUTHENTICATION FIX PLAN:")
        print("=" * 60)
        
        # Group all barriers by file
        file_issues = {}
        for barrier_type, items in self.barriers.items():
            for item in items:
                file_name = item['file']
                if file_name not in file_issues:
                    file_issues[file_name] = {}
                if barrier_type not in file_issues[file_name]:
                    file_issues[file_name][barrier_type] = []
                file_issues[file_name][barrier_type].append(item)
        
        fix_priority = 1
        for file_name, issues in file_issues.items():
            print(f"\n{fix_priority}. FILE: {file_name}")
            print("   ISSUES FOUND:")
            
            for issue_type, items in issues.items():
                print(f"     - {issue_type.replace('_', ' ').title()}: {len(items)} instances")
            
            print("   RECOMMENDED FIXES:")
            if 'flask_login_imports' in issues:
                print("     ✅ Remove Flask-Login imports")
            if 'flask_login_decorators' in issues:
                print("     ✅ Replace @login_required with session-based auth checks")
            if 'current_user_references' in issues:
                print("     ✅ Replace current_user with session['user']")
            if 'auth_required_decorators' in issues:
                print("     ✅ Add demo mode support to auth decorators")
            if 'redirect_to_login' in issues:
                print("     ✅ Add fallback routes for public access")
            print()
            
            fix_priority += 1
    
    def save_detailed_report(self):
        """Save detailed report to JSON file"""
        report = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_files_scanned': self.total_files_scanned,
            'problematic_files_count': len(self.problematic_files),
            'problematic_files': list(self.problematic_files),
            'barriers_summary': {k: len(v) for k, v in self.barriers.items()},
            'detailed_barriers': self.barriers
        }
        
        with open('auth_barrier_scan_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: auth_barrier_scan_report.json")

def main():
    scanner = AuthBarrierScanner()
    scanner.scan_codebase()
    report_data = scanner.generate_report()
    scanner.generate_fix_plan()
    scanner.save_detailed_report()
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("1. Review the detailed report (auth_barrier_scan_report.json)")
    print("2. Fix files in priority order (highest barrier count first)")
    print("3. Test public access after each file fix")
    print("4. Verify demo mode works without authentication")
    print("="*60)

if __name__ == "__main__":
    main()