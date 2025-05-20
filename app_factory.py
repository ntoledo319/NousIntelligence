"""
Application Factory

This module provides the application factory for creating the Flask app.
It centralizes app creation and configuration.

@module app_factory
@description Flask application factory
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()

def create_app(config_class=None):
    """Create and configure the Flask application
    
    Args:
        config_class: Configuration class to use (defaults to from_env)
        
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        # If no config provided, load from environment
        from config import get_config
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    with app.app_context():
        # Import and register all blueprints
        from routes import register_blueprints
        register_blueprints(app)
        
        # Set up middleware
        from middleware import register_middleware
        register_middleware(app)
        
        # Create database tables if they don't exist
        db.create_all()
    
    return app

def configure_app(app):
    """
    Configure the application with settings from environment and config files
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Set basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nous.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Login configuration
    app.config['LOGIN_DISABLED'] = False
    
    # Set dev/production mode
    app.config['DEBUG'] = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Application configured with database: {app.config['SQLALCHEMY_DATABASE_URI']}")

def initialize_extensions(app):
    """
    Initialize Flask extensions
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create all database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader callback for Flask-Login
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    logger.info("Extensions initialized")

def configure_error_handlers(app):
    """
    Configure error handlers for the application
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Import and register error handlers
    try:
        from utils.error_handler import register_error_handlers
        register_error_handlers(app)
        logger.info("Error handlers registered")
    except Exception as e:
        logger.error(f"Error registering error handlers: {str(e)}")

def register_blueprints(app):
    """
    Register all blueprint routes
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Register route blueprints
    try:
        from routes import register_blueprints
        register_blueprints(app)
        logger.info("Route blueprints registered")
    except Exception as e:
        logger.error(f"Error registering route blueprints: {str(e)}")
    
    # Register authentication blueprints
    try:
        from auth import register_auth_providers
        register_auth_providers(app)
        logger.info("Authentication blueprints registered")
    except Exception as e:
        logger.error(f"Error registering authentication blueprints: {str(e)}")

def register_templates(app):
    """
    Register custom template filters and context processors
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Register template filters
    try:
        from utils.template_filters import register_template_filters
        register_template_filters(app)
        logger.info("Template filters registered")
    except Exception as e:
        logger.error(f"Error registering template filters: {str(e)}") 