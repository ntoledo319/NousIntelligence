#!/usr/bin/env python3
"""
Comprehensive Authentication Barrier Scanner
Scans entire NOUS codebase for ALL authentication barriers preventing public access
"""

import os
import re
from pathlib import Path
import json

class AuthBarrierScanner:
    def __init__(self):
        self.barriers_found = []
        self.files_scanned = 0
        self.authentication_patterns = [
            # Flask-Login patterns
            r'@login_required',
            r'from flask_login import.*login_required',
            r'login_required\(',
            r'current_user\.',
            r'if not current_user',
            r'current_user\.is_authenticated',
            
            # Session-based auth barriers
            r'if.*not.*session\[.*user.*\]',
            r'if.*session\.get\(.*user.*\).*is None',
            r'return redirect.*login',
            r'abort\(401\)',
            r'abort\(403\)',
            
            # Custom auth decorators
            r'@require_auth',
            r'@authenticated',
            r'@auth_required',
            r'@login_required',
            
            # Auth check functions that block access
            r'def.*require.*authentication',
            r'def.*check.*auth',
            r'def.*verify.*login',
            
            # Error messages indicating auth barriers
            r'["\']You must be logged in',
            r'["\']Please log in',
            r'["\']Authentication required',
            r'["\']Access denied',
            r'["\']Unauthorized',
            
            # Redirect patterns
            r'redirect.*login',
            r'url_for.*login',
            
            # JWT patterns
            r'@jwt_required',
            r'verify_jwt_in_request',
            r'get_jwt_identity',
        ]
    
    def scan_file(self, file_path):
        """Scan a single Python file for authentication barriers"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            file_barriers = []
            
            for i, line in enumerate(lines, 1):
                for pattern in self.authentication_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        barrier = {
                            'file': str(file_path),
                            'line_number': i,
                            'line_content': line.strip(),
                            'pattern': pattern,
                            'severity': self._assess_severity(pattern, line)
                        }
                        file_barriers.append(barrier)
            
            return file_barriers
            
        except Exception as e:
            return [{'file': str(file_path), 'error': str(e)}]
    
    def _assess_severity(self, pattern, line):
        """Assess the severity of an authentication barrier"""
        # Critical barriers that completely block access
        if any(p in pattern for p in ['@login_required', 'abort(401)', 'abort(403)']):
            return 'CRITICAL'
        
        # High severity - likely to cause access issues
        if any(p in pattern for p in ['redirect.*login', 'You must be logged in']):
            return 'HIGH'
        
        # Medium severity - conditional access
        if any(p in pattern for p in ['if.*not.*session', 'current_user']):
            return 'MEDIUM'
        
        # Low severity - informational or fallback
        return 'LOW'
    
    def scan_codebase(self):
        """Scan entire codebase for authentication barriers"""
        print("🔍 Scanning entire NOUS codebase for authentication barriers...")
        
        # Scan all Python files
        for root, dirs, files in os.walk('.'):
            # Skip cache and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self.files_scanned += 1
                    
                    barriers = self.scan_file(file_path)
                    self.barriers_found.extend(barriers)
        
        print(f"📊 Scanned {self.files_scanned} Python files")
        print(f"🚨 Found {len(self.barriers_found)} potential authentication barriers")
        
    def generate_report(self):
        """Generate comprehensive report of all authentication barriers"""
        
        # Categorize barriers by severity
        critical_barriers = [b for b in self.barriers_found if b.get('severity') == 'CRITICAL']
        high_barriers = [b for b in self.barriers_found if b.get('severity') == 'HIGH']
        medium_barriers = [b for b in self.barriers_found if b.get('severity') == 'MEDIUM']
        low_barriers = [b for b in self.barriers_found if b.get('severity') == 'LOW']
        
        # Group by file
        files_with_barriers = {}
        for barrier in self.barriers_found:
            file_path = barrier.get('file', 'unknown')
            if file_path not in files_with_barriers:
                files_with_barriers[file_path] = []
            files_with_barriers[file_path].append(barrier)
        
        report = f"""
# COMPREHENSIVE AUTHENTICATION BARRIER REPORT
Generated: {os.popen('date').read().strip()}

## EXECUTIVE SUMMARY
- Files Scanned: {self.files_scanned}
- Total Barriers Found: {len(self.barriers_found)}
- Critical Barriers: {len(critical_barriers)}
- High Priority Barriers: {len(high_barriers)}
- Medium Priority Barriers: {len(medium_barriers)}
- Low Priority Barriers: {len(low_barriers)}
- Files Affected: {len(files_with_barriers)}

## CRITICAL BARRIERS (Immediate Fix Required)
"""
        
        for barrier in critical_barriers:
            report += f"""
### {barrier.get('file', 'Unknown File')}
- Line {barrier.get('line_number', '?')}: `{barrier.get('line_content', 'N/A')}`
- Pattern: {barrier.get('pattern', 'N/A')}
"""

        report += f"""
## HIGH PRIORITY BARRIERS
"""
        
        for barrier in high_barriers:
            report += f"""
### {barrier.get('file', 'Unknown File')}
- Line {barrier.get('line_number', '?')}: `{barrier.get('line_content', 'N/A')}`
- Pattern: {barrier.get('pattern', 'N/A')}
"""

        report += f"""
## FILES REQUIRING ATTENTION
"""
        
        for file_path, barriers in files_with_barriers.items():
            if any(b.get('severity') in ['CRITICAL', 'HIGH'] for b in barriers):
                report += f"""
### {file_path}
- Total barriers: {len(barriers)}
- Critical/High: {len([b for b in barriers if b.get('severity') in ['CRITICAL', 'HIGH']])}
"""

        return report
    
    def generate_fix_plan(self):
        """Generate specific fix plan for each file"""
        fix_plan = {
            'files_to_fix': [],
            'recommended_actions': [],
            'batch_operations': []
        }
        
        # Group barriers by file for batch processing
        files_with_critical = {}
        for barrier in self.barriers_found:
            if barrier.get('severity') in ['CRITICAL', 'HIGH']:
                file_path = barrier.get('file')
                if file_path not in files_with_critical:
                    files_with_critical[file_path] = []
                files_with_critical[file_path].append(barrier)
        
        for file_path, barriers in files_with_critical.items():
            fix_plan['files_to_fix'].append({
                'file': file_path,
                'barriers_count': len(barriers),
                'actions': [
                    'Replace @login_required with session-based auth checks',
                    'Replace current_user with get_current_user() from auth_compat',
                    'Add demo mode support',
                    'Replace authentication redirects with graceful fallbacks'
                ]
            })
        
        # Batch operations
        fix_plan['batch_operations'] = [
            'Mass replace @login_required decorators',
            'Update current_user references',
            'Add demo mode support to all routes',
            'Update authentication compatibility layer'
        ]
        
        return fix_plan
    
    def save_detailed_report(self):
        """Save detailed report to JSON file"""
        report_data = {
            'scan_summary': {
                'files_scanned': self.files_scanned,
                'total_barriers': len(self.barriers_found),
                'critical_barriers': len([b for b in self.barriers_found if b.get('severity') == 'CRITICAL']),
                'high_barriers': len([b for b in self.barriers_found if b.get('severity') == 'HIGH']),
                'medium_barriers': len([b for b in self.barriers_found if b.get('severity') == 'MEDIUM']),
                'low_barriers': len([b for b in self.barriers_found if b.get('severity') == 'LOW'])
            },
            'all_barriers': self.barriers_found,
            'fix_plan': self.generate_fix_plan()
        }
        
        with open('AUTHENTICATION_BARRIERS_COMPLETE_REPORT.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_data

def main():
    scanner = AuthBarrierScanner()
    
    print("🚀 COMPREHENSIVE AUTHENTICATION BARRIER SCAN")
    print("=" * 60)
    
    scanner.scan_codebase()
    
    # Generate reports
    text_report = scanner.generate_report()
    json_report = scanner.save_detailed_report()
    
    # Save text report
    with open('AUTHENTICATION_BARRIERS_COMPLETE_REPORT.md', 'w') as f:
        f.write(text_report)
    
    print("\n📋 SCAN COMPLETE!")
    print(f"✅ Text Report: AUTHENTICATION_BARRIERS_COMPLETE_REPORT.md")
    print(f"✅ JSON Report: AUTHENTICATION_BARRIERS_COMPLETE_REPORT.json")
    print(f"🔧 Fix Plan: {len(json_report['fix_plan']['files_to_fix'])} files need fixes")
    
    # Show critical summary
    critical_count = json_report['scan_summary']['critical_barriers']
    high_count = json_report['scan_summary']['high_barriers']
    
    if critical_count > 0 or high_count > 0:
        print(f"\n🚨 URGENT ACTION REQUIRED:")
        print(f"   - {critical_count} CRITICAL barriers")
        print(f"   - {high_count} HIGH priority barriers")
        print(f"   - These will cause 'You must be logged in' errors")
    else:
        print(f"\n✅ NO CRITICAL BARRIERS FOUND!")
        print(f"   - Application should allow public access")

if __name__ == "__main__":
    main()