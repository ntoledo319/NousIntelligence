"""
NOUS Personal Assistant - Public Deployment Version
This file provides a version of the application that can be publicly accessed without login.
"""

import os
from flask import Flask, jsonify, render_template_string

# Create a Flask application configured for public access
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-secret-key")

# Basic HTML template with improved styling
HOMEPAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NOUS Personal Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }
        .container {
            background-color: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #6f42c1;
            margin-top: 0;
        }
        .status {
            background-color: #e9f7ef;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 5px solid #27ae60;
        }
        .feature-list {
            margin-top: 30px;
        }
        .feature-list h2 {
            color: #5a32a3;
            font-size: 1.3em;
        }
        .feature-list ul {
            padding-left: 20px;
        }
        .feature-list li {
            margin-bottom: 8px;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>NOUS Personal Assistant</h1>
        <p>Your advanced AI-powered personal assistant application is up and running.</p>
        
        <div class="status">
            <strong>Status:</strong> Online
            <br>
            <strong>Deployment:</strong> Public Access Enabled
        </div>
        
        <div class="feature-list">
            <h2>System Features</h2>
            <ul>
                <li>AI-powered personal assistance</li>
                <li>Multi-modal interactions</li>
                <li>Robust deployment and monitoring</li>
                <li>Automated health checks</li>
                <li>Intelligent error recovery</li>
            </ul>
        </div>
        
        <footer>
            NOUS Personal Assistant - Deployed on Replit - {{ current_date }}
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the homepage with status information"""
    from datetime import datetime
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Render template with the current date
    return render_template_string(HOMEPAGE_TEMPLATE, current_date=current_date)

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "online",
        "version": "public-1.0",
        "environment": os.environ.get("FLASK_ENV", "production"),
        "database": "configured" if os.environ.get("DATABASE_URL") else "not configured"
    })

@app.route('/api/status')
def api_status():
    """Simple API endpoint for testing connectivity"""
    return jsonify({
        "service": "NOUS Personal Assistant",
        "status": "operational",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Get the port from environment variable with fallback to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Log startup information
    print(f"Starting NOUS Public Server on port {port}")
    print(f"Application will be available at: http://localhost:{port}/")
    
    # Run the app on the specified port, binding to all interfaces for public access
    app.run(host='0.0.0.0', port=port)