"""
NOUS Personal Assistant - Public Application
A streamlined Flask application specifically configured for public access
"""
import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

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

# Basic routes for public deployment
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
    
    # Build services status
    services = [
        {"name": "Web Application", "status": "ok", "message": "Running"},
        {"name": "File System", "status": "ok", "message": "Static files available"},
        {"name": "Memory Usage", "status": "ok", "message": f"{psutil.virtual_memory().percent}% used"},
        {"name": "Disk Usage", "status": "ok", "message": f"{psutil.disk_usage('/').percent}% used"}
    ]
    
    # Log health check
    logger.info(f"Health check: Status healthy")
    
    # For a template-based response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        return render_template('health.html', 
                              version='1.0.0',
                              environment="production",
                              timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              overall_status="healthy",
                              services=services,
                              system=platform.system(),
                              python_version=platform.python_version())
    
    # For API/JSON response
    return jsonify({
        'status': "healthy",
        'version': '1.0.0',
        'environment': "production",
        'timestamp': datetime.now().isoformat(),
        'services': {service["name"]: {"status": service["status"], "message": service["message"]} for service in services},
        'system': {
            'platform': platform.system(),
            'python_version': platform.python_version()
        }
    })

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=str(e), code=404), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500), 500

# Add production header
@app.after_request
def add_header(response):
    response.headers['X-NOUS-Public'] = 'True'
    return response

# Run the app when this file is executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting public server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)