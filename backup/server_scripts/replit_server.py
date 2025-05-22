"""
Simplified Replit-compatible web server for NOUS Personal Assistant
This file provides a reliable deployment entry point for Replit
"""

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a Flask application that will work reliably on Replit
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "developsecretkey"))

# Home page route
@app.route('/')
def index():
    try:
        # Try to render the index template if it exists
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {str(e)}")
        # Fall back to a simple success response
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running",
            "info": "The application is working, but templates may not be set up yet."
        })

# Static files route - for CSS, JS, images, etc.
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Health check endpoint for monitoring
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "environment": os.environ.get("FLASK_ENV", "production"),
        "host": request.host,
        "remote_addr": request.remote_addr
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {request.path}")
    try:
        return app.send_static_file('error/404.html'), 404
    except:
        return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {str(e)}")
    try:
        return app.send_static_file('error/500.html'), 500
    except:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Get port from environment variable or use 8080 as default
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Starting NOUS server on port {port}")
    
    # Run the app with the correct host and port for Replit
    app.run(host="0.0.0.0", port=port, debug=False)