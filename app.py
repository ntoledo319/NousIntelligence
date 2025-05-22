"""
NOUS Personal Assistant - Core Application Module

This is the main application module that provides a public interface
without requiring user login. It's optimized for fast loading and reliable
deployment on Replit.
"""

import os
import sys
import logging
import datetime
import platform
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", os.urandom(24).hex()))

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 20,
    "connect_args": {
        "connect_timeout": 10,
        "application_name": "NOUS",
    },
}

# Apply ProxyFix for proper URL generation with HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create database instance
db = SQLAlchemy(app)

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('templates/errors', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

@app.before_request
def before_request():
    """Redirect to HTTPS if not already secured"""
    if not request.is_secure and 'REPLIT_ENVIRONMENT' in os.environ:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.route('/')
def index():
    """Homepage - no login required"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {str(e)}")
        return jsonify({
            "status": "online",
            "message": "Welcome to NOUS Personal Assistant",
            "info": "The application is running correctly"
        })

@app.route('/health')
def health():
    """Health check endpoint for monitoring and diagnostics"""
    health_data = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
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

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "features": ["task_management", "information_retrieval", "data_analysis"]
    })

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "NOUS Personal Assistant API",
        "version": "1.0.0",
        "description": "Advanced AI-powered personal assistant web application",
        "endpoints": [
            {"path": "/", "description": "Homepage"},
            {"path": "/health", "description": "Health check endpoint"},
            {"path": "/api/status", "description": "Check API operational status"},
            {"path": "/api/info", "description": "API information"}
        ]
    })

# Legacy route handling - redirect old routes to home page
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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    if request.path.startswith('/api/'):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    try:
        return render_template('errors/404.html'), 404
    except:
        return app.send_static_file('error/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error", "status": 500}), 500
    try:
        return render_template('errors/500.html'), 500
    except:
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
    if request.path.startswith('/api/'):
        return jsonify(error="An unexpected error occurred. Please try again later."), 500
    try:
        return render_template('errors/500.html'), 500
    except:
        return jsonify(error="An unexpected error occurred. Please try again later."), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    logger.info(f"Debug mode: {debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)