"""
Route Registration Module

This module is responsible for registering all blueprint modules with the Flask application.
Add new blueprints here to make them available to the main app.

@module: routes
@author: NOUS Development Team
"""
# Import routes to make them available for registration with Flask app
from routes.spotify_visualization import spotify_viz
from routes.voice_emotion_routes import voice_emotion_bp
from routes.async_api import async_api
from routes.health_check import health_check
from routes.auth_api import auth_api
from routes.two_factor_routes import two_factor_bp
from routes.api_key_routes import api_key_bp

def register_blueprints(app):
    """Register all blueprint modules with the Flask application"""
    app.register_blueprint(spotify_viz)
    app.register_blueprint(voice_emotion_bp)
    app.register_blueprint(async_api)
    app.register_blueprint(health_check)
    app.register_blueprint(auth_api)
    app.register_blueprint(two_factor_bp)
    app.register_blueprint(api_key_bp)