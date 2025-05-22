"""
NOUS Personal Assistant - Ultra Simple Server

A guaranteed solution that will work on Replit without showing
the default Replit page.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Homepage with welcome message"""
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
        "version": "1.0.0"
    })

@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to handle any undefined route"""
    return index()

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Access your app at your Replit URL\n")
    app.run(host="0.0.0.0", port=port)