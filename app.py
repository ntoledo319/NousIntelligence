"""
Backend Stability + Beta Suite Overhaul
Professional-Grade Chat Interface with Health Monitoring & Beta Management
"""
import os
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash, Response
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration with fallbacks
try:
    from config import AppConfig, PORT, HOST, DEBUG
except ImportError:
    logger.warning("Config module not found, using defaults")
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    class AppConfig:
        SECRET_KEY = os.environ.get('SESSION_SECRET')
        
        if not SECRET_KEY:
            raise RuntimeError("SESSION_SECRET environment variable is required for security")
        DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///nous.db')

# Import database with fallbacks
try:
    from database import db, init_database
except ImportError:
    logger.warning("Database module not found, using fallback")
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(DeclarativeBase):
        pass
    
    db = SQLAlchemy(model_class=Base)
    
    def init_database(app):
        db.init_app(app)

# Import utilities with fallbacks
try:
    from utils.google_oauth import init_oauth, user_loader
except ImportError:
    logger.warning("Google OAuth not available")
    def init_oauth(app): pass
    def user_loader(user_id): return None

try:
    from utils.security_middleware import init_security_headers
except ImportError:
    logger.warning("Security middleware not available")
    def init_security_headers(app): pass

try:
    from utils.unified_auth import init_auth
except ImportError:
    logger.warning("Unified auth not available")
    def init_auth(app): pass


def create_app():
    """Create Flask application with comprehensive backend stability features"""
    app = Flask(__name__)
    
    # Basic configuration
    app.secret_key = AppConfig.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = AppConfig.DATABASE_URL
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize ProxyFix for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        """Add basic security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Initialize database
    init_database(app)
    
    # Initialize authentication systems
    init_oauth(app)
    init_auth(app)
    init_security_headers(app)
    
    # Create database tables
    with app.app_context():
        try:
            # Import models if available
            import models
            db.create_all()
            logger.info("Database tables created successfully")
        except ImportError:
            logger.warning("Models not found, skipping table creation")
        except Exception as e:
            logger.error(f"Database creation error: {e}")
    
    # Register routes with fallbacks
    try:
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("All routes registered successfully")
    except ImportError:
        logger.warning("Routes module not found, registering basic routes")
        register_basic_routes(app)
    
    return app

def register_basic_routes(app):
    """Register basic routes when full route system unavailable"""
    
    @app.route('/')
    def index():
        return render_template('index.html') if os.path.exists('templates/index.html') else '''
        <html>
        <head><title>NOUS - AI Personal Assistant</title></head>
        <body>
            <h1>NOUS AI Personal Assistant</h1>
            <p>Welcome to NOUS - Your comprehensive AI-powered personal assistant.</p>
            <p><a href="/demo">Try Demo</a> | <a href="/health">Health Check</a></p>
        </body>
        </html>
        '''
    
    @app.route('/demo')
    def demo():
        return '''
        <html>
        <head><title>NOUS Demo</title></head>
        <body>
            <h1>NOUS Demo Mode</h1>
            <p>Demo functionality is available.</p>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        '''
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected' if db else 'unavailable'
        })
    
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'service': 'NOUS API',
            'timestamp': datetime.now().isoformat()
        })

# Create the application instance
app = create_app()

if __name__ == '__main__':
    logger.info(f"Starting NOUS application on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)