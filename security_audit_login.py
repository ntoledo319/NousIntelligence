#!/usr/bin/env python3
"""
Login Service Security Audit
Comprehensive security analysis of authentication system
"""

import os
import re
import logging
from pathlib import Path

def audit_login_service():
    """Perform comprehensive security audit of login service"""
    
    print('=== LOGIN SERVICE SECURITY AUDIT ===\n')
    
    issues = []
    warnings = []
    good_practices = []
    
    # Check 1: Authentication configuration
    print('1. AUTHENTICATION CONFIGURATION')
    try:
        from app_working import create_app
        app = create_app()
        
        # Check secret key configuration
        if hasattr(app, 'secret_key') and app.secret_key:
            if app.secret_key.startswith('dev') or len(app.secret_key) < 32:
                issues.append('Weak secret key detected')
            else:
                good_practices.append('Secret key properly configured')
        else:
            issues.append('No secret key configured')
        
        # Check database configuration
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            good_practices.append('Database URI configured')
        else:
            issues.append('Database URI not configured')
            
        print('✅ App configuration check complete')
    except Exception as e:
        issues.append(f'App configuration error: {e}')
    
    # Check 2: OAuth credentials
    print('\n2. OAUTH CREDENTIALS')
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        good_practices.append('Google OAuth credentials configured')
        if len(client_id) > 50 and len(client_secret) > 20:
            good_practices.append('OAuth credentials appear valid')
        else:
            warnings.append('OAuth credentials may be invalid')
    else:
        issues.append('Google OAuth credentials missing')
    
    # Check 3: Code security analysis
    print('\n3. CODE SECURITY ANALYSIS')
    auth_files = [
        'routes/auth_routes.py',
        'utils/google_oauth.py', 
        'models/user.py'
    ]
    
    for file_path in auth_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for hardcoded secrets
            hardcoded_patterns = [
                r'client_secret.*=.*["\'][\w\-]{20,}["\']',
                r'SECRET_KEY.*=.*["\'][\w\-]{20,}["\']',
                r'password.*=.*["\'][\w\-]{8,}["\']'
            ]
            
            has_hardcoded = False
            for pattern in hardcoded_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    has_hardcoded = True
                    break
                    
            if has_hardcoded:
                issues.append(f'Hardcoded secret detected in {file_path}')
            else:
                good_practices.append(f'No hardcoded secrets in {file_path}')
                
            # Check for proper error handling
            if 'try:' in content and 'except' in content and 'logger' in content:
                good_practices.append(f'Proper error handling in {file_path}')
            elif 'try:' in content and 'except' in content:
                warnings.append(f'Basic error handling in {file_path}')
            else:
                warnings.append(f'Limited error handling in {file_path}')
                
            # Check for SQL injection protection
            if 'query.filter_by' in content or '.get(' in content:
                good_practices.append(f'Safe database queries in {file_path}')
            elif '%s' in content and 'query' in content:
                issues.append(f'Potential SQL injection in {file_path}')
                
            # Check for CSRF protection
            if "methods=['POST']" in content and ('csrf' in content.lower() or '@login_required' in content):
                good_practices.append(f'CSRF protection implemented in {file_path}')
            elif "methods=['POST']" in content:
                warnings.append(f'POST endpoint without CSRF protection in {file_path}')
    
    # Check 4: Session security
    print('\n4. SESSION SECURITY')
    try:
        from config.app_config import AppConfig
        
        session_secure = getattr(AppConfig, 'SESSION_COOKIE_SECURE', None)
        session_httponly = getattr(AppConfig, 'SESSION_COOKIE_HTTPONLY', None)
        session_samesite = getattr(AppConfig, 'SESSION_COOKIE_SAMESITE', None)
        
        if session_secure:
            good_practices.append('Secure session cookies enabled')
        else:
            warnings.append('Session cookies not marked secure')
            
        if session_httponly:
            good_practices.append('HTTPOnly session cookies enabled')
        else:
            warnings.append('Session cookies not HTTPOnly')
            
        if session_samesite:
            good_practices.append('SameSite session cookies configured')
        else:
            warnings.append('SameSite not configured for session cookies')
            
    except Exception as e:
        warnings.append(f'Could not check session config: {e}')
    
    # Check 5: OAuth flow security
    print('\n5. OAUTH FLOW SECURITY')
    try:
        oauth_file = Path('utils/google_oauth.py')
        if oauth_file.exists():
            content = oauth_file.read_text()
            
            # Check for state parameter (CSRF protection)
            if 'state' in content.lower():
                good_practices.append('OAuth state parameter used')
            else:
                warnings.append('OAuth state parameter not found')
                
            # Check for proper token handling
            if 'refresh_token' in content:
                good_practices.append('Refresh token support implemented')
            else:
                warnings.append('No refresh token support')
                
            # Check for token storage security
            if 'google_access_token' in content and 'db.session.commit' in content:
                good_practices.append('Secure token storage implemented')
            else:
                warnings.append('Token storage may be insecure')
                
    except Exception as e:
        warnings.append(f'OAuth flow check failed: {e}')
    
    # Check 6: Rate limiting and brute force protection
    print('\n6. RATE LIMITING')
    rate_limiting_found = False
    for file_path in ['routes/auth_routes.py', 'app_working.py']:
        if Path(file_path).exists():
            content = Path(file_path).read_text()
            if 'rate_limit' in content.lower() or 'limiter' in content.lower():
                good_practices.append('Rate limiting implemented')
                rate_limiting_found = True
                break
    
    if not rate_limiting_found:
        warnings.append('No rate limiting detected')
    
    # Print results
    print('\n=== AUDIT RESULTS ===')
    print(f'\n🔴 CRITICAL ISSUES ({len(issues)}):')
    for issue in issues:
        print(f'  - {issue}')
    
    print(f'\n🟡 WARNINGS ({len(warnings)}):')
    for warning in warnings:
        print(f'  - {warning}')
    
    print(f'\n🟢 GOOD PRACTICES ({len(good_practices)}):')
    for practice in good_practices:
        print(f'  - {practice}')
    
    security_score = max(0, 100 - (len(issues) * 20) - (len(warnings) * 5))
    print(f'\n📊 SECURITY SCORE: {security_score}/100')
    
    if len(issues) == 0:
        print('✅ No critical security issues found')
    else:
        print('❌ Critical issues need immediate attention')
    
    return {
        'issues': issues,
        'warnings': warnings,
        'good_practices': good_practices,
        'security_score': security_score
    }

if __name__ == '__main__':
    audit_login_service()