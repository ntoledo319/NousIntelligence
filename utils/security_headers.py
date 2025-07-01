"""
Security Headers and CSRF Protection
Implements comprehensive security headers and CSRF protection
"""

import secrets
from functools import wraps
from flask import request, jsonify, session, current_app

class CSRFProtection:
    """Simple CSRF protection implementation"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate CSRF token"""
        session_token = session.get('csrf_token')
        return session_token and secrets.compare_digest(session_token, token)

def csrf_protect(f):
    """CSRF protection decorator for state-changing operations"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Check for CSRF token
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            
            if not token or not CSRFProtection.validate_token(token):
                return jsonify({'error': 'CSRF token missing or invalid'}), 403
        
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

def add_security_headers(response):
    """Add comprehensive security headers to response"""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Force HTTPS in production
    if not current_app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self'"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy (formerly Feature Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )
    
    return response
