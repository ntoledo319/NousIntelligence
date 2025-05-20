"""
Application Factory

This module provides the application factory for creating the Flask app.
It centralizes app creation and configuration.

@module app_factory
@description Flask application factory - Optimized version
"""

import os
import logging
import time
from flask import Flask, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()

# Store a timestamp for startup performance measurement
_start_time = time.time()

# Enable SQLite foreign keys if using SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
    
    # Apply ProxyFix for proper URL generation with HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Setup logging
    log_level = logging.DEBUG if app.config.get('DEBUG', False) else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting NOUS application...")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    
    # Set up login manager
    login_manager.login_view = 'index'  # type: ignore # Default to index page if login route isn't available
    login_manager.login_message_category = 'info'
    
    # Configure user loader
    @login_manager.user_loader
    def load_user(user_id):
        # Import here to avoid circular imports
        from models import User
        return User.query.get(user_id)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    logger.info("Error handlers registered")
    
    # Register blueprints, middleware, and other components
    with app.app_context():
        try:
            # Import and register all blueprints
            from routes import register_blueprints
            register_blueprints(app)
            logger.info("All blueprints registered successfully")
            
            # Set up middleware
            from middleware import register_middleware
            register_middleware(app)
            logger.info("Middleware registered successfully")
            
            # Configure root route if not already defined
            if not app.view_functions.get('index'):
                @app.route('/')
                def index():
                    return render_template('index.html')
                logger.info("Root route registered")
            
            # Create database tables if they don't exist
            if app.config.get('AUTO_CREATE_TABLES', True):
                db.create_all()
                logger.info("Database tables created/verified")
                
            # Setup database optimization utilities if enabled
            if app.config.get('DB_OPTIMIZE', True):
                try:
                    from utils.db_optimizations import setup_db_optimizations
                    setup_db_optimizations(app)
                    logger.info("Database optimizations enabled")
                except ImportError:
                    logger.info("Database optimizations not available")
            
            # Initialize cache if available
            try:
                from utils.cache_helper import cache_helper
                # Warm up the cache with frequently used data
                cache_helper.warmup()
                logger.info("Cache initialized and warmed up")
            except (ImportError, AttributeError) as e:
                logger.info(f"Cache initialization skipped: {str(e)}")
                
            # Log startup performance
            startup_time = time.time() - _start_time
            logger.info(f"Application startup completed in {startup_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during application setup: {str(e)}")
            raise
    
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

# Remove the initialize_extensions function as we've moved this functionality into create_app

# Removed configure_error_handlers as we've integrated this directly into create_app

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