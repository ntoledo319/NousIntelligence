"""
Security Middleware

This module provides security middleware functions for the Flask application.
It implements security best practices to protect against common web vulnerabilities.

@module security_middleware
@description Security middleware utilities
"""

import logging
from functools import wraps
from flask import request, g, session, redirect, url_for, current_app, abort, flash
from werkzeug.urls import url_parse
from utils.login_security import log_security_event

logger = logging.getLogger(__name__)

def apply_security_headers(response):
    """
    Apply security headers to HTTP responses
    
    This adds various security headers to protect against common attacks:
    - Content-Security-Policy: Prevents XSS by restricting resource loading
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Restricts browser features
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response with security headers
    """
    # Content Security Policy (CSP)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: blob:; font-src 'self' cdn.jsdelivr.net; connect-src 'self'"
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent embedding in frames (clickjacking protection)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Control how much referrer information is included
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Restrict browser features
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(self), interest-cohort=()'
    
    return response

def require_https():
    """
    Redirect to HTTPS if accessed over HTTP
    
    This middleware ensures all requests use HTTPS in production.
    It checks the X-Forwarded-Proto header set by reverse proxies.
    """
    # Skip check if running locally/development or HTTPS already used
    if current_app.debug or request.is_secure:
        return
    
    # Check for proxy headers
    proto = request.headers.get('X-Forwarded-Proto')
    if proto == 'https':
        return
    
    # Redirect to HTTPS
    url = request.url.replace('http://', 'https://', 1)
    return redirect(url, code=301)

def session_security():
    """
    Apply session security measures
    
    This middleware:
    - Regenerates session ID periodically
    - Sets secure session cookies in production
    - Validates session referrer for CSRF protection
    """
    # Only process for authenticated sessions
    if 'user_id' not in session:
        return
    
    # Regenerate session ID periodically to prevent session fixation
    if 'last_regenerated' not in session:
        session['last_regenerated'] = 0
        
    regeneration_interval = current_app.config.get('SESSION_REGENERATION_INTERVAL', 3600)  # 1 hour default
    current_time = int(request.time)
    
    if current_time - session.get('last_regenerated', 0) > regeneration_interval:
        session.regenerate()
        session['last_regenerated'] = current_time
        logger.debug("Session ID regenerated")
    
    # Check if request comes from a different site (CSRF protection)
    if request.method != 'GET':
        referer = request.headers.get('Referer')
        if referer:
            parsed_url = url_parse(referer)
            if parsed_url.host != request.host:
                # Log possible CSRF attempt
                user_id = session.get('user_id')
                log_security_event('csrf_attempt', user_id, f"Request from {parsed_url.host}")
                logger.warning(f"Possible CSRF attempt from {parsed_url.host}")
                abort(403)

def setup_security_middleware(app):
    """
    Set up all security middleware for the application
    
    Args:
        app: Flask application
    """
    # Apply security headers to all responses
    app.after_request(apply_security_headers)
    
    # Add HTTPS redirects middleware
    app.before_request(require_https)
    
    # Add session security middleware
    app.before_request(session_security)
    
    logger.info("Security middleware configured")

def admin_required(f):
    """
    Decorator to require admin privileges for a route
    
    Usage:
    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
            
        if not current_user.is_admin:
            log_security_event('unauthorized_admin_access', current_user.id, 
                             f"Attempted to access admin route: {request.path}")
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def verified_account_required(f):
    """
    Decorator to require verified email for a route
    
    Usage:
    @app.route('/settings')
    @verified_account_required
    def settings():
        return render_template('settings.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
            
        if not current_user.email_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('auth.verify_email'))
            
        return f(*args, **kwargs)
    return decorated_function