"""
Security Middleware Module

This module provides security-focused middleware for the Flask application.
It includes protection against common web vulnerabilities like XSS, CSRF, and clickjacking.

@module utils.security_middleware
@description Security middleware functions
"""

import logging
from flask import request, session, g, abort, make_response, current_app
from functools import wraps
import secrets
import re
import time
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

def apply_security_headers(response):
    """
    Apply security headers to HTTP responses

    Args:
        response: Flask response object

    Returns:
        response: Modified response with security headers
    """
    # Content Security Policy (CSP)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self';"

    # Protection against clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Protection against XSS
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # MIME type sniffing protection
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Protection against content leakage
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # HTTP Strict Transport Security (HSTS)
    if not current_app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Permissions policy (formerly Feature-Policy)
    response.headers['Permissions-Policy'] = "geolocation=(), microphone=(), camera=()"

    return response

def setup_security_middleware(app):
    """
    Set up security middleware for the Flask application

    Args:
        app: Flask application instance
    """
    # Apply security headers to all responses
    app.after_request(apply_security_headers)

    # Set secure cookie options
    app.config['SESSION_COOKIE_SECURE'] = not app.debug
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Enable CSRF protection
    @app.before_request
    def csrf_protect():
        # Only apply to state-changing methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token')
            if not token or session.get('csrf_token') != token:
                logger.warning(f"CSRF token validation failed for {request.path}")
                abort(403, "CSRF token validation failed")

    # Generate CSRF token for templates
    @app.context_processor
    def inject_csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return {'csrf_token': session.get('csrf_token')}

    # Detect and block suspicious requests
    @app.before_request
    def detect_suspicious_request():
        # Skip for static files and assets
        if request.path.startswith('/static/'):
            return

        # Set rate limiting data in g
        if not hasattr(g, 'rate_limit_data'):
            g.rate_limit_data = {}

        ip = request.remote_addr
        path = request.path

        # Create rate limit key with IP and path
        key = f"{ip}:{path}"

        # Initialize rate limit data for this key
        if key not in g.rate_limit_data:
            g.rate_limit_data[key] = {
                'count': 0,
                'first_request': time.time()
            }

        # Update request count
        g.rate_limit_data[key]['count'] += 1

        # Check if rate limit exceeded (more than 30 requests in 10 seconds)
        if (time.time() - g.rate_limit_data[key]['first_request'] < 10 and
            g.rate_limit_data[key]['count'] > 30):
            logger.warning(f"Rate limit exceeded for {ip} on {path}")
            abort(429, "Too many requests")

        # Reset counter if more than 10 seconds since first request
        if time.time() - g.rate_limit_data[key]['first_request'] > 10:
            g.rate_limit_data[key]['count'] = 1
            g.rate_limit_data[key]['first_request'] = time.time()

        # Check for SQL injection patterns in URL parameters
        sql_patterns = [
            r'(?i)(?:\%27)|(?:\')(?:\s+?)(?:(?:(?:or)|(?:and))\s+)(?:\w+)(?:\s+?)(?:=)(?:\s+?)(?:(?:\')|(?:\")|(?:\%27))',
            r'(?i)(?:union)(?:\s+?)(?:(?:select))',
            r'(?i)(?:into)(?:\s+?)(?:(?:dump))',
            r'(?i)(?:from)(?:\s+?)(?:(?:information_schema))',
            r'(?i)(?:(?:--)|(?:#)|(?:\/\*.*\*\/))'
        ]

        # Check URL parameters for SQL injection patterns
        for key, value in request.args.items():
            for pattern in sql_patterns:
                if re.search(pattern, value):
                    logger.warning(f"Potential SQL injection attempt from {ip}: {key}={value}")
                    abort(403, "Suspicious request parameter")

    # Log all requests except static files
    @app.before_request
    def log_request():
        # Skip for static files
        if request.path.startswith('/static/'):
            return

        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

def require_https(f):
    """
    Decorator to require HTTPS for a view function

    Args:
        f: View function to decorate

    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return abort(403, "HTTPS required")
        return f(*args, **kwargs)
    return decorated_function

def allowed_roles(*roles):
    """
    Decorator to restrict access to users with specific roles

    Args:
        *roles: List of allowed roles

    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user

            # Check if user is authenticated and has an allowed role
            if not current_user.is_authenticated:
                abort(401, "Authentication required")

            # Get user's role(s)
            user_roles = getattr(current_user, 'roles', [])
            if isinstance(user_roles, str):
                user_roles = [user_roles]

            # Check if user has any of the allowed roles
            if not any(role in user_roles for role in roles):
                logger.warning(f"Role-based access denied for {current_user.email}: requires {roles}, has {user_roles}")
                abort(403, "Access denied")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests, period_seconds):
    """
    Decorator to apply rate limiting to a view function

    Args:
        max_requests: Maximum number of requests allowed in the period
        period_seconds: Time period in seconds

    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client info
            ip = request.remote_addr
            path = request.path

            # Create rate limit key with IP and path
            key = f"{ip}:{path}"

            # Initialize rate limit data in g
            if not hasattr(g, 'view_rate_limits'):
                g.view_rate_limits = {}

            # Initialize rate limit data for this key
            if key not in g.view_rate_limits:
                g.view_rate_limits[key] = {
                    'count': 0,
                    'first_request': time.time()
                }

            # Check if period has passed
            if time.time() - g.view_rate_limits[key]['first_request'] > period_seconds:
                # Reset counter if period has passed
                g.view_rate_limits[key]['count'] = 1
                g.view_rate_limits[key]['first_request'] = time.time()
            else:
                # Increment counter
                g.view_rate_limits[key]['count'] += 1

                # Check if rate limit exceeded
                if g.view_rate_limits[key]['count'] > max_requests:
                    logger.warning(f"Rate limit exceeded for {ip} on {path}: {max_requests} requests in {period_seconds}s")

                    # Calculate retry after time
                    retry_after = int(period_seconds - (time.time() - g.view_rate_limits[key]['first_request']))

                    response = make_response("Rate limit exceeded", 429)
                    response.headers['Retry-After'] = str(max(1, retry_after))
                    return response

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def secure_admin_required(f):
    """
    Decorator to restrict access to admin users with additional security checks

    Args:
        f: View function to decorate

    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check if user is authenticated and is an admin
        if not current_user.is_authenticated:
            abort(401, "Authentication required")

        # Check if user has admin role
        user_roles = getattr(current_user, 'roles', [])
        if isinstance(user_roles, str):
            user_roles = [user_roles]

        if 'admin' not in user_roles:
            logger.warning(f"Admin access denied for {current_user.email}")
            abort(403, "Admin access required")

        # Additional security checks for admin access

        # Check if request is HTTPS
        if not request.is_secure and not current_app.debug:
            abort(403, "HTTPS required for admin access")

        # Check if admin session is fresh (re-login required for sensitive operations)
        if not session.get('admin_access_time') or (time.time() - session.get('admin_access_time', 0)) > 3600:
            # Admin session expired, require re-login
            session['next'] = request.url  # Save requested URL
            session['admin_reauth'] = True

            # Redirect to admin login
            from flask import redirect, url_for
            return redirect(url_for('auth.admin_login'))

        # Update admin access time
        session['admin_access_time'] = time.time()

        return f(*args, **kwargs)
    return decorated_function

def xss_protect(content, allowed_tags=None, strip=True):
    """
    Clean content from potential XSS attacks

    Args:
        content: HTML content to clean
        allowed_tags: List of allowed HTML tags (optional)
        strip: Whether to strip disallowed tags or escape them

    Returns:
        str: Cleaned content
    """
    import bleach

    if allowed_tags is None:
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'a']

    allowed_attributes = {
        'a': ['href', 'title', 'target', 'rel'],
        '*': ['class']
    }

    # Clean the content
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=strip
    )