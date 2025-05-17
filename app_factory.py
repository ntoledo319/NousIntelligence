"""
Application Factory Module

This module contains the application factory function that creates and configures
a Flask application instance using the specified configuration.
"""
import os
import logging
from flask import Flask, session
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from models import db, User
from config import get_config

# Initialize extension instances
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_object=None):
    """
    Application factory function to create and configure a Flask application.
    
    Args:
        config_object: Configuration object or name of configuration to use
                      If None, the configuration is determined by FLASK_ENV
    
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_object is None:
        config_object = get_config()
    app.config.from_object(config_object)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG if app.config.get('DEBUG') else logging.INFO)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Set up login manager
    login_manager.login_view = "google_auth.login"  # Redirects to Google login
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "info"
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(user_id)
    
    # Make session permanent
    @app.before_request
    def make_session_permanent():
        """Make session permanent with expiration from config"""
        session.permanent = True
    
    # Register components with app context
    with app.app_context():
        # Register authentication providers
        from auth import register_auth_providers
        register_auth_providers(app)
        
        # Import and register blueprints
        from routes import register_blueprints
        register_blueprints(app)
        
        # Import and register error handlers
        from utils.error_handler import register_error_handlers
        register_error_handlers(app)
        
        # Register template filters
        from utils.template_filters import register_template_filters
        register_template_filters(app)
        
        # Configure beta testing mode if available
        try:
            from utils.beta_test_helper import configure_beta_mode
            configure_beta_mode(app)
        except ImportError:
            logging.info("Beta test helper not available")
        
        # Create database tables if needed
        try:
            db.create_all()
            logging.info("Database tables created (if they didn't exist already)")
            
            # Start maintenance scheduler (if available)
            try:
                from utils.maintenance_helper import start_maintenance_scheduler
                start_maintenance_scheduler()
                logging.info("Maintenance scheduler started")
            except ImportError:
                logging.info("Maintenance scheduler not available")
                
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
    
    return app 