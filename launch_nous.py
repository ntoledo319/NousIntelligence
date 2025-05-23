#!/usr/bin/env python
"""
NOUS Personal Assistant - Simplified Launcher

This script provides a clean way to launch the NOUS application
with the proper configuration.
"""
import os
import sys
import importlib
import logging
from flask import Flask

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create a simplified version of the NOUS app for reliable deployment"""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    
    # Ensure required directories exist
    for directory in ['logs', 'flask_session', 'static', 'templates', 'instance', 'uploads']:
        os.makedirs(directory, exist_ok=True)
    
    # Import routes from app.py
    try:
        from app import index, health, page_not_found, server_error
        
        # Register basic routes
        app.route('/')(index)
        app.route('/health')(health)
        app.errorhandler(404)(page_not_found)
        app.errorhandler(500)(server_error)
        
        logger.info("Basic routes registered successfully")
    except ImportError as e:
        logger.error(f"Failed to import routes: {str(e)}")
        
        # Define fallback routes
        @app.route('/')
        def index():
            """Main landing page"""
            from flask import render_template
            return render_template('index.html', title="NOUS Personal Assistant")
        
        @app.route('/health')
        def health():
            """Health check endpoint"""
            from flask import jsonify
            from datetime import datetime
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'environment': os.environ.get('FLASK_ENV', 'production'),
                'timestamp': datetime.now().isoformat()
            })
            
    return app

def main():
    """Main entry point for the application"""
    # Set environment variables
    os.environ.setdefault('PORT', '5000')
    
    # Create the application
    app = create_app()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')

if __name__ == "__main__":
    logger.info("Starting NOUS Personal Assistant")
    main()