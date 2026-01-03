"""
Security Headers Middleware - Phase 5.1 Security Hardening
Implements comprehensive security headers
"""
from flask import Flask, Response
from typing import Dict

def add_security_headers(app: Flask) -> None:
    """
    Add security headers to all responses
    
    Headers added:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options  
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    @app.after_request
    def set_security_headers(response: Response) -> Response:
        """Apply security headers to response"""
        
        # HSTS: Force HTTPS for 1 year
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # XSS Protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy (restrict browser features)
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'accelerometer=(), '
            'gyroscope=()'
        )
        
        # Content Security Policy (CSP)
        # Allow self, Google OAuth, and CDNs
        csp_directives = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",  # Required for some inline scripts
                "https://accounts.google.com",
                "https://apis.google.com"
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",  # Required for styled-components
                "https://fonts.googleapis.com"
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com"
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:",
                "blob:"
            ],
            "connect-src": [
                "'self'",
                "https://accounts.google.com",
                "https://oauth2.googleapis.com"
            ],
            "frame-src": [
                "https://accounts.google.com"
            ],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "frame-ancestors": ["'none'"],
            "upgrade-insecure-requests": []
        }
        
        csp = "; ".join(
            f"{key} {' '.join(values)}" if values else key
            for key, values in csp_directives.items()
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    return app
