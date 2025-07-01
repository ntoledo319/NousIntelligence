#!/usr/bin/env python3
"""
Comprehensive Security Audit for NOUS Application
Performs thorough security analysis including code review, dependency checks, and configuration validation
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class ComprehensiveSecurityAudit:
    def __init__(self):
        self.security_score = 100
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
        self.recommendations = []
        
    def audit_environment_variables(self) -> Dict[str, Any]:
        """Audit environment variable security"""
        print("🔍 Auditing environment variables...")
        
        issues = []
        
        # Critical environment variables
        critical_vars = {
            'SESSION_SECRET': 'Session encryption key',
            'DATABASE_URL': 'Database connection string',
            'GOOGLE_CLIENT_ID': 'OAuth client ID',
            'GOOGLE_CLIENT_SECRET': 'OAuth client secret'
        }
        
        missing_critical = []
        weak_secrets = []
        
        for var, desc in critical_vars.items():
            value = os.environ.get(var)
            if not value:
                missing_critical.append(f"{var} ({desc})")
            elif var in ['SESSION_SECRET', 'GOOGLE_CLIENT_SECRET'] and len(value) < 32:
                weak_secrets.append(f"{var} is too short (< 32 characters)")
        
        if missing_critical:
            issues.append(f"Missing critical environment variables: {', '.join(missing_critical)}")
            self.critical_issues.extend(missing_critical)
            self.security_score -= 30
            
        if weak_secrets:
            issues.append(f"Weak secrets: {', '.join(weak_secrets)}")
            self.medium_issues.extend(weak_secrets)
            self.security_score -= 15
            
        # Check for debug mode in production
        if os.environ.get('FLASK_DEBUG') == '1' or os.environ.get('DEBUG') == 'True':
            issues.append("Debug mode enabled - security risk in production")
            self.high_issues.append("Debug mode enabled")
            self.security_score -= 20
            
        return {
            'issues': issues,
            'missing_critical': missing_critical,
            'weak_secrets': weak_secrets,
            'score_impact': 100 - self.security_score if issues else 0
        }
    
    def audit_code_security(self) -> Dict[str, Any]:
        """Audit code for security vulnerabilities"""
        print("🔍 Auditing code security...")
        
        issues = []
        
        # Check critical files
        critical_files = ['app.py', 'main.py', 'models.py']
        
        for file_path in critical_files:
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Check for hardcoded secrets
                secret_patterns = [
                    (r'["\'][A-Za-z0-9]{32,}["\']', 'Potential hardcoded secret'),
                    (r'password\s*=\s*["\'][^"\']*["\']', 'Hardcoded password'),
                    (r'secret\s*=\s*["\'][^"\']*["\']', 'Hardcoded secret'),
                    (r'api_key\s*=\s*["\'][^"\']*["\']', 'Hardcoded API key'),
                ]
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern, desc in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip safe patterns
                            if any(safe in line for safe in ['os.environ', 'getenv', 'config', 'SECRET_KEY']):
                                continue
                            issues.append(f"{file_path}:{line_num} - {desc}")
                            self.high_issues.append(f"Hardcoded secret in {file_path}")
                            self.security_score -= 25
                            
                # Check for SQL injection patterns
                sql_patterns = [
                    (r'\.execute\s*\([^)]*%[^)]*\)', 'String formatting in SQL'),
                    (r'\.execute\s*\([^)]*\+[^)]*\)', 'String concatenation in SQL'),
                    (r'f["\'].*SELECT.*{.*}.*["\']', 'F-string in SQL query'),
                ]
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern, desc in sql_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(f"{file_path}:{line_num} - {desc}")
                            self.high_issues.append(f"SQL injection risk in {file_path}")
                            self.security_score -= 20
                            
                # Check for dangerous functions
                dangerous_functions = ['eval(', 'exec(', 'os.system(', '__import__(']
                for line_num, line in enumerate(content.split('\n'), 1):
                    for func in dangerous_functions:
                        if func in line and not line.strip().startswith('#'):
                            issues.append(f"{file_path}:{line_num} - Dangerous function {func}")
                            self.critical_issues.append(f"Dangerous function {func} in {file_path}")
                            self.security_score -= 30
                            
            except Exception as e:
                issues.append(f"Error reading {file_path}: {e}")
                
        return {
            'issues': issues,
            'files_checked': critical_files,
            'score_impact': len([i for i in issues if 'Dangerous function' in i]) * 30 + 
                           len([i for i in issues if 'SQL injection' in i]) * 20 +
                           len([i for i in issues if 'Hardcoded' in i]) * 25
        }
    
    def audit_dependencies(self) -> Dict[str, Any]:
        """Audit dependencies for security vulnerabilities"""
        print("🔍 Auditing dependencies...")
        
        issues = []
        
        # Check if pyproject.toml exists
        if os.path.exists('pyproject.toml'):
            try:
                with open('pyproject.toml', 'r') as f:
                    content = f.read()
                    
                # Check for unpinned dependencies (security risk)
                unpinned_deps = []
                for line in content.split('\n'):
                    if '=' in line and '"' in line and not ('==' in line or '>=' in line or '<=' in line):
                        dep_match = re.search(r'"([^"]+)"', line)
                        if dep_match:
                            unpinned_deps.append(dep_match.group(1))
                            
                if unpinned_deps:
                    issues.append(f"Unpinned dependencies: {', '.join(unpinned_deps[:5])}")
                    self.medium_issues.extend(unpinned_deps[:5])
                    self.security_score -= 10
                    
            except Exception as e:
                issues.append(f"Error reading pyproject.toml: {e}")
                
        return {
            'issues': issues,
            'recommendations': ['Pin all dependency versions', 'Regular security updates']
        }
    
    def audit_configuration(self) -> Dict[str, Any]:
        """Audit configuration security"""
        print("🔍 Auditing configuration...")
        
        issues = []
        
        # Check Flask configuration
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
                # Check for debug mode
                if 'DEBUG = True' in content:
                    issues.append("Debug mode enabled in app.py")
                    self.high_issues.append("Debug mode in code")
                    self.security_score -= 20
                    
                # Check for proper security headers
                if 'Content-Security-Policy' not in content:
                    issues.append("Content Security Policy not configured")
                    self.medium_issues.append("Missing CSP")
                    self.security_score -= 10
                    
                # Check for HTTPS enforcement
                if 'FORCE_HTTPS' not in content and 'force_https' not in content:
                    issues.append("HTTPS enforcement not configured")
                    self.medium_issues.append("Missing HTTPS enforcement")
                    self.security_score -= 10
                    
        except Exception as e:
            issues.append(f"Error reading app.py: {e}")
            
        return {
            'issues': issues,
            'recommendations': ['Enable HTTPS enforcement', 'Configure CSP headers', 'Disable debug in production']
        }
    
    def audit_authentication(self) -> Dict[str, Any]:
        """Audit authentication security"""
        print("🔍 Auditing authentication...")
        
        issues = []
        
        # Check for proper session configuration
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
                # Check session configuration
                if 'SESSION_COOKIE_SECURE' not in content:
                    issues.append("Session cookies not configured as secure")
                    self.medium_issues.append("Insecure session cookies")
                    self.security_score -= 10
                    
                if 'SESSION_COOKIE_HTTPONLY' not in content:
                    issues.append("Session cookies not HTTPOnly")
                    self.medium_issues.append("Session cookies not HTTPOnly")
                    self.security_score -= 10
                    
                # Check for proper OAuth implementation
                if 'google_oauth' in content.lower():
                    if 'csrf' not in content.lower():
                        issues.append("CSRF protection not implemented for OAuth")
                        self.high_issues.append("Missing CSRF protection")
                        self.security_score -= 20
                        
        except Exception as e:
            issues.append(f"Error reading app.py: {e}")
            
        return {
            'issues': issues,
            'recommendations': ['Configure secure session cookies', 'Implement CSRF protection', 'Add rate limiting']
        }
    
    def generate_recommendations(self):
        """Generate security recommendations based on findings"""
        base_recommendations = [
            "Implement comprehensive input validation for all endpoints",
            "Add rate limiting to prevent abuse and DoS attacks",
            "Enable security headers (CSP, HSTS, X-Frame-Options)",
            "Configure secure session cookies (Secure, HTTPOnly, SameSite)",
            "Implement proper error handling without information disclosure",
            "Regular security audits and dependency updates",
            "Use HTTPS in production with proper SSL configuration",
            "Implement comprehensive logging for security monitoring",
            "Add CSRF protection for all state-changing operations",
            "Configure proper CORS policies for API endpoints"
        ]
        
        # Add specific recommendations based on findings
        if self.critical_issues:
            self.recommendations.insert(0, "CRITICAL: Address all critical security issues immediately")
        if self.high_issues:
            self.recommendations.insert(0 if not self.critical_issues else 1, "HIGH PRIORITY: Fix high-severity security issues")
            
        self.recommendations.extend(base_recommendations)
        
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        print("🔐 Starting comprehensive security audit...")
        print("=" * 60)
        
        # Run all audit components
        env_audit = self.audit_environment_variables()
        code_audit = self.audit_code_security()
        deps_audit = self.audit_dependencies()
        config_audit = self.audit_configuration()
        auth_audit = self.audit_authentication()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Calculate final score
        final_score = max(0, self.security_score)
        
        # Determine security level
        if final_score >= 90:
            security_level = "EXCELLENT"
            level_color = "✅"
        elif final_score >= 75:
            security_level = "GOOD"
            level_color = "🟢"
        elif final_score >= 60:
            security_level = "MODERATE"
            level_color = "🟡"
        else:
            security_level = "POOR"
            level_color = "❌"
            
        return {
            'security_score': final_score,
            'security_level': security_level,
            'level_color': level_color,
            'total_issues': len(self.critical_issues) + len(self.high_issues) + len(self.medium_issues) + len(self.low_issues),
            'critical_issues': self.critical_issues,
            'high_issues': self.high_issues,
            'medium_issues': self.medium_issues,
            'low_issues': self.low_issues,
            'recommendations': self.recommendations[:10],  # Top 10 recommendations
            'audit_results': {
                'environment': env_audit,
                'code_security': code_audit,
                'dependencies': deps_audit,
                'configuration': config_audit,
                'authentication': auth_audit
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def save_audit_report(self, results: Dict[str, Any], filename: str = None):
        """Save audit report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_audit_report_{timestamp}.json"
            
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"📄 Audit report saved to {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")

def main():
    """Run comprehensive security audit"""
    auditor = ComprehensiveSecurityAudit()
    results = auditor.run_comprehensive_audit()
    
    # Display results
    print(f"\n🔐 COMPREHENSIVE SECURITY AUDIT RESULTS")
    print("=" * 60)
    print(f"Security Score: {results['security_score']}/100")
    print(f"Security Level: {results['level_color']} {results['security_level']}")
    print(f"Total Issues: {results['total_issues']}")
    
    if results['critical_issues']:
        print(f"\n🚨 CRITICAL ISSUES ({len(results['critical_issues'])}):")
        for issue in results['critical_issues']:
            print(f"  • {issue}")
    
    if results['high_issues']:
        print(f"\n⚠️  HIGH PRIORITY ISSUES ({len(results['high_issues'])}):")
        for issue in results['high_issues']:
            print(f"  • {issue}")
    
    if results['medium_issues']:
        print(f"\n🟡 MEDIUM PRIORITY ISSUES ({len(results['medium_issues'])}):")
        for issue in results['medium_issues'][:5]:  # Show first 5
            print(f"  • {issue}")
    
    print(f"\n💡 TOP SECURITY RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'][:8], 1):
        print(f"  {i}. {rec}")
    
    # Save report
    auditor.save_audit_report(results)
    
    return results

if __name__ == '__main__':
    main()