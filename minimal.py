"""
NOUS Personal Assistant - Minimal Version

A simple version that's guaranteed to run and deploy properly.
"""

import os
from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nous-deployment-key")

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        return render_template('minimal.html')
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running",
            "info": "Welcome to NOUS"
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Application running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'your-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)