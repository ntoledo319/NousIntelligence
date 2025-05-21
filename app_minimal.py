"""
NOUS Personal Assistant - Minimal Deployment Version
This file provides a minimal version of the application that can be reliably deployed on Replit.
"""

import os
from flask import Flask, jsonify, render_template_string

# Create a basic Flask application that will reliably deploy
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-secret-key")

# Basic HTML template
HOMEPAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NOUS Personal Assistant</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #6f42c1;
            margin-top: 0;
        }
        .status {
            background-color: #e9f7ef;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 5px solid #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>NOUS Personal Assistant</h1>
        <p>Your personal assistant application is up and running.</p>
        
        <div class="status">
            <strong>Status:</strong> Online
            <br>
            <strong>Deployment:</strong> Success
        </div>
        
        <p>This is a simplified version of the application for reliable deployment.
        Once this is working, we can implement the full functionality.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the homepage with status information"""
    return render_template_string(HOMEPAGE_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "online",
        "version": "minimal-1.0",
        "environment": os.environ.get("FLASK_ENV", "production")
    })

if __name__ == '__main__':
    # Get the port from environment variable with fallback to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Run the app on the specified port, binding to all interfaces
    app.run(host='0.0.0.0', port=port)