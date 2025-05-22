
import os
import sys
import logging
from flask import Flask, render_template, jsonify, send_from_directory, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nous")

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-key")

@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        return render_template('minimal.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running"
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS running on http://0.0.0.0:{port}\n")
    app.run(host='0.0.0.0', port=port)
