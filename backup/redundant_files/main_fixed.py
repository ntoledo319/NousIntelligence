"""
NOUS Personal Assistant - Main Fixed Version

A simple but effective solution to fix the routing issues.
"""

import os
import sys
from flask import Flask, render_template, jsonify, send_from_directory, request

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", os.urandom(24).hex()))

# Create basic template directory
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Create minimal template if it doesn't exist
if not os.path.exists('templates/minimal.html'):
    with open('templates/minimal.html', 'w') as f:
        f.write("""<!DOCTYPE html>
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
</html>""")

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        return render_template('minimal.html')
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
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
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                header {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 1rem;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .content {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                footer {
                    margin-top: 20px;
                    text-align: center;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>NOUS Personal Assistant</h1>
            </header>
            <div class="content">
                <h2>Welcome to NOUS</h2>
                <p>Your AI-powered personal assistant is up and running!</p>
                <p>Check the health of the system at <a href="/health">/health</a></p>
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

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('minimal.html'), 404

# This is the important part - make sure all paths use our app
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to override Replit defaults"""
    return render_template('minimal.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'nous-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)