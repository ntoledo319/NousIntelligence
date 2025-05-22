"""
NOUS Personal Assistant - Default Entry Point

This is the simplest possible entry point for the Replit environment.
"""

from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Homepage"""
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
            <p>This is a clean version of the app that should display correctly.</p>
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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)