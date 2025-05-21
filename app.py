"""
Application Module for Imports

This module exists to provide clean imports for other modules in the application.
Instead of importing directly from main.py, modules can import from here.
This helps avoid circular import issues.
"""

from app_factory import create_app, db
from flask import redirect, request, url_for
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Create an application instance for direct import
# This allows modules to import 'app' directly
app = create_app()

# Root level callback route for Google OAuth
@app.route('/callback/google')
def google_callback_root():
    """
    Root-level Google OAuth callback handler that redirects to the proper route
    """
    logger.info("Root-level Google OAuth callback received")
    
    # Preserve all query parameters when redirecting to the actual handler
    return redirect(url_for('google_auth.callback', **request.args.to_dict()))

# Export key components for easy importing
__all__ = ['app', 'db']