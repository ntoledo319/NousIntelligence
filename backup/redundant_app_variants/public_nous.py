"""
NOUS Personal Assistant - Public Deployment Version

This version is optimized for public access on Replit with a clean interface
and essential functionality.
"""

import os
from flask import Flask, jsonify, render_template, request, send_from_directory

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-app-secret-key")

@app.route('/')
def index():
    """Home page"""
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running",
            "info": "Welcome to the public deployment"
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0"
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/info')
def api_info():
    """API info endpoint"""
    return jsonify({
        "name": "NOUS Personal Assistant",
        "description": "An advanced AI-powered personal assistant",
        "version": "1.0.0",
        "status": "online"
    })

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)