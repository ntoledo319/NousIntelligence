"""
NOUS Personal Assistant - Single Consolidated Application
A completely public Flask application with no login required
"""
import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Create and configure Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Basic configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///instance/nous.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Ensure required directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('instance', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)

# Verify database connection
try:
    with app.app_context():
        db.engine.connect()
        logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Database connection failed: {str(e)}")
    # Don't crash the app, continue without database if needed

# Basic routes for public access
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    import psutil
    import platform
    from datetime import datetime
    
    # Check database connectivity
    db_status = "ok"
    db_message = "Connected"
    try:
        with app.app_context():
            db.engine.connect()
    except Exception as e:
        db_status = "error"
        db_message = str(e)
        logger.error(f"Health check: Database error: {str(e)}")
    
    # Check file system
    fs_status = "ok"
    try:
        if not os.path.exists("static/styles.css"):
            fs_status = "warning"
            logger.warning("Health check: Missing static files")
    except Exception:
        fs_status = "error"
        logger.error("Health check: File system error")
    
    # System resource information
    try:
        memory = psutil.virtual_memory()
        memory_used_percent = memory.percent
        memory_status = "ok" if memory_used_percent < 90 else "warning"
        
        disk = psutil.disk_usage('/')
        disk_used_percent = disk.percent
        disk_status = "ok" if disk_used_percent < 90 else "warning"
    except Exception as e:
        memory_status = "unknown"
        memory_used_percent = 0
        disk_status = "unknown"
        disk_used_percent = 0
        logger.error(f"Health check: System resource check error: {str(e)}")
    
    # Build services status
    services = [
        {"name": "Web Application", "status": "ok", "message": "Running"},
        {"name": "Database Connection", "status": db_status, "message": db_message},
        {"name": "File System", "status": fs_status, "message": "Static files available" if fs_status == "ok" else "Missing static files"},
        {"name": "Memory Usage", "status": memory_status, "message": f"{memory_used_percent}% used"},
        {"name": "Disk Usage", "status": disk_status, "message": f"{disk_used_percent}% used"}
    ]
    
    # Determine overall status
    if any(service["status"] == "error" for service in services):
        overall_status = "error"
    elif any(service["status"] == "warning" for service in services):
        overall_status = "warning"
    else:
        overall_status = "healthy"
    
    # Log health check
    logger.info(f"Health check: Status {overall_status}")
    
    # For a template-based response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        return render_template('health.html', 
                             version='1.0.0',
                             environment="production",
                             timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             overall_status=overall_status,
                             services=services,
                             system=platform.system(),
                             python_version=platform.python_version())
    
    # For API/JSON response
    return jsonify({
        'status': overall_status,
        'version': '1.0.0',
        'environment': "production",
        'timestamp': datetime.now().isoformat(),
        'services': {service["name"]: {"status": service["status"], "message": service["message"]} for service in services},
        'system': {
            'platform': platform.system(),
            'python_version': platform.python_version()
        }
    })

@app.route('/features')
def features():
    """Features overview page"""
    return render_template('features.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=str(e), code=404), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500), 500

# Add public header to all responses
@app.after_request
def add_public_header(response):
    response.headers['X-NOUS-Access'] = 'Public'
    return response

# Import and register routes if they exist
# Simple route registration without external dependencies
# This ensures the app works without requiring any extra modules
logger.info("Using standalone route configuration")

# Run the app when this file is executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting public server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)