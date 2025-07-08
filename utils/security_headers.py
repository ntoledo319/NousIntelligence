from flask import Flask

def init_security_headers(app: Flask):
    """Add security headers to all responses"""
    @app.after_request
    def add_security_headers(response):
        # Prevent XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Force HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://apis.google.com https://accounts.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https://*.googleusercontent.com; "
            "connect-src 'self' https://oauth2.googleapis.com https://www.googleapis.com; "
            "frame-src https://accounts.google.com;"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # Prevent referrer leakage
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    return app
