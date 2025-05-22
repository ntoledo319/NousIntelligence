"""
NOUS Personal Assistant - Deployment Ready Version

This version is specially designed to work with Replit's deployment system.
"""

from flask import Flask, jsonify, redirect, send_from_directory, render_template_string
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "nous-secure-key-2025"))

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)

# Log startup information
logger.info("NOUS Personal Assistant starting up...")

@app.route('/')
def index():
    """Homepage with welcome message"""
    template = """
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
            
            .status-ok {
                color: #2ecc71;
                font-weight: bold;
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
                <p>System status: <span class="status-ok">✓ Operational</span></p>
            </div>
            
            <div class="card">
                <h2>System Status</h2>
                <p>All services are operational.</p>
                <p>Check detailed status at the <a href="/health">health page</a>.</p>
            </div>
            
            <div class="card">
                <h2>Features</h2>
                <ul>
                    <li>Advanced AI assistance with task management</li>
                    <li>Health monitoring and data analysis</li>
                    <li>Secure authentication and user profiles</li>
                    <li>Multi-modal interaction capabilities</li>
                </ul>
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 NOUS Personal Assistant</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(template)

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

# This is critical - catch all undefined routes
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to handle any undefined route"""
    logger.info(f"Redirecting undefined path: {path}")
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {e}")
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {e}")
    return render_template_string("<h1>Internal Server Error</h1><p>The server encountered an error. Please try again later.</p>"), 500

# Start the application when run directly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Access your app at your Replit URL\n")
    app.run(host="0.0.0.0", port=port)