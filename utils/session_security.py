#!/usr/bin/env python3
"""
Session Security Utilities
Provides session timeout and security validation for NOUS application
"""

from datetime import datetime, timedelta
from flask import session, request, redirect, url_for, flash
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def validate_session_security():
    """Validate session security and handle timeouts"""
    user_data = session.get('user')
    if not user_data:
        return None  # No session to validate
    
    # Check demo session expiration
    if user_data.get('demo_mode'):
        session_expires = user_data.get('session_expires')
        if session_expires:
            try:
                expire_time = datetime.fromisoformat(session_expires)
                if datetime.utcnow() > expire_time:
                    session.clear()
                    flash('Demo session expired. Please login again.', 'warning')
                    return redirect(url_for('auth.login'))
            except ValueError:
                # Invalid timestamp format, clear session
                session.clear()
                return redirect(url_for('auth.login'))
    
    # Update last activity timestamp
    session['last_activity'] = datetime.utcnow().isoformat()
    
    # Check for session hijacking indicators
    current_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    stored_ip = session.get('session_ip')
    
    if stored_ip and stored_ip != current_ip:
        logger.warning(f"Session IP changed: {stored_ip} -> {current_ip} for user {user_data.get('email', 'unknown')}")
        # For security, log but don't auto-logout (could be legitimate proxy/VPN change)
    
    # Store current IP for future comparison
    session['session_ip'] = current_ip
    
    return None

def require_valid_session(f):
    """Decorator to ensure session is valid and not expired"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validation_result = validate_session_security()
        if validation_result:
            return validation_result
        return f(*args, **kwargs)
    return decorated_function

def init_session_security(app):
    """Initialize session security with Flask app"""
    
    @app.before_request
    def check_session_security():
        """Check session security on every request"""
        # Skip session validation for static files and auth endpoints
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.endpoint.startswith('auth.'))):
            return None
        
        return validate_session_security()
    
    # Configure secure session settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8)  # Regular session timeout
    )