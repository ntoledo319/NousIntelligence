#!/usr/bin/env python3
"""
Verification Script: Error Handling
Scans for bare except clauses and improper error handling patterns
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import List, Dict

class ErrorHandlingVerifier:
    """Scans for poor error handling practices"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        
    def verify_error_handling(self) -> Dict:
        """Check for error handling issues"""
        print("🔍 Verifying error handling practices...")
        
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
                
            self._check_file_error_handling(py_file)
        
        return self._generate_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'verification'}
        return any(skip_dir in file_path.parts for skip_dir in skip_dirs)
    
    def _check_file_error_handling(self, file_path: Path):
        """Check error handling in a single file"""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                self._check_bare_except(line, line_num, file_path)
                self._check_broad_except(line, line_num, file_path)
                self._check_pass_in_except(line, line_num, file_path, lines)
                
        except Exception as e:
            self.issues.append({
                'type': 'file_read_error',
                'file': str(file_path),
                'message': f'Could not read file: {e}',
                'severity': 'LOW'
            })
    
    def _check_bare_except(self, line: str, line_num: int, file_path: Path):
        """Check for bare except clauses"""
        if re.search(r'except\s*:', line.strip()):
            self.issues.append({
                'type': 'bare_except',
                'file': str(file_path),
                'line': line_num,
                'content': line.strip(),
                'message': 'Bare except clause - should specify exception type',
                'severity': 'HIGH'
            })
    
    def _check_broad_except(self, line: str, line_num: int, file_path: Path):
        """Check for overly broad except clauses"""
        if re.search(r'except\s+Exception\s*:', line.strip()):
            self.issues.append({
                'type': 'broad_except',
                'file': str(file_path),
                'line': line_num,
                'content': line.strip(),
                'message': 'Broad except Exception - consider specific exceptions',
                'severity': 'MEDIUM'
            })
    
    def _check_pass_in_except(self, line: str, line_num: int, file_path: Path, all_lines: List[str]):
        """Check for pass statements in except blocks without logging"""
        if 'except' in line and line_num < len(all_lines):
            # Look at the next few lines for pass without logging
            for i in range(line_num, min(line_num + 3, len(all_lines))):
                next_line = all_lines[i].strip()
                if next_line == 'pass':
                    # Check if there's logging before the pass
                    has_logging = False
                    for j in range(line_num, i):
                        if any(log_word in all_lines[j] for log_word in ['logger', 'logging', 'print']):
                            has_logging = True
                            break
                    
                    if not has_logging:
                        self.issues.append({
                            'type': 'silent_except',
                            'file': str(file_path),
                            'line': i + 1,
                            'content': next_line,
                            'message': 'Silent exception handling - no logging or error reporting',
                            'severity': 'MEDIUM'
                        })
                    break
    
    def _generate_report(self) -> Dict:
        """Generate error handling verification report"""
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for issue in self.issues:
            severity_counts[issue['severity']] += 1
        
        report = {
            'timestamp': str(self.project_root),
            'total_issues': len(self.issues),
            'severity_breakdown': severity_counts,
            'issues': self.issues,
            'status': 'FAIL' if self.issues else 'PASS',
            'quality_score': max(0, 100 - (severity_counts['HIGH'] * 10) - (severity_counts['MEDIUM'] * 5) - severity_counts['LOW']),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for fixing error handling"""
        recommendations = []
        
        if any(issue['type'] == 'bare_except' for issue in self.issues):
            recommendations.append("Replace bare except: clauses with specific exception types")
        
        if any(issue['type'] == 'broad_except' for issue in self.issues):
            recommendations.append("Replace broad Exception catches with specific exception types")
        
        if any(issue['type'] == 'silent_except' for issue in self.issues):
            recommendations.append("Add logging to exception handlers to aid debugging")
        
        if not recommendations:
            recommendations.append("Error handling practices are acceptable")
        
        return recommendations

def main():
    """Main verification function"""
    verifier = ErrorHandlingVerifier()
    report = verifier.verify_error_handling()
    
    # Save report
    report_path = Path(__file__).parent / 'error_handling_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print results
    print(f"\n📊 Error Handling Verification Results:")
    print(f"Total issues: {report['total_issues']}")
    print(f"High: {report['severity_breakdown']['HIGH']}")
    print(f"Medium: {report['severity_breakdown']['MEDIUM']}")
    print(f"Low: {report['severity_breakdown']['LOW']}")
    print(f"Quality Score: {report['quality_score']}/100")
    print(f"Status: {report['status']}")
    
    if report['total_issues'] > 0:
        print(f"\nTop issues found:")
        for issue in report['issues'][:5]:
            print(f"  - {issue['message']} ({issue['file']}:{issue.get('line', '?')})")
        
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
        
        return False
    else:
        print(f"✅ Error handling verification passed!")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)