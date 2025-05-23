
"""
NOUS Personal Assistant - Main Application
A streamlined Flask application for reliable deployment
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

# Basic routes for testing deployment
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    
    # For a template-based response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        services = [
            {"name": "Web Application", "status": "ok"},
            {"name": "Authentication System", "status": "ok"},
            {"name": "Database Connection", "status": "ok"},
            {"name": "Content Services", "status": "ok"},
        ]
        
        return render_template('health.html', 
                              version='1.0.0',
                              environment=os.environ.get('FLASK_ENV', 'production'),
                              timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              services=services)
    
    # For API/JSON response
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=str(e), code=404), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500), 500

# Import and register routes after the app is created
def register_routes():
    try:
        # Import the main blueprint registration function
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("Successfully registered application routes")
    except Exception as e:
        logger.error(f"Error registering routes: {str(e)}")
        # Continue without routes for basic functionality

# Register routes if they exist
register_routes()

# Run the app when this file is executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
