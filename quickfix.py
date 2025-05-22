"""
NOUS Personal Assistant - Quick Fix Solution

This is a condensed single-file solution that should work reliably.
"""

import flask
import os

app = flask.Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NOUS Personal Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #4a6fa5;
                color: white;
                padding: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .logo {
                font-size: 1.8rem;
                font-weight: bold;
            }
            .main-content {
                margin: 40px 0;
            }
            .card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 2rem;
                margin-bottom: 2rem;
            }
            h1, h2 {
                color: #4a6fa5;
            }
            footer {
                background-color: #2c3e50;
                color: white;
                text-align: center;
                padding: 1rem 0;
                margin-top: 3rem;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">NOUS</div>
                </div>
            </div>
        </header>
        
        <div class="container">
            <div class="main-content">
                <h1>NOUS Personal Assistant</h1>
                <p>Your AI-powered personal assistant designed to help you manage tasks, analyze data, and provide intelligent recommendations.</p>
                
                <div class="card">
                    <h2>Welcome to NOUS</h2>
                    <p>The application is running correctly and ready to help you with your tasks.</p>
                </div>
                
                <div class="card">
                    <h2>System Status</h2>
                    <p><span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #2ecc71; margin-right: 8px;"></span> All systems operational</p>
                    <p>For detailed status information, check our <a href="/health">health page</a>.</p>
                </div>
            </div>
        </div>
        
        <footer>
            <div class="container">
                <p>&copy; 2025 NOUS Personal Assistant | Advanced AI-Powered Technology</p>
            </div>
        </footer>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return flask.jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production")
    })

port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)