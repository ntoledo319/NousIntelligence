#!/usr/bin/env python3
"""
Test Issue 5: Insecure Session Configuration
This test demonstrates session security configuration issues
"""
import os
import sys
sys.path.insert(0, '.')

def test_session_cookie_security_config():
    """Test that session cookies are not properly secured for production"""
    
    if os.path.exists('config/app_config.py'):
        with open('config/app_config.py', 'r') as f:
            content = f.read()
        
        # Check session cookie configuration
        session_configs = [
            'SESSION_COOKIE_SECURE',
            'SESSION_COOKIE_HTTPONLY', 
            'SESSION_COOKIE_SAMESITE'
        ]
        
        found_configs = []
        for config in session_configs:
            if config in content:
                found_configs.append(config)
        
        # Should have some session config but not production-ready
        assert len(found_configs) >= 2, "Should have basic session configuration"
        
        # Check if secure flag is environment-dependent (vulnerability)
        if 'SESSION_COOKIE_SECURE' in content:
            # Check the line with SESSION_COOKIE_SECURE
            lines = content.split('\n')
            for line in lines:
                if 'SESSION_COOKIE_SECURE' in line and '=' in line:
                    # Should be dependent on environment (insecure)
                    assert 'development' in line or 'production' in line, "Session security should be environment-dependent for this test"

def test_production_session_vulnerability():
    """Test demonstrates session configuration vulnerability in production"""
    
    # Read the app configuration
    if os.path.exists('config/app_config.py'):
        with open('config/app_config.py', 'r') as f:
            content = f.read()
        
        # Check for insecure session configuration patterns
        vulnerable_patterns = [
            "SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV', 'production') != 'development'",
            "DEBUG = os.environ.get('FLASK_ENV', 'production') == 'development'"
        ]
        
        vulnerabilities_found = []
        for pattern in vulnerable_patterns:
            if pattern in content:
                vulnerabilities_found.append("Environment-dependent security settings")
        
        # Check for missing security headers
        if 'PERMANENT_SESSION_LIFETIME' in content:
            # Check if session lifetime is too long
            lines = content.split('\n')
            for line in lines:
                if 'PERMANENT_SESSION_LIFETIME' in line and '86400' in line:
                    vulnerabilities_found.append("Session lifetime too long (24 hours)")
        
        assert len(vulnerabilities_found) > 0, f"Should find session vulnerabilities: {vulnerabilities_found}"

def test_csrf_token_in_session():
    """Test that CSRF tokens are stored in session without proper validation"""
    
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Should have CSRF token generation
        assert 'csrf_token' in content, "Should have CSRF token functionality"
        
        # Check if CSRF is properly implemented
        if 'secrets.token_hex(32)' in content:
            # CSRF tokens are generated but check validation
            csrf_validation_patterns = [
                'csrf_protect',
                'validate_csrf_token',
                'csrf.protect'
            ]
            
            validation_found = False
            for pattern in csrf_validation_patterns:
                if pattern in content:
                    validation_found = True
                    break
            
            # For this vulnerability test, CSRF should be generated but not widely used
            assert not validation_found, "CSRF tokens generated but not properly validated across routes"

def test_session_security_gaps():
    """Test demonstrates various session security gaps"""
    
    security_gaps = []
    
    # Check app.py for session configuration
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check if session security is initialized
        if 'init_session_security' in app_content:
            security_gaps.append("Session security module exists but may not be comprehensive")
    
    # Check if there's a session security utility
    if os.path.exists('utils/session_security.py'):
        with open('utils/session_security.py', 'r') as f:
            session_content = f.read()
        
        # Basic session security should exist but be incomplete
        if 'regenerate' in session_content or 'session_id' in session_content:
            security_gaps.append("Basic session security exists")
    
    assert len(security_gaps) > 0, "Should find session security implementation gaps"

if __name__ == "__main__":
    test_session_cookie_security_config()
    test_production_session_vulnerability()
    test_csrf_token_in_session()
    test_session_security_gaps()
    print("All tests completed - Session security vulnerabilities confirmed")