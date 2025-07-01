#!/usr/bin/env python3
"""
Verification Script: SQL Security
Scans codebase for SQL injection vulnerabilities and validates secure practices
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Set

class SQLSecurityScanner:
    """Comprehensive scanner for SQL injection vulnerabilities"""
    
    def __init__(self):
        self.vulnerable_patterns = [
            # String concatenation in queries
            r'\.execute\s*\([^)]*\+[^)]*\)',
            r'\.execute\s*\([^)]*%[^)]*\)',
            r'\.execute\s*\([^)]*\.format\([^)]*\)\)',
            
            # F-strings with user input
            r'f["\'][^"\']*SELECT[^"\']*\{[^}]*\}[^"\']*["\']',
            r'f["\'][^"\']*INSERT[^"\']*\{[^}]*\}[^"\']*["\']',
            r'f["\'][^"\']*UPDATE[^"\']*\{[^}]*\}[^"\']*["\']',
            r'f["\'][^"\']*DELETE[^"\']*\{[^}]*\}[^"\']*["\']',
            
            # Raw SQL with variable substitution
            r'["\'][^"\']*SELECT[^"\']*%s[^"\']*["\']',
            r'["\'][^"\']*INSERT[^"\']*%s[^"\']*["\']',
            r'["\'][^"\']*UPDATE[^"\']*%s[^"\']*["\']',
            r'["\'][^"\']*DELETE[^"\']*%s[^"\']*["\']',
            
            # Direct cursor.execute with variables
            r'cursor\.execute\s*\([^)]*,',
            r'db\.execute\s*\([^)]*,',
            
            # Potentially unsafe SQLAlchemy text() usage
            r'text\s*\([^)]*\+[^)]*\)',
            r'text\s*\(f["\'][^"\']*\{[^}]*\}[^"\']*["\']',
        ]
        
        self.safe_patterns = [
            # Parameterized queries (safe patterns)
            r'\.execute\s*\([^)]*,\s*\([^)]*\)\)',  # execute(query, params)
            r'\.execute\s*\([^)]*,\s*\{[^}]*\}\)',  # execute(query, dict_params)
            r'query\.filter\(',  # SQLAlchemy ORM filters
            r'session\.query\(',  # SQLAlchemy session queries
            r'\.filter_by\(',  # SQLAlchemy filter_by
            r'\.where\(',  # SQLAlchemy where clauses
            
            # Constants and safe string literals
            r'["\'][^"\']*SELECT[^"\']*["\'](?!\s*\+|\s*%|\s*\.format)',
            r'text\s*\(["\'][^"\']*["\']\s*\)',  # SQLAlchemy text with string literal
        ]
        
        self.skip_directories = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'verification'}
        
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                    
                for pattern in self.vulnerable_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Check if this matches a safe pattern
                        is_safe = any(re.search(safe_pattern, line, re.IGNORECASE) 
                                    for safe_pattern in self.safe_patterns)
                        
                        if not is_safe:
                            vulnerabilities.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'match': match.group(),
                                'pattern': pattern,
                                'severity': self._assess_severity(line, pattern)
                            })
                            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return vulnerabilities
    
    def _assess_severity(self, line: str, pattern: str) -> str:
        """Assess the severity of the SQL injection vulnerability"""
        # High severity indicators
        high_severity_keywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER']
        
        # User input indicators
        user_input_patterns = ['request.', 'form.', 'args.', 'json.', 'data.']
        
        line_upper = line.upper()
        has_high_risk_sql = any(keyword in line_upper for keyword in high_severity_keywords)
        has_user_input = any(pattern in line for pattern in user_input_patterns)
        
        if has_high_risk_sql and has_user_input:
            return 'CRITICAL'
        elif has_high_risk_sql or has_user_input:
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan entire directory recursively for SQL vulnerabilities"""
        all_vulnerabilities = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_directories]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    vulnerabilities = self.scan_file(file_path)
                    all_vulnerabilities.extend(vulnerabilities)
                    
        return all_vulnerabilities
    
    def generate_report(self, vulnerabilities: List[Dict]) -> Dict:
        """Generate comprehensive SQL security report"""
        report = {
            'timestamp': str(Path.cwd()),
            'total_vulnerabilities': len(vulnerabilities),
            'vulnerabilities_by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0},
            'vulnerabilities_by_file': {},
            'critical_files': [],
            'recommendations': [],
            'summary': {}
        }
        
        for vuln in vulnerabilities:
            severity = vuln['severity']
            file_path = vuln['file']
            
            # Count by severity
            report['vulnerabilities_by_severity'][severity] += 1
            
            # Group by file
            if file_path not in report['vulnerabilities_by_file']:
                report['vulnerabilities_by_file'][file_path] = []
            report['vulnerabilities_by_file'][file_path].append(vuln)
            
            # Track critical files
            if severity == 'CRITICAL':
                if file_path not in [f['file'] for f in report['critical_files']]:
                    report['critical_files'].append({
                        'file': file_path,
                        'critical_count': sum(1 for v in report['vulnerabilities_by_file'][file_path] 
                                            if v['severity'] == 'CRITICAL')
                    })
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(vulnerabilities)
        
        # Generate summary
        report['summary'] = {
            'files_with_vulnerabilities': len(report['vulnerabilities_by_file']),
            'critical_vulnerabilities': report['vulnerabilities_by_severity']['CRITICAL'],
            'high_vulnerabilities': report['vulnerabilities_by_severity']['HIGH'],
            'status': 'FAIL' if vulnerabilities else 'PASS',
            'security_score': self._calculate_security_score(vulnerabilities)
        }
        
        return report
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Generate security recommendations based on found vulnerabilities"""
        recommendations = []
        
        if vulnerabilities:
            recommendations.extend([
                "Replace all string concatenation in SQL queries with parameterized queries",
                "Use SQLAlchemy ORM methods instead of raw SQL where possible",
                "Implement input validation and sanitization for all user inputs",
                "Use prepared statements for all database operations",
                "Add SQL injection tests to your test suite",
                "Consider using query builders with automatic escaping",
                "Implement database access logging and monitoring"
            ])
        
        return recommendations
    
    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> int:
        """Calculate security score (0-100, higher is better)"""
        if not vulnerabilities:
            return 100
        
        # Weighted scoring based on severity
        critical_weight = 20
        high_weight = 10
        medium_weight = 5
        
        total_penalty = 0
        for vuln in vulnerabilities:
            if vuln['severity'] == 'CRITICAL':
                total_penalty += critical_weight
            elif vuln['severity'] == 'HIGH':
                total_penalty += high_weight
            else:
                total_penalty += medium_weight
        
        # Cap at 0 minimum
        score = max(0, 100 - total_penalty)
        return score

def main():
    """Main verification function"""
    print("🔍 Starting SQL security vulnerability scan...")
    
    scanner = SQLSecurityScanner()
    current_dir = Path.cwd()
    
    # Scan the entire codebase
    vulnerabilities = scanner.scan_directory(current_dir)
    
    # Generate report
    report = scanner.generate_report(vulnerabilities)
    
    # Save detailed report
    report_path = Path(__file__).parent / 'sql_security_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n📊 SQL Security Scan Results:")
    print(f"Total vulnerabilities found: {report['total_vulnerabilities']}")
    print(f"Critical: {report['vulnerabilities_by_severity']['CRITICAL']}")
    print(f"High: {report['vulnerabilities_by_severity']['HIGH']}")
    print(f"Medium: {report['vulnerabilities_by_severity']['MEDIUM']}")
    print(f"Security Score: {report['summary']['security_score']}/100")
    print(f"Status: {report['summary']['status']}")
    
    if vulnerabilities:
        print(f"\n❌ CRITICAL: SQL injection vulnerabilities detected!")
        
        if report['critical_files']:
            print(f"\nCritical files requiring immediate attention:")
            for critical_file in report['critical_files']:
                print(f"  - {critical_file['file']}: {critical_file['critical_count']} critical vulnerabilities")
        
        print(f"\nRecommendations:")
        for rec in report['recommendations'][:5]:  # Show top 5 recommendations
            print(f"  - {rec}")
            
        return False
    else:
        print(f"✅ SUCCESS: No SQL injection vulnerabilities detected!")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)