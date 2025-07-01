#!/usr/bin/env python3
"""
CSRF Protection Utility
Provides comprehensive Cross-Site Request Forgery protection for NOUS application
"""

import secrets
import hashlib
import hmac
from functools import wraps
from flask import session, request, abort, current_app
from typing import Optional

class CSRFProtection:
    """CSRF Protection implementation"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection with Flask app"""
        app.config.setdefault('CSRF_TOKEN_EXPIRES', 3600)  # 1 hour
        app.config.setdefault('CSRF_SECRET_KEY', app.secret_key)
        
        # Add CSRF token to all template contexts
        @app.context_processor
        def inject_csrf_token():
            return {'csrf_token': self.generate_csrf_token()}
    
    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']
    
    def validate_csrf_token(self, token: Optional[str] = None) -> bool:
        """Validate CSRF token"""
        if not token:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        
        if not token:
            return False
        
        session_token = session.get('csrf_token')
        if not session_token:
            return False
        
        # Use constant time comparison to prevent timing attacks
        return hmac.compare_digest(token, session_token)
    
    def protect(self, f):
        """Decorator to protect routes with CSRF validation"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                if not self.validate_csrf_token():
                    abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function

# Global CSRF protection instance
csrf = CSRFProtection()

def csrf_protect(f):
    """Standalone CSRF protection decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            
            if not token or not session_token or not hmac.compare_digest(token, session_token):
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token() -> str:
    """Generate CSRF token for templates"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']