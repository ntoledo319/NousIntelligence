#!/usr/bin/env python3
"""
Verification Script: No Hardcoded Secrets
Scans entire codebase to ensure no hardcoded credentials, API keys, or secrets exist
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class SecretsScanner:
    """Comprehensive scanner for hardcoded secrets in codebase"""
    
    def __init__(self):
        self.suspicious_patterns = [
            # API Keys
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'apikey\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'access[_-]?token\s*=\s*["\'][^"\']+["\']',
            r'auth[_-]?token\s*=\s*["\'][^"\']+["\']',
            
            # OAuth credentials
            r'client[_-]?id\s*=\s*["\'][^"\']+["\']',
            r'client[_-]?secret\s*=\s*["\'][^"\']+["\']',
            r'oauth[_-]?token\s*=\s*["\'][^"\']+["\']',
            
            # Database URLs with credentials
            r'postgresql://[^:\s]+:[^@\s]+@[^/\s]+/[^\s]+',
            r'mysql://[^:\s]+:[^@\s]+@[^/\s]+/[^\s]+',
            
            # JWT secrets
            r'jwt[_-]?secret\s*=\s*["\'][^"\']+["\']',
            r'session[_-]?secret\s*=\s*["\'][^"\']+["\']',
            
            # AWS/Cloud credentials
            r'aws[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            
            # Generic secrets
            r'password\s*=\s*["\'][^"\']+["\']',
            r'pass\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
            
            # Common hardcoded values
            r'["\'][a-zA-Z0-9]{32,}["\']',  # Long alphanumeric strings
        ]
        
        self.safe_patterns = [
            # Environment variable references
            r'os\.environ\.get\(',
            r'os\.getenv\(',
            r'getenv\(',
            r'env\.get\(',
            
            # Configuration patterns
            r'config\.',
            r'settings\.',
            r'from_env\(',
            
            # Placeholder/example patterns
            r'your[_-]?api[_-]?key',
            r'insert[_-]?key[_-]?here',
            r'example[_-]?secret',
            r'placeholder',
            r'<.*>',
            r'\{.*\}',
        ]
        
        self.skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll'}
        self.skip_directories = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'verification'}
        
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for hardcoded secrets"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments (basic detection)
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                    
                for pattern in self.suspicious_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Check if this is a safe pattern
                        is_safe = any(re.search(safe_pattern, line, re.IGNORECASE) 
                                    for safe_pattern in self.safe_patterns)
                        
                        if not is_safe:
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'match': match.group(),
                                'pattern': pattern
                            })
                            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return violations
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan entire directory recursively"""
        all_violations = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_directories]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip certain file extensions
                if file_path.suffix in self.skip_extensions:
                    continue
                    
                violations = self.scan_file(file_path)
                all_violations.extend(violations)
                
        return all_violations
    
    def generate_report(self, violations: List[Dict]) -> Dict:
        """Generate comprehensive report"""
        report = {
            'timestamp': str(Path.cwd()),
            'total_violations': len(violations),
            'violations_by_file': {},
            'violations_by_pattern': {},
            'high_risk_files': [],
            'summary': {}
        }
        
        for violation in violations:
            file_path = violation['file']
            pattern = violation['pattern']
            
            # Group by file
            if file_path not in report['violations_by_file']:
                report['violations_by_file'][file_path] = []
            report['violations_by_file'][file_path].append(violation)
            
            # Group by pattern
            if pattern not in report['violations_by_pattern']:
                report['violations_by_pattern'][pattern] = 0
            report['violations_by_pattern'][pattern] += 1
            
        # Identify high-risk files (multiple violations)
        for file_path, file_violations in report['violations_by_file'].items():
            if len(file_violations) > 3:
                report['high_risk_files'].append({
                    'file': file_path,
                    'violation_count': len(file_violations)
                })
                
        # Generate summary
        report['summary'] = {
            'files_with_violations': len(report['violations_by_file']),
            'most_common_patterns': sorted(
                report['violations_by_pattern'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'status': 'FAIL' if violations else 'PASS'
        }
        
        return report

def main():
    """Main verification function"""
    print("🔍 Starting comprehensive secrets scan...")
    
    scanner = SecretsScanner()
    current_dir = Path.cwd()
    
    # Scan the entire codebase
    violations = scanner.scan_directory(current_dir)
    
    # Generate report
    report = scanner.generate_report(violations)
    
    # Save detailed report
    report_path = Path(__file__).parent / 'secrets_scan_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n📊 Secrets Scan Results:")
    print(f"Total violations found: {report['total_violations']}")
    print(f"Files with violations: {report['summary']['files_with_violations']}")
    print(f"Status: {report['summary']['status']}")
    
    if violations:
        print(f"\n❌ CRITICAL: Hardcoded secrets detected!")
        print(f"Most common violation patterns:")
        for pattern, count in report['summary']['most_common_patterns']:
            print(f"  - {pattern}: {count} occurrences")
            
        print(f"\nHigh-risk files (>3 violations):")
        for risk_file in report['high_risk_files']:
            print(f"  - {risk_file['file']}: {risk_file['violation_count']} violations")
            
        return False
    else:
        print(f"✅ SUCCESS: No hardcoded secrets detected!")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)