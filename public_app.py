"""
NOUS Personal Assistant - Public Web Application

This is the main entry point for the deployed public version of the NOUS
personal assistant application, optimized for Replit deployment.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Routes
@app.route('/')
def index():
    """Homepage with welcome message and features"""
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
    """Health check endpoint"""
    import platform
    import datetime
    
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "platform": platform.platform()
    })

@app.route('/api/info')
def api_info():
    """API information"""
    return jsonify({
        "name": "NOUS Personal Assistant API",
        "version": "1.0.0",
        "description": "Advanced AI-powered personal assistant web application",
        "endpoints": [
            {"path": "/", "description": "Homepage"},
            {"path": "/health", "description": "Health check endpoint"},
            {"path": "/api/info", "description": "API information"}
        ]
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
    logger.error(f"Server error: {str(e)}")
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error", "status": 500}), 500
    try:
        return render_template('errors/500.html'), 500
    except:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    
    # Log startup information
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the application
    app.run(host="0.0.0.0", port=port, debug=debug)