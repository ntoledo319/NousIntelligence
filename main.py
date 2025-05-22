"""
Main Application Entry Point - No Login Required

This is a modified version of the NOUS personal assistant application that
doesn't require any login. It provides a public interface to the app.
"""

import os
import logging
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
from sqlalchemy import text

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

# Configure enhanced deployment logging
try:
    from utils.deployment_logger import configure_deployment_logging, log_deployment_event
    deployment_logger = configure_deployment_logging()
    log_deployment_event('startup', 'Public application starting up')
except ImportError:
    logger.warning("Deployment logger not available, using standard logging only")
    deployment_logger = None

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Apply ProxyFix for proper URL generation with HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create database instance
db = SQLAlchemy(app)

# Create directories if needed
os.makedirs('static', exist_ok=True)
os.makedirs('templates/errors', exist_ok=True)

@app.before_request
def before_request():
    """Redirect to HTTPS and enforce primary domain if needed"""
    # Check if we're already on HTTPS
    if not request.is_secure and 'REPLIT_ENVIRONMENT' in os.environ:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Main index route - no login required
@app.route('/')
def index():
    """Render homepage without requiring login"""
    return render_template('index_public.html')

# Health check endpoint for monitoring
@app.route('/health')
def health_status():
    """Health check endpoint for monitoring and diagnostics"""
    import datetime
    import platform
    
    health_data = {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "development"),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
        }
    }
    
    # Check database connection
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        health_data["database"] = "connected"
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["database"] = f"error: {str(e)}"
    
    return jsonify(health_data)

# API status route 
@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "features": ["task_management", "information_retrieval", "data_analysis"]
    })

# API info route
@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "NOUS Personal Assistant API",
        "version": "1.0.0",
        "description": "Access the features of NOUS programmatically",
        "endpoints": [
            {
                "path": "/api/status",
                "method": "GET",
                "description": "Check API operational status"
            },
            {
                "path": "/api/info",
                "method": "GET",
                "description": "Get API documentation"
            }
        ]
    })

# Legacy route handling - for backward compatibility
@app.route('/dashboard')
@app.route('/login')
@app.route('/auth/login')
def redirect_to_home():
    """Redirect old routes to home page"""
    return redirect(url_for('index'))

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

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
    """Handle all uncaught exceptions with improved error logging and recovery"""
    # Get exception details
    import traceback
    error_traceback = traceback.format_exc()
    
    # Log the full error with traceback for debugging
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(f"Traceback: {error_traceback}")
    
    # Pass through HTTP exceptions (maintain standard HTTP error handling)
    if isinstance(e, HTTPException):
        return e
    
    # Database connection errors - attempt to reconnect
    if 'psycopg2.OperationalError' in error_traceback:
        logger.warning("Database connection error detected, attempting to reconnect...")
        try:
            db.session.rollback()  # Roll back any active transaction
            db.session.close()     # Close the current session
            db.engine.dispose()    # Dispose all connections in the pool
            logger.info("Database connection pool reset successfully")
        except Exception as db_err:
            logger.error(f"Failed to reset database connection: {str(db_err)}")
    
    # Application state errors - attempt to recover application state
    if 'RuntimeError: Working outside of application context' in error_traceback:
        logger.warning("Application context error detected, attempting to recover...")
        try:
            with app.app_context():
                logger.info("Application context temporarily established for recovery")
        except Exception as app_err:
            logger.error(f"Failed to recover application context: {str(app_err)}")
    
    # Handle unexpected errors with a user-friendly response
    return jsonify(error="An unexpected error occurred. Please try again later."), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host="0.0.0.0", port=port, debug=debug)