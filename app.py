"""
Main application module
======================

This module initializes the NOUS Assistant Flask application and registers all routes.
"""

from flask import Flask, render_template
from flask_login import LoginManager
import logging
import os

# Import blueprints
from routes.meet_routes import meet_bp
from routes.chat_routes import chat_bp, chat_api_bp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_pyfile('config.py')
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    app.register_blueprint(meet_bp)
    
    # Register chat blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_api_bp)
    
    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))