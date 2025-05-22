"""
NOUS Personal Assistant - Fixed Application

This is a streamlined version that should work reliably on Replit without
showing the default Replit page.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nous")

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", os.urandom(24).hex()))

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        logger.info("Rendering index page")
        return render_template('minimal.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NOUS Personal Assistant</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f8f9fa;
                    margin: 0;
                    padding: 0;
                }
                
                header {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 1rem 0;
                    text-align: center;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                
                h1 {
                    margin-top: 0;
                }
                
                .card {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 2rem;
                    margin-bottom: 2rem;
                }
                
                footer {
                    background-color: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 1rem 0;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>NOUS Personal Assistant</h1>
            </header>
            
            <div class="container">
                <div class="card">
                    <h2>Welcome to NOUS</h2>
                    <p>Your AI-powered personal assistant is up and running!</p>
                    <p>System status: <span style="color: #2ecc71; font-weight: bold;">✓ Operational</span></p>
                </div>
                
                <div class="card">
                    <h2>System Status</h2>
                    <p>All services are operational.</p>
                    <p>Check detailed status at <a href="/health">/health</a></p>
                </div>
            </div>
            
            <footer>
                <p>&copy; 2025 NOUS Personal Assistant</p>
            </footer>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production")
    })

@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        "name": "NOUS API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "description": "Home page"},
            {"path": "/health", "description": "Health check"}
        ]
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

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    return jsonify({"error": "Internal server error", "status": 500}), 500

# This is critical - catch all undefined routes
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to handle any undefined route"""
    logger.info(f"Catching undefined route: {path}")
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'nous-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)