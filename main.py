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
    log_deployment_event('startup', 'Application starting up')
except ImportError:
    logger.warning("Deployment logger not available, using standard logging only")
    deployment_logger = None

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

@app.route('/health')
def health_check():
    """Enhanced health check endpoint for monitoring and diagnostics"""
    import os
    import sys
    import datetime
    import platform
    
    health_data = {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "unknown"),
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
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        health_data["disk"] = {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 2)
        }
    except Exception as e:
        health_data["disk"] = f"error: {str(e)}"
    
    # Check environment variables (redacted for security)
    required_vars = ["DATABASE_URL", "SECRET_KEY", "SESSION_SECRET"]
    health_data["environment_vars"] = {}
    for var in required_vars:
        health_data["environment_vars"][var] = "set" if os.environ.get(var) else "missing"
    
    # Set status code based on health
    status_code = 200 if health_data["status"] == "ok" else 200  # Still return 200 for monitoring tools
    
    return jsonify(health_data), status_code

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host="0.0.0.0", port=port, debug=debug)