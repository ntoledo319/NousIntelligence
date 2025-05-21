#!/usr/bin/env python3
"""
Simple Flask Server for Deployment

This is a simplified version of the app that's guaranteed to deploy successfully.
It provides basic endpoints while maintaining compatibility with the main application.
"""

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deploy_app')

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET", "nous-deployment-key")

@app.route('/')
def index():
    """Render homepage"""
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running",
            "info": "This is a simplified deployment version"
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)