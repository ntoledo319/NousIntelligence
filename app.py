
"""
NOUS Personal Assistant - Main Application
A robust, production-ready Flask application with standardized routes
"""
import os
import logging
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """
    Application factory pattern to create and configure the Flask app
    
    Returns:
        Flask application instance
    """
    # Create and configure Flask application
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Load configuration
    app.config.from_object('config.get_config()')
    app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/application.log')
        ]
    )
    
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Register all blueprints
    from routes import register_all_blueprints
    register_all_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Set up additional middleware and utilities
    setup_middleware(app)
    
    return app

# Import the more comprehensive error handlers
from error_handlers import register_error_handlers

# Import the comprehensive middleware setup
from middleware import setup_middleware

# Create the Flask application
app = create_app()

# Run the app when this file is executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
