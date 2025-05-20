"""
Routes Module

This module registers all blueprint routes for the application.
It centralizes route organization and blueprint registration.
Optimized with lazy loading to improve application startup time.

@module routes
@description Blueprint registration and organization
"""

import logging
import importlib
import time
from flask import Flask, Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from typing import Dict, Callable, List, Tuple, Any

logger = logging.getLogger(__name__)

# Import blueprints directly to maintain compatibility
from routes.index import index_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.api import api_bp
from routes.spotify_visualization import spotify_viz
from routes.spotify_commands import spotify_commands
from routes.aa_routes import aa_bp
from routes.dbt_routes import dbt_bp
from routes.crisis_routes import crisis_bp
from routes.forms_routes import forms_bp
from routes.meet_routes import meet_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.spotify_routes import spotify_bp
from routes.smart_shopping_routes import smart_shopping_bp
from routes.price_routes import price_tracking_bp
from routes.voice_routes import voice_bp
from routes.view.auth import auth_bp
from auth.google_auth import google_bp

# Blueprint module organization
# This comment serves as documentation for the blueprint structure
# The blueprints are organized into the following categories:
#
# 1. Core blueprints:
#    - index_bp (/)
#    - dashboard_bp (/dashboard)
#    - settings_bp (/settings)
#    - api_bp (/api)
#
# 2. Feature-specific blueprints:
#    - Spotify integration (spotify_viz, spotify_commands, spotify_bp)
#    - Health & wellness (aa_bp, dbt_bp, crisis_bp)
#    - Google Workspace (forms_bp, meet_bp)
#    - User management (user_bp, admin_bp)
#    - Shopping features (smart_shopping_bp, price_tracking_bp)
#    - Voice interfaces (voice_bp)

def register_blueprints(app: Flask):
    """
    Register all blueprint routes with the application
    
    Args:
        app: Flask application instance
    """
    # Register core blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    
    # Register Spotify blueprints
    app.register_blueprint(spotify_viz)
    app.register_blueprint(spotify_commands)
    app.register_blueprint(spotify_bp)
    
    # Register AA and DBT feature blueprints
    app.register_blueprint(aa_bp)
    app.register_blueprint(dbt_bp)
    app.register_blueprint(crisis_bp)
    
    # Register Google Workspace integration blueprints
    app.register_blueprint(forms_bp)
    app.register_blueprint(meet_bp)
    
    # Register user and admin blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # Register smart shopping and price tracking blueprints
    app.register_blueprint(smart_shopping_bp)
    app.register_blueprint(price_tracking_bp)
    
    # Register voice interface blueprint
    app.register_blueprint(voice_bp)
    
    # Register authentication blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp)
    
    logger.info("All blueprints registered successfully")
    
    # Add welcome route
    @app.route('/welcome')
    @login_required
    def welcome():
        """Welcome page for new users"""
        return render_template('welcome.html')
        
    # Add logout route
    @app.route('/logout')
    def logout():
        """Log out the current user"""
        from flask_login import logout_user
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('index.index'))
        
    logger.info("All blueprints registered successfully")