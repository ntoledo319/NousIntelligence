#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
# This script ensures your application is publicly accessible without requiring login

echo "======= NOUS Public Deployment ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Create special .replit.deployment file to disable auth
cat > .replit.deployment << 'EOF'
[deployment]
run = ["sh", "-c", "python simple_app.py"]
deploymentTarget = "cloudrun"
ignorePorts = false

[auth]
pageEnabled = false
buttonEnabled = false
EOF

# Create special headers in our application
cat > simple_public_app.py << 'EOF'
"""
NOUS Personal Assistant - Public App
A streamlined Flask application with guaranteed public access
"""
import os
from flask import Flask, render_template, request, jsonify, Response, make_response

# Create a simple Flask app
app = Flask(__name__)
app.secret_key = "nous-secure-key-2025"

# Ensure required directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Add headers to ensure public access
@app.after_request
def add_public_header(response):
    """Add headers that ensure public access without login"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

# Basic routes
@app.route('/')
def index():
    """Main landing page"""
    response = make_response(render_template('index.html', title="Home"))
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    import platform
    from datetime import datetime
    
    # Basic health info
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python': platform.python_version(),
        'system': platform.system()
    }
    
    # HTML or JSON response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        response = make_response(render_template('health.html', 
                             status="healthy",
                             title="Health Check",
                             timestamp=health_info['timestamp'],
                             system=health_info['system'],
                             python_version=health_info['python']))
        response.headers['X-Replit-Auth-Bypass'] = 'true'
        return response
    
    response = make_response(jsonify(health_info))
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

@app.route('/about')
def about():
    """About page"""
    response = make_response(render_template('about.html', title="About"))
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

@app.route('/features')
def features():
    """Features page"""
    response = make_response(render_template('features.html', title="Features"))
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('error.html', error="Page not found", code=404, title="Not Found"), 404)
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

@app.errorhandler(500)
def server_error(e):
    response = make_response(render_template('error.html', error="Internal server error", code=500, title="Error"), 500)
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    return response

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

# Set environment variables for public access
export PORT=8080
export FLASK_APP=simple_public_app.py
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

echo "Starting public app on port 8080..."
python simple_public_app.py