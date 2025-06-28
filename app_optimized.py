"""
Optimized Flask Application for Production
Fast startup, minimal overhead, maximum performance
"""
import os
import time
import logging
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, init_database

def create_optimized_app():
    """Create production-optimized Flask application"""
    app = Flask(__name__)
    
    # Production configuration
    app.config.update({
        'DEBUG': False,
        'TESTING': False,
        'SECRET_KEY': os.environ.get('SESSION_SECRET', 'production-key'),
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 5,
            'pool_timeout': 30,
            'echo': False,
        },
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
    })
    
    # Apply ProxyFix for production deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize database
    init_database(app)
    
    # Add health check endpoint
    @app.route('/health')
    @app.route('/healthz')
    def optimized_health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '0.2.0'
        }), 200
    
    # Import and register routes
    try:
        from app import create_app
        main_app = create_app()
        
        # Copy all routes from main app
        for rule in main_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                app.add_url_rule(
                    rule.rule,
                    rule.endpoint,
                    main_app.view_functions.get(rule.endpoint),
                    methods=rule.methods
                )
    except ImportError:
        logging.warning("Could not import main app routes")
    
    return app

# Create the optimized app instance
app = create_optimized_app()
