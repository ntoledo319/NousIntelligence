"""
Main Routes Blueprint

This module defines the main routes for the NOUS application.
"""

from flask import Blueprint, jsonify, send_from_directory, render_template_string, render_template, redirect, request
import os
import logging
import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with welcome message"""
    return render_template('index.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    # For API clients requesting JSON format
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "production"),
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    # For browser requests, return HTML page
    return render_template('health.html', 
                          version="1.0.0", 
                          environment=os.environ.get("FLASK_ENV", "production"),
                          timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@main_bp.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

# Catch-all route to handle any undefined route
@main_bp.route('/<path:path>')
def catch_all(path):
    """Catch-all route to handle any undefined route"""
    logger.info(f"Redirecting undefined path: {path}")
    return redirect('/')