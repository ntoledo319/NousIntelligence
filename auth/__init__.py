"""
Authentication Package

This package provides authentication implementations for different providers.
It consolidates various authentication mechanisms into a unified interface.

@module auth
@author NOUS Development Team
"""

from flask import Flask
import logging

logger = logging.getLogger(__name__)

def register_auth_providers(app: Flask) -> None:
    """
    Register all available authentication providers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Try to register Google OAuth using the standardized implementation
    try:
        from auth.google_auth import google_bp, init_app
        init_app(app)
        logger.info("Registered Google authentication provider using standard implementation")
    except Exception as e:
        logger.warning(f"Failed to register Google authentication: {str(e)}")
    
    # Try to register any other providers here
    # For example:
    # try:
    #     from auth.github import register_auth_blueprint as register_github
    #     register_github(app)
    #     logger.info("Registered GitHub authentication provider")
    # except Exception as e:
    #     logger.warning(f"Failed to register GitHub authentication: {str(e)}")
    
    logger.info("Authentication providers registration complete")