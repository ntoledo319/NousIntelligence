#!/usr/bin/env python3
"""
Security Scanner for NOUS Application
Identifies and reports security vulnerabilities
"""

import os
import re
import subprocess
from typing import Dict, List, Any
from datetime import datetime

class SecurityScanner:
    def __init__(self):
        self.issues = []
        self.recommendations = []
        self.score = 100
        
    def scan_hardcoded_secrets(self) -> Dict[str, Any]:
        """Scan for hardcoded secrets and credentials"""
        print("🔍 Scanning for hardcoded secrets...")
        
        secret_patterns = [
            (r'secret.*=.*["\'][^"\']*["\']', 'Secret key assignment'),
            (r'password.*=.*["\'][^"\']*["\']', 'Password assignment'),
            (r'api.*key.*=.*["\'][^"\']*["\']', 'API key assignment'),
            (r'token.*=.*["\'][^"\']*["\']', 'Token assignment'),
            (r'["\'][A-Za-z0-9]{32,}["\']', 'Long string (potential secret)'),
        ]
        
        issues = []
        key_files = ['app.py', 'main.py', 'config.py', 'models.py']
        
        for file_path in key_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        for line_num, line in enumerate(content.split('\n'), 1):
                            for pattern, desc in secret_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    # Skip environment variable usage (safe)
                                    if 'os.environ.get' in line or 'getenv' in line:
                                        continue
                                    issues.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'issue': desc,
                                        'content': line.strip()
                                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        if issues:
            self.score -= 20
            self.issues.extend([f"Hardcoded secret in {i['file']}:{i['line']}" for i in issues])
            
        return {'issues': issues, 'count': len(issues)}
    
    def scan_sql_injection(self) -> Dict[str, Any]:
        """Scan for SQL injection vulnerabilities"""
        print("🔍 Scanning for SQL injection risks...")
        
        sql_patterns = [
            (r'\.execute\s*\([^)]*%[^)]*\)', 'String formatting in SQL'),
            (r'\.execute\s*\([^)]*\+[^)]*\)', 'String concatenation in SQL'),
            (r'\.execute\s*\([^)]*\.format\([^)]*\)', 'Format method in SQL'),
            (r'f["\'].*SELECT.*{.*}.*["\']', 'F-string in SQL query'),
        ]
        
        issues = []
        
        # Check Python files for SQL injection patterns
        try:
            result = subprocess.run(['find', '.', '-name', '*.py', '-type', 'f'], 
                                  capture_output=True, text=True, timeout=10)
            py_files = result.stdout.strip().split('\n')[:20]  # Limit to first 20 files
            
            for file_path in py_files:
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            for line_num, line in enumerate(content.split('\n'), 1):
                                for pattern, desc in sql_patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        issues.append({
                                            'file': file_path,
                                            'line': line_num,
                                            'issue': desc,
                                            'content': line.strip()
                                        })
                    except Exception:
                        continue
        except subprocess.TimeoutExpired:
            print("SQL injection scan timed out, skipping")
        except Exception as e:
            print(f"SQL injection scan error: {e}")
            
        if issues:
            self.score -= 25
            self.issues.extend([f"SQL injection risk in {i['file']}:{i['line']}" for i in issues])
            
        return {'issues': issues, 'count': len(issues)}
    
    def scan_dangerous_functions(self) -> Dict[str, Any]:
        """Scan for dangerous function usage"""
        print("🔍 Scanning for dangerous functions...")
        
        dangerous_functions = ['eval(', 'exec(', 'os.system(', '__import__(']
        issues = []
        
        key_files = ['app.py', 'main.py']
        for file_path in key_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        for line_num, line in enumerate(content.split('\n'), 1):
                            for func in dangerous_functions:
                                if func in line and not line.strip().startswith('#'):
                                    issues.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'function': func,
                                        'content': line.strip()
                                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        if issues:
            self.score -= 30
            self.issues.extend([f"Dangerous function {i['function']} in {i['file']}:{i['line']}" for i in issues])
            
        return {'issues': issues, 'count': len(issues)}
    
    def check_environment_security(self) -> Dict[str, Any]:
        """Check environment and configuration security"""
        print("🔍 Checking environment security...")
        
        issues = []
        
        # Check for required environment variables
        required_env_vars = ['SESSION_SECRET', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
            self.score -= 10
        
        # Check if running in debug mode
        if os.environ.get('FLASK_DEBUG') == '1' or os.environ.get('DEBUG') == 'True':
            issues.append("Debug mode enabled in production")
            self.score -= 15
        
        # Check secret key strength
        session_secret = os.environ.get('SESSION_SECRET', '')
        if session_secret and len(session_secret) < 32:
            issues.append("Session secret is too short (should be 32+ characters)")
            self.score -= 10
            
        self.issues.extend(issues)
        return {'issues': issues, 'count': len(issues)}
    
    def check_security_headers(self) -> Dict[str, Any]:
        """Check if security headers are properly configured"""
        print("🔍 Checking security headers...")
        
        issues = []
        
        # Check if security middleware is imported and used
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                if 'security_middleware' not in content:
                    issues.append("Security middleware not imported")
                    self.score -= 15
                elif 'init_security_headers' not in content:
                    issues.append("Security headers not initialized")
                    self.score -= 10
        except Exception:
            issues.append("Cannot verify security headers configuration")
            self.score -= 10
            
        self.issues.extend(issues)
        return {'issues': issues, 'count': len(issues)}
    
    def generate_recommendations(self):
        """Generate security recommendations"""
        self.recommendations = [
            "Remove hardcoded 'dev-secret-key' fallback from production code",
            "Ensure all SQL queries use parameterized statements",
            "Set strong SESSION_SECRET environment variable (32+ characters)",
            "Disable debug mode in production environment",
            "Implement comprehensive input validation for all endpoints",
            "Add rate limiting to prevent abuse",
            "Enable security headers (CSP, HSTS, X-Frame-Options)",
            "Regular security audits and dependency updates",
            "Implement proper error handling without information disclosure",
            "Use HTTPS in production with proper SSL configuration"
        ]
    
    def run_full_scan(self) -> Dict[str, Any]:
        """Run complete security scan"""
        print(f"🔐 Starting security scan at {datetime.now()}")
        print("=" * 50)
        
        # Run all security checks
        secrets_result = self.scan_hardcoded_secrets()
        sql_result = self.scan_sql_injection()
        dangerous_result = self.scan_dangerous_functions()
        env_result = self.check_environment_security()
        headers_result = self.check_security_headers()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Calculate final score
        final_score = max(0, self.score)
        
        return {
            'security_score': final_score,
            'total_issues': len(self.issues),
            'issues': self.issues,
            'recommendations': self.recommendations,
            'scan_results': {
                'hardcoded_secrets': secrets_result,
                'sql_injection': sql_result,
                'dangerous_functions': dangerous_result,
                'environment': env_result,
                'security_headers': headers_result
            },
            'timestamp': datetime.now().isoformat()
        }

def main():
    scanner = SecurityScanner()
    results = scanner.run_full_scan()
    
    print(f"\n🔐 SECURITY SCAN RESULTS")
    print("=" * 50)
    print(f"Security Score: {results['security_score']}/100")
    print(f"Total Issues: {results['total_issues']}")
    
    if results['issues']:
        print(f"\n⚠️  SECURITY ISSUES:")
        for issue in results['issues']:
            print(f"  • {issue}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in results['recommendations'][:5]:
        print(f"  • {rec}")
        
    # Determine security level
    score = results['security_score']
    if score >= 90:
        print(f"\n✅ Security Level: EXCELLENT")
    elif score >= 75:
        print(f"\n⚠️  Security Level: GOOD")
    elif score >= 60:
        print(f"\n⚠️  Security Level: MODERATE")
    else:
        print(f"\n❌ Security Level: POOR")

if __name__ == '__main__':
    main()