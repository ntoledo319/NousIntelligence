"""
Application Middleware

This module defines middleware functions for the Flask application.
It includes functions for applying system settings, HTTPS requirements, and more.

@module middleware
@description Flask application middleware
"""

import logging
from flask import Flask, request, redirect, session
from datetime import timedelta
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

def setup_middleware(app: Flask):
    """Set up all middleware for the application
    
    Args:
        app: Flask application instance
    """
    # Apply middleware in order
    apply_system_settings_middleware(app)
    apply_security_middleware(app)

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
    @app.before_request
    def security_requirements():
        """Apply security requirements on each request"""
        try:
            # Import here to avoid circular import issues
            from utils.settings import get_setting
            
            # HTTPS requirement
            require_https = get_setting('require_https', True)
            if require_https and not request.is_secure and not app.debug:
                # Check if we're behind a proxy that handles HTTPS
                proto = request.headers.get('X-Forwarded-Proto')
                if proto and proto == 'http' and request.url.startswith('http://'):
                    url = request.url.replace('http://', 'https://', 1)
                    return redirect(url, code=301)
        except Exception as e:
            logger.error(f"Error in security middleware: {str(e)}")

def register_middleware(app: Flask):
    """Register all middleware with the Flask application
    
    Args:
        app: Flask application instance
    """
    setup_middleware(app) 