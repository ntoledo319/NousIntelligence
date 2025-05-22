"""
NOUS Personal Assistant - Public Version

This is a public version of NOUS that doesn't require any login.
It provides basic features and API access without authentication.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Check and create directories
os.makedirs('static', exist_ok=True)
os.makedirs('templates/errors', exist_ok=True)

# Main index route - no login required
@app.route('/')
def index():
    """Render homepage without requiring login"""
    return render_template('index_public.html')

# Health check endpoint for monitoring
@app.route('/health')
def health():
    """Health check endpoint"""
    health_data = {
        "status": "ok",
        "timestamp": str(os.path.getmtime(__file__)),
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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"NOUS Public Assistant starting on {host}:{port}")
    app.run(host=host, port=port, debug=debug)