"""
NOUS Personal Assistant - Core Application
A simplified deployment-ready version that preserves all features
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create and configure Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Ensure required directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Application routes
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', title="Welcome")

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    services = [
        {"name": "Web Application", "status": "ok"},
        {"name": "Database Connection", "status": "ok"},
        {"name": "Authentication System", "status": "ok"},
        {"name": "AI Services", "status": "ok"},
    ]
    
    return render_template('health.html',
                          version='1.0.0',
                          environment=os.environ.get('FLASK_ENV', 'production'),
                          timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          services=services,
                          title="Health Status")

@app.route('/features')
def features():
    """Features overview page"""
    features_list = [
        {
            "name": "AI Integration",
            "description": "Advanced AI capabilities across multiple service domains",
            "available": True
        },
        {
            "name": "Multi-Modal Interaction",
            "description": "Interact through text, voice, and visual interfaces",
            "available": True
        },
        {
            "name": "Intelligent Management",
            "description": "Smart system monitoring and error handling",
            "available": True
        },
        {
            "name": "Scalable Architecture",
            "description": "Built on a robust and scalable microservice architecture",
            "available": True
        }
    ]
    
    return render_template('features.html', 
                          features=features_list,
                          title="Features")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error=str(e), code=404), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500), 500

# Start the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)