"""
NOUS Personal Assistant - Direct Version

A streamlined version designed for direct execution and reliable deployment.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, send_from_directory, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nous")

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "nous-secure-key-2025"))

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        logger.info("Rendering index page")
        return render_template('minimal.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running",
            "info": "Welcome to NOUS"
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production")
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {e}")
    if request.path.startswith('/api/'):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    try:
        return render_template('minimal.html'), 404
    except:
        return jsonify({"error": "Page not found", "status": 404}), 404

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'nous-app')}.replit.app\n")
    try:
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)