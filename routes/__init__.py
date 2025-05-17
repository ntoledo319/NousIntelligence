"""
Route Registration Module

This module is responsible for registering all blueprint modules with the Flask application.
Add new blueprints here to make them available to the main app.

@module routes
@author NOUS Development Team
"""

def register_blueprints(app):
    """
    Register all blueprint modules with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Import blueprints from individual modules
    from routes.spotify_visualization import spotify_viz
    from routes.voice_emotion_routes import voice_emotion_bp
    from routes.async_api import async_api
    from routes.health_check import health_check
    from routes.auth_api import auth_api
    from routes.two_factor_routes import two_factor_bp
    from routes.api_key_routes import api_key_bp
    from routes.beta_routes import beta
    
    # Import our new view blueprints
    from routes.view.index import index_bp
    from routes.view.dashboard import dashboard_bp
    from routes.view.settings import settings_bp
    
    # Import API blueprints
    from routes.api.v1.settings import settings_bp as api_settings_bp
    from routes.api.v1.weather import weather_bp as api_weather_bp
    
    # Try to import other organized blueprints if available
    try:
        # API blueprints
        from routes.api.health import health_bp
        from routes.api.shopping import shopping_bp
        from routes.api.finance import finance_bp
        from routes.api.travel import travel_bp
        from routes.api.weather import weather_bp
        
        # View blueprints
        from routes.view.user import user_bp
        
        has_organized_blueprints = True
    except ImportError:
        has_organized_blueprints = False
    
    # Register flat structure blueprints
    app.register_blueprint(spotify_viz)
    app.register_blueprint(voice_emotion_bp)
    app.register_blueprint(async_api)
    app.register_blueprint(health_check)
    app.register_blueprint(auth_api)
    app.register_blueprint(two_factor_bp)
    app.register_blueprint(api_key_bp)
    app.register_blueprint(beta)
    
    # Register new view blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    
    # Register API blueprints
    app.register_blueprint(api_settings_bp)
    app.register_blueprint(api_weather_bp)
    
    # Register organized blueprints if available
    if has_organized_blueprints:
        # Register API blueprints
        app.register_blueprint(health_bp)
        app.register_blueprint(shopping_bp)
        app.register_blueprint(finance_bp)
        app.register_blueprint(travel_bp)
        app.register_blueprint(weather_bp)
        
        # Register view blueprints
        app.register_blueprint(user_bp)