"""
Main Application Entry Point

This is the single entry point for the NOUS personal assistant application.
The application is created using the factory pattern defined in app_factory.py.
"""

import os
import logging
import sys
from flask import redirect, request, url_for, abort, jsonify
from app_factory import create_app
from app_factory import db
from werkzeug.exceptions import HTTPException

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

app = create_app()

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

@app.before_request
def before_request():
    """Redirect to HTTPS and enforce primary domain if needed"""
    # Check if we're already on HTTPS
    if not request.is_secure and 'REPLIT_ENVIRONMENT' in os.environ:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return app.send_static_file('error/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    return app.send_static_file('error/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(e)}")
    
    # Pass through HTTP exceptions
    if isinstance(e, HTTPException):
        return e
    
    # Handle unexpected errors
    return jsonify(error="An unexpected error occurred. Please try again later."), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify(status="ok", version="1.0.0"), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host="0.0.0.0", port=port, debug=debug)