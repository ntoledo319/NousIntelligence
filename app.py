
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

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('errors/404.html', title='Page Not Found', 
                            error_code=404, message="The page you requested was not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        return render_template('errors/500.html', title='Server Error', 
                            error_code=500, message="An internal server error occurred."), 500

def setup_middleware(app):
    """Set up middleware and utilities for the application"""
    # Try to apply security middleware if available
    try:
        from utils.security_middleware import setup_security_middleware
        setup_security_middleware(app)
    except ImportError:
        pass
    
    # Try to set up database optimizations if available
    try:
        from utils.db_optimizations import setup_db_optimizations
        setup_db_optimizations(app)
    except ImportError:
        pass

# Create the Flask application
app = create_app()

# Run the app when this file is executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
