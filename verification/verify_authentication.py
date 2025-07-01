#!/usr/bin/env python3
"""
Verification Script: Authentication System
Validates authentication implementation and security
"""

import os
import re
import json
import importlib
from pathlib import Path
from typing import List, Dict, Set

class AuthenticationVerifier:
    """Comprehensive authentication system verifier"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.critical_issues = []
        
    def verify_authentication_system(self) -> Dict:
        """Run all authentication verifications"""
        print("🔍 Verifying authentication system...")
        
        # Check for duplicate auth implementations
        self._check_duplicate_auth_implementations()
        
        # Check JWT implementation
        self._check_jwt_implementation()
        
        # Check OAuth implementation
        self._check_oauth_implementation()
        
        # Check endpoint security
        self._check_endpoint_security()
        
        # Check session management
        self._check_session_management()
        
        return self._generate_report()
    
    def _check_duplicate_auth_implementations(self):
        """Check for multiple conflicting auth implementations"""
        auth_files = [
            'utils/jwt_auth.py',
            'utils/enhanced_auth_service.py',
            'utils/secure_jwt_auth.py',
            'utils/simple_auth.py',
            'utils/auth_compat.py'
        ]
        
        existing_auth_files = []
        for auth_file in auth_files:
            if (self.project_root / auth_file).exists():
                existing_auth_files.append(auth_file)
        
        if len(existing_auth_files) > 2:  # Allow maximum 2 auth files
            self.critical_issues.append({
                'type': 'duplicate_auth',
                'message': f"Multiple auth implementations found: {existing_auth_files}",
                'files': existing_auth_files,
                'severity': 'CRITICAL'
            })
    
    def _check_jwt_implementation(self):
        """Check JWT implementation for security issues"""
        jwt_files = [f for f in Path('utils').glob('*jwt*.py') if f.exists()]
        
        for jwt_file in jwt_files:
            try:
                content = jwt_file.read_text()
                
                # Check for proper JWT library usage
                if 'import jwt' in content:
                    # Check for proper error handling
                    if 'ExpiredSignatureError' not in content:
                        self.issues.append({
                            'type': 'jwt_error_handling',
                            'file': str(jwt_file),
                            'message': 'Missing JWT ExpiredSignatureError handling',
                            'severity': 'HIGH'
                        })
                    
                    # Check for proper token validation
                    if 'verify_exp' not in content and 'verify_iat' not in content:
                        self.issues.append({
                            'type': 'jwt_validation',
                            'file': str(jwt_file),
                            'message': 'Missing proper JWT token validation',
                            'severity': 'HIGH'
                        })
                
                # Check for hardcoded secrets in JWT
                if re.search(r'secret.*=.*["\'][^"\']{1,31}["\']', content, re.IGNORECASE):
                    self.critical_issues.append({
                        'type': 'hardcoded_secret',
                        'file': str(jwt_file),
                        'message': 'Hardcoded JWT secret detected',
                        'severity': 'CRITICAL'
                    })
                    
            except Exception as e:
                self.issues.append({
                    'type': 'file_error',
                    'file': str(jwt_file),
                    'message': f'Error reading JWT file: {e}',
                    'severity': 'MEDIUM'
                })
    
    def _check_oauth_implementation(self):
        """Check OAuth implementation security"""
        oauth_file = Path('utils/google_oauth.py')
        
        if oauth_file.exists():
            try:
                content = oauth_file.read_text()
                
                # Check for proper environment variable usage
                if 'GOOGLE_CLIENT_ID' not in content or 'GOOGLE_CLIENT_SECRET' not in content:
                    self.issues.append({
                        'type': 'oauth_config',
                        'file': str(oauth_file),
                        'message': 'OAuth credentials not properly configured from environment',
                        'severity': 'HIGH'
                    })
                
                # Check for hardcoded OAuth credentials
                if re.search(r'client_id.*=.*["\'][^"\']+["\']', content) and 'environ' not in content:
                    self.critical_issues.append({
                        'type': 'hardcoded_oauth',
                        'file': str(oauth_file),
                        'message': 'Hardcoded OAuth credentials detected',
                        'severity': 'CRITICAL'
                    })
                    
            except Exception as e:
                self.issues.append({
                    'type': 'oauth_error',
                    'file': str(oauth_file),
                    'message': f'Error checking OAuth file: {e}',
                    'severity': 'MEDIUM'
                })
    
    def _check_endpoint_security(self):
        """Check if endpoints are properly secured"""
        route_files = list(Path('routes').glob('*.py'))
        
        unsecured_endpoints = []
        
        for route_file in route_files:
            try:
                content = route_file.read_text()
                
                # Look for route definitions
                route_patterns = re.findall(r'@[^.]+\.route\([^)]+\)', content)
                
                for route_pattern in route_patterns:
                    # Check if route has authentication
                    route_start = content.find(route_pattern)
                    route_end = content.find('\ndef ', route_start + 1)
                    if route_end == -1:
                        route_end = len(content)
                    
                    route_section = content[route_start:route_end]
                    
                    # Check for authentication decorators
                    auth_patterns = [
                        '@login_required',
                        '@token_required',
                        '@require_auth',
                        '@jwt_required'
                    ]
                    
                    has_auth = any(pattern in route_section for pattern in auth_patterns)
                    
                    # Skip public endpoints
                    public_endpoints = ['/health', '/demo', '/public', '/static', '/']
                    is_public = any(endpoint in route_pattern for endpoint in public_endpoints)
                    
                    if not has_auth and not is_public and 'POST' in route_section:
                        unsecured_endpoints.append({
                            'file': str(route_file),
                            'route': route_pattern,
                            'type': 'unsecured_endpoint'
                        })
                        
            except Exception as e:
                continue
        
        if unsecured_endpoints:
            self.issues.append({
                'type': 'unsecured_endpoints',
                'message': f'Found {len(unsecured_endpoints)} potentially unsecured endpoints',
                'endpoints': unsecured_endpoints,
                'severity': 'HIGH'
            })
    
    def _check_session_management(self):
        """Check session management security"""
        app_files = ['app.py', 'app_working.py']
        
        for app_file in app_files:
            if Path(app_file).exists():
                try:
                    content = Path(app_file).read_text()
                    
                    # Check for proper session configuration
                    session_checks = [
                        ('SESSION_COOKIE_SECURE', 'Session cookies not marked as secure'),
                        ('SESSION_COOKIE_HTTPONLY', 'Session cookies not HTTPOnly'),
                        ('SECRET_KEY', 'No SECRET_KEY configuration found')
                    ]
                    
                    for check, message in session_checks:
                        if check not in content:
                            self.issues.append({
                                'type': 'session_security',
                                'file': app_file,
                                'message': message,
                                'severity': 'MEDIUM'
                            })
                            
                except Exception as e:
                    continue
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive authentication verification report"""
        total_issues = len(self.issues) + len(self.critical_issues)
        
        report = {
            'timestamp': str(Path.cwd()),
            'total_issues': total_issues,
            'critical_issues': len(self.critical_issues),
            'high_issues': len([i for i in self.issues if i.get('severity') == 'HIGH']),
            'medium_issues': len([i for i in self.issues if i.get('severity') == 'MEDIUM']),
            'issues': self.issues,
            'critical_issues': self.critical_issues,
            'status': 'FAIL' if total_issues > 0 else 'PASS',
            'security_score': max(0, 100 - (len(self.critical_issues) * 20) - (len(self.issues) * 5)),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.critical_issues:
            recommendations.append("IMMEDIATE: Fix all critical authentication issues")
            
            for critical in self.critical_issues:
                if critical['type'] == 'duplicate_auth':
                    recommendations.append("Consolidate to single authentication implementation")
                elif critical['type'] == 'hardcoded_secret':
                    recommendations.append("Remove all hardcoded secrets, use environment variables")
                elif critical['type'] == 'hardcoded_oauth':
                    recommendations.append("Move OAuth credentials to environment variables")
        
        if any(i.get('severity') == 'HIGH' for i in self.issues):
            recommendations.append("Fix high-severity authentication issues")
            recommendations.append("Implement proper JWT error handling")
            recommendations.append("Secure all API endpoints with authentication")
        
        if not recommendations:
            recommendations.append("Authentication system appears secure")
        
        return recommendations

def main():
    """Main verification function"""
    verifier = AuthenticationVerifier()
    report = verifier.verify_authentication_system()
    
    # Save report
    report_path = Path(__file__).parent / 'authentication_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print results
    print(f"\n📊 Authentication Verification Results:")
    print(f"Total issues: {report['total_issues']}")
    print(f"Critical: {report['critical_issues']}")
    print(f"High: {report['high_issues']}")
    print(f"Medium: {report['medium_issues']}")
    print(f"Security Score: {report['security_score']}/100")
    print(f"Status: {report['status']}")
    
    if len(report['critical_issues']) > 0:
        print(f"\n❌ CRITICAL AUTHENTICATION ISSUES:")
        for critical in report['critical_issues']:
            print(f"  - {critical['message']} ({critical.get('file', 'unknown')})")
    
    if report['status'] == 'FAIL':
        print(f"\nRecommendations:")
        for rec in report['recommendations'][:5]:
            print(f"  - {rec}")
        return False
    else:
        print(f"✅ Authentication system verification passed!")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)