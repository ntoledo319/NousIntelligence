"""
Authentication Module

This module handles user authentication and registration.
It provides a simplified authentication system for development.

@module auth
@description Authentication providers and integration
"""

import logging
from flask import Blueprint, Flask
from flask_login import LoginManager

logger = logging.getLogger(__name__)

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import auth routes
from auth.routes import *

def register_auth_providers(app: Flask):
    """
    Register authentication providers with the application
    
    Args:
        app: Flask application instance
    """
    # Register the core auth blueprint
    app.register_blueprint(auth_bp)
    
    try:
        # Import and register Google auth provider if available
        from auth.google_auth import google_bp
        app.register_blueprint(google_bp)
        logger.info("Google authentication provider registered")
    except Exception as e:
        logger.warning(f"Google authentication provider not registered: {str(e)}")
    
    logger.info("Authentication providers registered")