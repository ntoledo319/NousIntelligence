"""
Routes initialization module
Centralizes the registration of all application blueprints
"""

from flask import Blueprint, Flask

def register_all_blueprints(app):
    """
    Register all application blueprints with the Flask app

    Args:
        app: Flask application instance
    """
    # Import and register main routes
    from routes.main import main_bp
    app.register_blueprint(main_bp)

    # Import and register API routes
    from routes.api.health import health_bp
    app.register_blueprint(health_bp, url_prefix='/api')

    # Only import additional routes if they exist
    try:
        from routes.aa_routes import aa_bp
        app.register_blueprint(aa_bp, url_prefix='/aa')
    except ImportError:
        pass

    try:
        from routes.user_routes import user_bp
        app.register_blueprint(user_bp, url_prefix='/user')
    except ImportError:
        pass

    try:
        from routes.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    except ImportError:
        pass

    # Add other blueprint registrations as needed

    return app