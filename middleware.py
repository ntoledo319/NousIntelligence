"""
Application Middleware

This module defines middleware functions for the Flask application.
It includes functions for applying system settings, HTTPS requirements, and security enhancements.

@module middleware
@description Flask application middleware with enhanced security
"""

import logging
from flask import Flask, request, redirect, session, current_app, abort
from datetime import timedelta
from functools import wraps
import time
import re

# Configure logging
logger = logging.getLogger(__name__)

# Simple in-memory store for rate-limiting counters (per process)
_rate_limit_cache: dict[str, int] = {}

def apply_performance_middleware(app: Flask):
    """Apply performance optimization middleware
    
    Args:
        app: Flask application instance
    """
    try:
        # Use our optimized performance middleware
        from utils.performance_middleware import setup_performance_middleware
        setup_performance_middleware(app)
        logger.info("Performance middleware applied")
    except ImportError:
        logger.info("Performance middleware not available")

def setup_middleware(app: Flask):
    """Set up all middleware for the application
    
    This function applies all middleware in the correct order.
    
    Args:
        app: Flask application instance
    """
    # Apply middleware in order of importance
    apply_security_middleware(app)
    apply_system_settings_middleware(app)
    apply_performance_middleware(app)

def apply_system_settings_middleware(app: Flask):
    """Apply system settings to the Flask application
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def load_system_settings():
        """Apply system settings on each request"""
        # Only apply settings to active requests, not static files
        if request.endpoint and 'static' not in request.endpoint:
            try:
                # Import here to avoid circular import issues
                from utils.settings import get_setting
                
                # Set session lifetime from settings
                session_timeout = get_setting('session_timeout', 60)  # Default 60 minutes
                app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=session_timeout)
                
                # Set session permanent to respect the timeout
                session.permanent = True
            except Exception as e:
                logger.error(f"Error applying system settings middleware: {str(e)}")

def apply_security_middleware(app: Flask):
    """Apply security-related middleware
    
    Args:
        app: Flask application instance
    """
    # Add security headers to every response
    @app.after_request
    def add_security_headers(response):
        """Add security headers to HTTP responses"""
        # Security headers based on OWASP recommendations
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # X-XSS-Protection is deprecated – rely on modern browsers and CSP.
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), fullscreen=*"
        )
        
        # Content Security Policy - can be customized based on application needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' https://cdn.jsdelivr.net",
            "style-src 'self' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https://lh3.googleusercontent.com",
            "connect-src 'self'",
            "frame-src 'self'"
        ]
        response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # HTTP Strict Transport Security for HTTPS enforcement
        if not app.debug and not app.testing:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
        return response
    
    # Rate limiting for API endpoints
    @app.before_request
    def api_rate_limiting():
        """Apply rate limiting to API requests"""
        # Only apply to API requests
        if request.path.startswith('/api/'):
            # Get client IP (support proxy header)
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

            # Window configuration
            now = int(time.time())
            window_size = 60  # seconds
            window_start = now // window_size

            key = f"{client_ip}:{window_start}"

            # Determine limit – higher for authenticated users
            from flask_login import current_user
            limit = 300 if current_user.is_authenticated else 60

            count = _rate_limit_cache.get(key, 0) + 1
            _rate_limit_cache[key] = count

            # Prune old windows occasionally to bound memory usage
            if len(_rate_limit_cache) > 10000:
                expiry_threshold = window_start - 2  # two windows ago
                for k in list(_rate_limit_cache.keys()):
                    if int(k.split(":")[-1]) < expiry_threshold:
                        _rate_limit_cache.pop(k, None)

            if count > limit:
                logger.warning(f"Rate limit exceeded for {client_ip} on {request.path}")
                abort(429, description="Too many requests. Please try again later.")
    
    # HTTPS redirection
    @app.before_request
    def enforce_https():
        """Enforce HTTPS for all requests in production"""
        try:
            # Only enforce in production
            if not app.debug and not app.testing:
                # Check if request is secure
                is_secure = request.is_secure
                
                # Also check X-Forwarded-Proto if behind a proxy
                x_proto = request.headers.get('X-Forwarded-Proto')
                if x_proto:
                    is_secure = x_proto.lower() == 'https'
                
                # Redirect to HTTPS if not secure
                if not is_secure and request.url.startswith('http://'):
                    url = request.url.replace('http://', 'https://', 1)
                    logger.info(f"Redirecting to HTTPS: {url}")
                    return redirect(url, code=301)
        except Exception as e:
            logger.error(f"Error enforcing HTTPS: {str(e)}")
    
    # Content type validation
    @app.before_request
    def validate_content_type():
        """Validate Content-Type header for API requests"""
        try:
            if request.method in ['POST', 'PUT', 'PATCH'] and request.path.startswith('/api/'):
                content_type = request.headers.get('Content-Type', '')
                
                # Validate JSON content type
                if 'json' in request.path and not content_type.startswith('application/json'):
                    logger.warning(f"Invalid Content-Type: {content_type} for JSON API")
                    abort(415, description="Content type must be application/json")
                    
                # Validate form submissions
                if 'form' in request.path and not content_type.startswith('application/x-www-form-urlencoded') and not content_type.startswith('multipart/form-data'):
                    logger.warning(f"Invalid Content-Type: {content_type} for form submission")
                    abort(415, description="Content type must be form data")
        except Exception as e:
            logger.error(f"Error validating content type: {str(e)}")
    
    # Path traversal prevention using standardized URL validation
    @app.before_request
    def prevent_path_traversal():
        """Prevent path traversal attacks using standardized URL validation"""
        try:
            from utils.url_utils import validate_url_path
            
            path = request.path
            
            # Use our standardized URL validation
            if not validate_url_path(path):
                logger.warning(f"Invalid URL path detected: {path}")
                abort(400, description="Invalid request path")
                
            # Additional checks for file extensions that should never be requested directly
            suspicious_extensions = ['.py', '.pyc', '.db', '.sqlite', '.env', '.git', '.ini', '.cfg', '.conf']
            if any(path.endswith(ext) for ext in suspicious_extensions):
                logger.warning(f"Suspicious file extension requested: {path}")
                abort(403, description="Access denied")
        except Exception as e:
            logger.error(f"Error in path traversal prevention: {str(e)}")
    
    # Try to use enhanced security middleware if available
    try:
        from utils.security_middleware import setup_security_middleware
        setup_security_middleware(app)
        logger.info("Enhanced security middleware applied")
    except ImportError:
        logger.info("Using built-in security middleware only")

def register_middleware(app: Flask):
    """Register all middleware with the Flask application
    
    Args:
        app: Flask application instance
    """
    setup_middleware(app)