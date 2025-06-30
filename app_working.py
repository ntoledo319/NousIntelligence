"""
NOUS Personal Assistant - Secure Flask Application
Production-ready app with Google OAuth authentication and comprehensive security
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_login import LoginManager
# CORS not needed for basic setup
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with comprehensive backend stability features"""
    logger.info("🚀 Starting NOUS application creation...")

    # Initialize Flask app
    app = Flask(__name__)

    # Configure app from environment and config
    try:
        from config.app_config import AppConfig
        app.config.from_object(AppConfig)

        # Ensure database URI is set
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

        logger.info("✅ App configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise

    # ProxyFix for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database initialization
    try:
        from database import init_database
        init_database(app)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

    # User loader for Flask-Login
    def user_loader(user_id):
        """Load user by ID for Flask-Login"""
        try:
            from models.user import User
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"User loading error: {e}")
            return None

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.user_loader(user_loader)

    # Initialize Google OAuth
    try:
        from utils.google_oauth import init_oauth
        init_oauth(app)
        logger.info("✅ Google OAuth initialized successfully")
    except Exception as e:
        logger.warning(f"Google OAuth initialization failed: {e}")

    # Register all application blueprints
    try:
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("✅ All blueprints registered successfully")
    except Exception as e:
        logger.error(f"Blueprint registration failed: {e}")
        raise

    # Security headers for public deployment
    @app.after_request
    def add_security_headers(response):
        """Add security headers for public deployment"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    logger.info("✅ NOUS application created successfully")
    return app

# Global app instance for deployment
try:
    app = create_app()
    logger.info("🎯 NOUS application ready for deployment")
except Exception as e:
    logger.error(f"❌ Application creation failed: {e}")
    raise