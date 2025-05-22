"""
NOUS Personal Assistant - Public Version

A simplified, reliable version designed for public use without login requirements.
"""

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory, request, redirect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        return render_template('minimal.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS Personal Assistant</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #4a6fa5; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NOUS Personal Assistant</h1>
                <p>Your AI-powered personal assistant is up and running!</p>
                <p>System Status: <strong>Operational</strong></p>
                <p><a href="/health">Check System Health</a></p>
            </div>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production"),
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", logging.INFO, "", 0, "", (), None))
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.before_request
def before_request():
    """Redirect to HTTPS if not already secured"""
    # Check if we're already on HTTPS
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Page not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'your-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)