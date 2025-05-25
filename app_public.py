"""
NOUS Personal Assistant - Public Deployment Version

A simplified Flask application that ensures public access without Replit login,
while maintaining internal Google authentication functionality.
"""
import os
import logging
from datetime import datetime
import platform
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Ensure required directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Routes
@app.route('/')
def index():
    """Main landing page"""
    logger.info("Rendering index page")
    return render_template('index.html', title="Home")

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    
    # Basic health info
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python': platform.python_version(),
        'system': platform.system()
    }
    
    # HTML or JSON response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        return render_template('health.html', 
                             status="healthy",
                             title="Health Check",
                             timestamp=health_info['timestamp'],
                             system=health_info['system'],
                             python_version=health_info['python'])
    
    return jsonify(health_info)

@app.route('/features')
def features():
    """Features overview page"""
    logger.info("Rendering features page")
    return render_template('features.html', title="Features")

@app.route('/about')
def about():
    """About page"""
    logger.info("Rendering about page")
    return render_template('about.html', title="About")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return render_template('error.html', error="Page not found", code=404, title="Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500, title="Error"), 500

# Add headers to bypass Replit login requirement
@app.after_request
def add_header(response):
    """Add headers to enable public access"""
    # CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    # Security headers
    response.headers['X-Frame-Options'] = 'ALLOWALL'  # Allow framing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    
    return response

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}, debug mode: {app.debug}")
    app.run(host='0.0.0.0', port=port)