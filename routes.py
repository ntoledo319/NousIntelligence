"""
Routes Module (Legacy)

This module serves as a compatibility layer for the old routes system.
New code should use the organized routes in the routes/ directory.

This file will be removed in a future version.

@module routes
@author NOUS Development Team
"""

import logging
from flask import Flask, redirect, url_for
from flask_login import current_user

def register_routes(app: Flask):
    """
    Register compatibility routes for redirecting to the new route structure.
    
    Args:
        app: Flask application instance
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info("Registering compatibility routes")
    
    @app.route('/')
    def index():
        """Redirect to the new index blueprint"""
        return redirect(url_for('index.index'))
    
    @app.route('/dashboard')
    def dashboard():
        """Redirect to the new dashboard blueprint"""
        return redirect(url_for('dashboard.dashboard'))
    
    @app.route('/settings')
    def settings_page():
        """Redirect to the new settings blueprint"""
        return redirect(url_for('settings.settings_page'))
    
    @app.route('/user_guide')
    def user_guide():
        """Redirect to help page"""
        return redirect(url_for('index.help_page'))
    
    @app.route('/help')
    def help_page():
        """Redirect to new help page"""
        return redirect(url_for('index.help_page'))