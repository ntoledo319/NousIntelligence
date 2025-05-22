"""
NOUS Personal Assistant - Clean Version

A simple version designed for reliable deployment.
"""

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        return render_template('minimal.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return jsonify({
            "status": "ok",
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
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Application running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'your-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)