"""
NOUS Personal Assistant - Production Version

This version is optimized for stable deployment on Replit with proper database handling,
error recovery, and production-ready configuration.
"""

import os
import logging
from flask import Flask, jsonify, render_template, redirect, url_for, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET", os.urandom(24))

# Apply ProxyFix to ensure proper URL generation behind proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database with optimized connection pooling for production
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,          # Test connections before use
    "pool_recycle": 300,            # Recycle connections after 5 minutes
    "pool_size": 10,                # Connection pool size
    "max_overflow": 20,             # Allow more overflow connections when needed
    "pool_timeout": 20,             # Timeout for getting connection from pool
    "pool_use_lifo": True           # Use LIFO for better connection reuse
}

# Initialize database
db = SQLAlchemy(app)

# Create database tables if configured to do so
if os.environ.get("AUTO_CREATE_TABLES", "false").lower() == "true":
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

# Add middleware to ensure HTTPS is used when applicable
@app.before_request
def ensure_https():
    """Redirect to HTTPS when on Replit deployment"""
    if not request.is_secure and os.environ.get('REPLIT_ENVIRONMENT'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Define routes
@app.route('/')
def index():
    """Render homepage"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {str(e)}")
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running",
            "info": "Production-ready deployment version"
        })

@app.route('/health')
def health():
    """Enhanced health check endpoint for monitoring"""
    import platform
    import datetime
    
    health_data = {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }
    }
    
    # Check database connection
    if os.environ.get("DATABASE_URL"):
        try:
            from sqlalchemy import text
            start_time = time.time()
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            query_time = time.time() - start_time
            
            health_data["database"] = {
                "status": "connected",
                "query_time_ms": round(query_time * 1000, 2)
            }
        except Exception as e:
            health_data["status"] = "degraded"
            health_data["database"] = {
                "status": "error",
                "message": str(e)
            }
    else:
        health_data["database"] = {"status": "not configured"}
    
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
        health_data["disk"] = {"status": "error", "message": str(e)}
    
    # Status code based on overall health
    status_code = 200 if health_data["status"] == "ok" else 200  # Always return 200 for monitoring tools
    
    return jsonify(health_data), status_code

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "ok",
        "api_version": "1.0.0",
        "message": "API is operational"
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    try:
        return render_template('errors/404.html'), 404
    except:
        return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error", "status": 500}), 500
    try:
        return render_template('errors/500.html'), 500
    except:
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(e)}")
    
    # Add recovery attempt for database connection issues
    if "psycopg2.OperationalError" in str(e) or "sqlalchemy.exc.OperationalError" in str(e):
        logger.warning("Database connection error detected, attempting to reconnect...")
        try:
            db.session.rollback()
            db.session.close()
            db.engine.dispose()
            logger.info("Database connection pool reset")
        except Exception as db_err:
            logger.error(f"Failed to reset database connection: {str(db_err)}")
    
    # Return a generic error response
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)