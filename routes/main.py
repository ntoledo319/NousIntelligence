"""
Main Routes Blueprint

This module defines the main routes for the NOUS application.
"""

from flask import Blueprint, jsonify, send_from_directory, render_template_string, render_template, redirect, request, url_for, current_app
import os
import logging
import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint with standard naming
main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('/')
def index():
    """Homepage with welcome message"""
    try:
        # Get the flask app instance
        from flask import g
        
        # Log debugging information
        logger.info("Rendering index page")
        logger.info(f"PUBLIC_ACCESS: {current_app.config.get('PUBLIC_ACCESS', False)}")
        logger.info(f"PUBLIC_PREVIEW_MODE: {current_app.config.get('PUBLIC_PREVIEW_MODE', False)}")
        logger.info(f"Request host: {request.host}")
        
        # Check if public preview is enabled
        is_public = getattr(g, 'public_preview', False)
        logger.info(f"Is public preview (g.public_preview): {is_public}")
        
        # Use the public index for demonstration purposes
        return render_template('index_public.html', title='NOUS Personal Assistant')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        logger.exception("Full traceback for index error:")
        return render_template_string("""
            <html>
                <head><title>NOUS - Error Recovery</title></head>
                <body>
                    <h1>NOUS Personal Assistant</h1>
                    <p>We encountered an error, but we're still here! Please try refreshing the page.</p>
                    <p>Error details (for debugging): {{ error_message }}</p>
                </body>
            </html>
        """, error_message=str(e))

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard route"""
    try:
        return render_template('dashboard.html', title='Dashboard')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # Fallback to simple template if dashboard template is missing
        return render_template('minimal.html', title='Dashboard')

@main_bp.route('/help')
def help():
    """Help page route"""
    return render_template('help.html', title='Help')

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
    return redirect(url_for('main.index'))
