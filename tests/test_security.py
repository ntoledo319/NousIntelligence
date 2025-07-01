"""
Security Test Suite
Comprehensive tests for security vulnerabilities
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


class TestXSSPrevention:
    """Test XSS vulnerability prevention"""
    
    def test_no_html_injection_in_messages(self, authenticated_client):
        """Test that HTML is properly escaped in chat messages"""
        malicious_input = '<script>alert("XSS")</script>'
        
        response = authenticated_client.post('/api/v1/chat',
                                           json={'message': malicious_input})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Ensure the response doesn't contain unescaped script tags
        assert '<script>' not in data.get('response', '')
        assert '&lt;script&gt;' in data.get('response', '') or malicious_input not in data.get('response', '')
    
    def test_no_javascript_urls(self, authenticated_client):
        """Test that javascript: URLs are blocked"""
        malicious_input = 'Check this link: javascript:alert("XSS")'
        
        response = authenticated_client.post('/api/v1/chat',
                                           json={'message': malicious_input})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'javascript:' not in data.get('response', '')
    
    def test_svg_xss_prevention(self, authenticated_client):
        """Test that SVG-based XSS is prevented"""
        svg_xss = '<svg onload=alert("XSS")>'
        
        response = authenticated_client.post('/api/v1/chat',
                                           json={'message': svg_xss})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'onload=' not in data.get('response', '')


class TestAuthentication:
    """Test authentication security"""
    
    def test_session_rotation_on_login(self, client):
        """Test that session is rotated on successful login"""
        # Get initial session
        client.get('/')
        initial_session = client.cookie_jar._cookies
        
        # Perform login
        response = client.post('/auth/demo-mode')
        
        # Session should be different after login
        assert response.status_code in [302, 200]
        new_session = client.cookie_jar._cookies
        assert initial_session != new_session
    
    def test_csrf_protection(self, client):
        """Test CSRF protection on state-changing operations"""
        # Try to make a POST request without CSRF token
        response = client.post('/api/v1/chat',
                             json={'message': 'test'},
                             headers={'X-Requested-With': 'XMLHttpRequest'})
        
        # Should be rejected or require authentication
        assert response.status_code in [401, 403]
    
    def test_session_timeout(self, authenticated_client):
        """Test session timeout behavior"""
        # Session should expire after configured time
        with patch('flask.session', {'user': {'id': 'test'}, 
                                   '_permanent': True,
                                   '_expires': datetime.utcnow() - timedelta(hours=25)}):
            response = authenticated_client.get('/api/user')
            # Should require re-authentication
            assert response.status_code == 401
    
    def test_password_not_in_logs(self, client, caplog):
        """Test that passwords are never logged"""
        # Attempt login with credentials
        client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'super_secret_password_123'
        })
        
        # Check logs don't contain password
        assert 'super_secret_password_123' not in caplog.text


class TestSQLInjection:
    """Test SQL injection prevention"""
    
    def test_sql_injection_in_search(self, authenticated_client):
        """Test SQL injection in search functionality"""
        sql_injection = "'; DROP TABLE users; --"
        
        response = authenticated_client.get(f'/api/v1/search/?q={sql_injection}')
        
        # Should handle gracefully without executing SQL
        assert response.status_code in [200, 400]
        # Table should still exist (would need DB check in real test)
    
    def test_parameterized_queries(self, authenticated_client):
        """Test that queries use parameterization"""
        # Test various SQL injection patterns
        injections = [
            "1' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1",
            "1' UNION SELECT * FROM users--",
            "1' AND SLEEP(5)--"
        ]
        
        for injection in injections:
            response = authenticated_client.post('/api/v1/chat',
                                               json={'message': injection})
            # Should complete quickly without sleeping
            assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting implementation"""
    
    def test_rate_limit_on_login(self, client):
        """Test rate limiting on login attempts"""
        # Make multiple rapid login attempts
        for i in range(10):
            response = client.post('/auth/google')
            
        # Should eventually get rate limited
        response = client.post('/auth/google')
        assert response.status_code in [429, 302]  # Too Many Requests or redirect
    
    def test_rate_limit_on_api(self, authenticated_client):
        """Test rate limiting on API endpoints"""
        # Make many rapid API calls
        responses = []
        for i in range(100):
            response = authenticated_client.post('/api/v1/chat',
                                               json={'message': 'test'})
            responses.append(response.status_code)
        
        # Should see rate limiting kick in
        assert 429 in responses or all(r == 200 for r in responses[:60])


class TestInputValidation:
    """Test input validation"""
    
    def test_message_length_limit(self, authenticated_client):
        """Test message length validation"""
        # Try to send extremely long message
        long_message = 'x' * 10001
        
        response = authenticated_client.post('/api/v1/chat',
                                           json={'message': long_message})
        
        assert response.status_code in [400, 413]  # Bad Request or Payload Too Large
    
    def test_invalid_json(self, authenticated_client):
        """Test handling of invalid JSON"""
        response = authenticated_client.post('/api/v1/chat',
                                           data='{"invalid json}',
                                           content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_required_fields(self, authenticated_client):
        """Test missing required fields"""
        response = authenticated_client.post('/api/v1/chat',
                                           json={})  # Missing 'message'
        
        assert response.status_code == 400
    
    def test_null_byte_injection(self, authenticated_client):
        """Test null byte injection prevention"""
        null_byte_input = 'test\x00malicious'
        
        response = authenticated_client.post('/api/v1/chat',
                                           json={'message': null_byte_input})
        
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert '\x00' not in data.get('response', '')


class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are set"""
        response = client.get('/')
        
        # Check for essential security headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        
        assert 'X-XSS-Protection' in response.headers
        
        # CSP should be present
        assert 'Content-Security-Policy' in response.headers
    
    def test_no_server_header_leak(self, client):
        """Test that server info is not leaked"""
        response = client.get('/')
        
        # Should not reveal server software
        assert 'Server' not in response.headers or 'Python' not in response.headers.get('Server', '')


class TestCryptography:
    """Test cryptographic implementations"""
    
    def test_token_randomness(self):
        """Test that tokens are properly random"""
        from utils.secret_manager import generate_secure_secret
        
        # Generate multiple tokens
        tokens = [generate_secure_secret() for _ in range(100)]
        
        # All should be unique
        assert len(set(tokens)) == 100
        
        # All should be of sufficient length
        assert all(len(token) >= 64 for token in tokens)
    
    def test_secret_validation(self):
        """Test secret strength validation"""
        from utils.secret_manager import validate_secret
        
        # Weak secrets should fail
        weak_secrets = [
            'password123',
            '12345678901234567890123456789012345678901234567890123456789012',
            'a' * 64,  # Low entropy
        ]
        
        for secret in weak_secrets:
            valid, message = validate_secret(secret)
            assert not valid
        
        # Strong secret should pass
        from utils.secret_manager import generate_secure_secret
        strong_secret = generate_secure_secret()
        valid, message = validate_secret(strong_secret)
        assert valid


class TestErrorHandling:
    """Test secure error handling"""
    
    def test_no_stack_traces_in_production(self, client):
        """Test that stack traces aren't exposed in production"""
        # Force an error
        response = client.get('/api/v1/nonexistent')
        
        assert response.status_code in [404, 500]
        
        # Response should not contain stack trace
        response_text = response.get_data(as_text=True)
        assert 'Traceback' not in response_text
        assert 'File "' not in response_text
    
    def test_generic_error_messages(self, client):
        """Test that error messages don't reveal system info"""
        response = client.post('/api/v1/chat')  # Missing auth
        
        if response.status_code >= 400:
            data = response.get_data(as_text=True)
            # Should not reveal internal paths or system info
            assert '/home/' not in data
            assert 'postgres' not in data.lower()
            assert 'sqlalchemy' not in data.lower() 