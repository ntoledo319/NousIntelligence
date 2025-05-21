"""
NOUS Personal Assistant - 100% Public Version

This version is specifically designed to be completely public on Replit
with no authentication requirements.
"""

import os
import logging
from flask import Flask, render_template, jsonify, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-public-secret-key")

# Routes
@app.route('/')
def index():
    """Homepage"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        # Simple HTML response as fallback
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS Personal Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>NOUS Personal Assistant</h1>
            <p>Your intelligent companion for daily tasks</p>
            <p>This is a fully public deployment of the NOUS application.</p>
            <p>You can access the API at <a href="/api/info">/api/info</a>.</p>
        </body>
        </html>
        '''

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/api/info')
def api_info():
    """API information"""
    return jsonify({
        "name": "NOUS Personal Assistant API",
        "version": "1.0.0",
        "status": "online",
        "public": True
    })

# Start the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # Log startup information
    logger.info(f"Starting NOUS Public Assistant on port {port}")
    
    # Start the application with public settings
    app.run(host="0.0.0.0", port=port)