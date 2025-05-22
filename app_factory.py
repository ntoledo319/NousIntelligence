"""
NOUS Personal Assistant - Application Factory

This module provides a factory function for creating and configuring
the Flask application with all necessary extensions, blueprints, and middleware.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

def create_app(test_config=None):
    """Create and configure the Flask application

    Args:
        test_config: Configuration dictionary for testing (optional)

    Returns:
        Configured Flask application
    """
    # Create the Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if test_config is None:
        # Load configuration from config module based on environment
        from config import get_config
        app.config.from_object(get_config())
    else:
        # Use test configuration
        app.config.from_mapping(test_config)

    # Create required directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    # Add ProxyFix middleware for proper handling of forwarded requests
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Setup public preview mode for Replit deployment
    setup_public_preview_mode(app)
    
    # Register blueprints and routes
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database
    from models.database import init_db
    init_db(app)
    
    # Log startup information
    logger.info("NOUS Personal Assistant initialized")
    
    return app
    
def setup_public_preview_mode(app):
    """Setup public preview mode for Replit deployment
    
    This disables login_required for Replit preview URLs
    
    Args:
        app: Flask application instance
    """
    # Public preview configuration
    app.config['PUBLIC_PREVIEW_MODE'] = True
    
    # Override Flask-Login's login_required decorator for Replit preview
    from flask import request, g
    from functools import wraps
    from flask_login import current_user
    
    # Store the original login_required decorator
    from flask_login import login_required as original_login_required
    
    # Create a modified login_required decorator
    def public_preview_login_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Check if this is a Replit preview URL
            is_replit_preview = (
                request.host.endswith('.repl.co') or 
                request.host.endswith('.replit.app') or 
                'REPLIT_DEPLOYMENT' in os.environ
            )
            
            # If it's a Replit preview, bypass login requirement
            if is_replit_preview and app.config['PUBLIC_PREVIEW_MODE']:
                # Set a flag for templates to know we're in preview mode
                g.public_preview = True
                return func(*args, **kwargs)
            
            # Otherwise, use the original login_required
            return original_login_required(func)(*args, **kwargs)
        
        return decorated_view
    
    # Replace the original login_required with our modified version
    import flask_login
    flask_login.login_required = public_preview_login_required
    
    logger.info("Public preview mode configured for Replit deployment")

def register_blueprints(app):
    """Register Flask blueprints

    Args:
        app: Flask application instance
    """
    # Import blueprints here to avoid circular imports
    from routes.main import main_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    # Add more blueprint registrations as needed
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    logger.info("Blueprints registered")

def register_error_handlers(app):
    """Register error handlers

    Args:
        app: Flask application instance
    """
    from flask import redirect, render_template
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        logger.warning(f"404 error: {e}")
        return render_template('error.html', 
                              code=404, 
                              title="Page Not Found", 
                              message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        logger.error(f"500 error: {e}")
        return render_template('error.html', 
                              code=500, 
                              title="Internal Server Error", 
                              message="The server encountered an error. Please try again later."), 500
    
    logger.info("Error handlers registered")