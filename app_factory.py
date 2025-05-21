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
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
import sqlite3

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()
csrf = CSRFProtect()

# Store a timestamp for startup performance measurement
_start_time = time.time()

# Enable SQLite foreign keys if using SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@event.listens_for(Engine, "engine_connect")
def ping_connection(connection, branch):
    """Ensure database connections are alive and reset them if needed"""
    if branch:
        # Don't ping on sub-connections (like inside a transaction)
        return

    # Add health check for PostgreSQL connections
    try:
        # Run a simple statement to check connection
        connection.scalar(text("SELECT 1"))
    except Exception:
        # Connection is invalid - dispose and get a new connection
        logging.warning("Database connection invalid, reconnecting...")
        connection.connection.close()
        raise  # Force SQLAlchemy to reconnect

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
    
    # Setup logging only if the root logger has no handlers (avoid double logging
    # when gunicorn or another WSGI server already configured logging).
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        log_level = logging.DEBUG if app.config.get('DEBUG', False) else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    logger = logging.getLogger(__name__)
    logger.info("Starting NOUS application...")
    
    # Ensure a secure SECRET_KEY is configured (defence in depth – already checked
    # in config.py, but validate here in case create_app is invoked with a custom
    # config object).
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("SECRET_KEY must be configured before creating the Flask app.")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection
    
    # Set up login manager to use Google authentication
    # Configure login options manually to avoid type issues
    # Using setattr to bypass type checking issues with login_manager properties
    setattr(login_manager, 'login_view', 'auth.login')  # Redirect to login page
    setattr(login_manager, 'login_message', 'Please sign in to access this page.')
    setattr(login_manager, 'login_message_category', 'info')
    
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
    
    # Register other common error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
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
            
            # Create database tables only when explicitly enabled.
            if app.config.get('AUTO_CREATE_TABLES', False):
                logger.warning("AUTO_CREATE_TABLES is enabled – creating tables automatically.")
                db.create_all()
                logger.info("Database tables created/verified")
                
                # Create default admin user if no users exist
                try:
                    from utils.create_default_user import create_default_admin
                    create_default_admin(app, db)
                except ImportError:
                    logger.warning("Could not import create_default_user module")
                except Exception as e:
                    logger.warning(f"Error creating default user: {str(e)}")
                
            # Setup database optimization utilities if enabled
            if app.config.get('DB_OPTIMIZE', True):
                try:
                    from utils.db_optimizations import setup_db_optimizations
                    setup_db_optimizations(app)
                    logger.info("Database optimizations enabled")
                    
                    # Apply custom query optimizations
                    if hasattr(db.session, 'execute'):
                        # Pre-warm system settings cache to reduce repeated queries
                        try:
                            from sqlalchemy import text
                            with db.session.begin():
                                db.session.execute(text("SELECT key, value FROM system_settings"))
                            logger.info("System settings pre-warmed")
                        except Exception as e:
                            logger.warning(f"Could not pre-warm settings: {str(e)}")
                except ImportError:
                    logger.info("Database optimizations not available")
                except Exception as e:
                    logger.warning(f"Failed to apply custom query optimizations: {str(e)}")
            
            # Load AA content if enabled
            if app.config.get('LOAD_AA_CONTENT', True):
                try:
                    from utils.aa_content_loader import load_aa_content
                    logger.info("Loading AA content...")
                    result = load_aa_content()
                    if all(result.values()):
                        logger.info("AA content loaded successfully")
                    else:
                        logger.warning(f"Some AA content failed to load: {result}")
                except ImportError:
                    logger.info("AA content loader not available")
                except Exception as e:
                    logger.warning(f"Failed to load AA content: {str(e)}")
                
            # Initialize cache if available
            try:
                from utils.cache_helper import cache_helper
                # Warm up the cache with frequently used data
                cache_helper.warmup()
                logger.info("Cache initialized and warmed up")
            except (ImportError, AttributeError) as e:
                logger.info(f"Cache initialization skipped: {str(e)}")
                
            # Initialize settings cache
            try:
                from utils.settings_cache import initialize_settings_cache
                initialize_settings_cache()
            except ImportError:
                logger.info("Settings cache initialization skipped")
                
            # Register template filters
            try:
                from utils.template_filters import register_template_filters
                register_template_filters(app)
                logger.info("Template filters registered")
            except Exception as e:
                logger.error(f"Error registering template filters: {str(e)}")
                
            # Log startup performance
            startup_time = time.time() - _start_time
            logger.info(f"Application startup completed in {startup_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during application setup: {str(e)}")
            raise
    
    return app

