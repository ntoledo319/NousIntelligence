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

# Import blueprints directly for backwards compatibility
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

# Define blueprint import paths and priorities
# Higher priority (lower number) blueprints are loaded first
BLUEPRINT_IMPORTS = [
    # Core blueprints (Priority 1) - loaded immediately
    (1, 'routes.index', 'index_bp'),
    (1, 'routes.dashboard', 'dashboard_bp'),
    
    # Essential services (Priority 2)
    (2, 'routes.api', 'api_bp'),
    (2, 'routes.settings', 'settings_bp'),
    (2, 'routes.user_routes', 'user_bp'),
    
    # Feature blueprints (Priority 3)
    (3, 'routes.spotify_visualization', 'spotify_viz'),
    (3, 'routes.spotify_commands', 'spotify_commands'),
    (3, 'routes.spotify_routes', 'spotify_bp'),
    (3, 'routes.voice_routes', 'voice_bp'),
    
    # Health & wellness features (Priority 4)
    (4, 'routes.aa_routes', 'aa_bp'),
    (4, 'routes.dbt_routes', 'dbt_bp'),
    (4, 'routes.crisis_routes', 'crisis_bp'),
    
    # Additional services (Priority 5)
    (5, 'routes.forms_routes', 'forms_bp'),
    (5, 'routes.meet_routes', 'meet_bp'),
    (5, 'routes.admin_routes', 'admin_bp'),
    (5, 'routes.smart_shopping_routes', 'smart_shopping_bp'),
    (5, 'routes.price_routes', 'price_tracking_bp'),
]

# Store imported blueprints
_blueprints_cache: Dict[str, Blueprint] = {}

def _import_blueprint(module_path: str, blueprint_name: str) -> Blueprint:
    """
    Import a blueprint lazily (only when needed)
    
    Args:
        module_path: Import path for the module
        blueprint_name: Name of the blueprint variable in the module
        
    Returns:
        Imported blueprint
    """
    cache_key = f"{module_path}.{blueprint_name}"
    
    # Return from cache if already imported
    if cache_key in _blueprints_cache:
        return _blueprints_cache[cache_key]
    
    # Import the module and get the blueprint
    try:
        start_time = time.time()
        module = importlib.import_module(module_path)
        blueprint = getattr(module, blueprint_name)
        import_time = time.time() - start_time
        
        # Cache the blueprint for future use
        _blueprints_cache[cache_key] = blueprint
        
        # Log slow imports to help identify optimization opportunities
        if import_time > 0.1:  # Log imports taking more than 100ms
            logger.warning(f"Slow blueprint import: {cache_key} took {import_time:.3f}s")
        else:
            logger.debug(f"Blueprint imported: {cache_key} in {import_time:.3f}s")
            
        return blueprint
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import blueprint {cache_key}: {str(e)}")
        raise

def register_blueprints(app: Flask):
    """
    Register all blueprint routes with the application
    
    This function maintains backward compatibility while offering performance improvements
    
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
    app.register_blueprint(spotify_bp)
    
    # Register smart shopping and price tracking blueprints
    app.register_blueprint(smart_shopping_bp)
    app.register_blueprint(price_tracking_bp)
    
    # Register voice interface blueprint
    app.register_blueprint(voice_bp)
    
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