"""
Unified Security Headers Module
Ensures consistent security headers across all pages
"""

from flask import make_response
from functools import wraps

def apply_security_headers(response):
    """Apply consistent security headers to response"""
    # Comprehensive CSP that allows necessary external resources
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://apis.google.com https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https://lh3.googleusercontent.com https://*.googleusercontent.com; "
        "connect-src 'self' https://oauth2.googleapis.com https://www.googleapis.com https://accounts.google.com; "
        "frame-src https://accounts.google.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self' https://accounts.google.com"
    )
    
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Add STS header for HTTPS deployments
    if response.headers.get('X-Forwarded-Proto') == 'https':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

def secure_headers(f):
    """Decorator to apply security headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        return apply_security_headers(response)
    return decorated_function