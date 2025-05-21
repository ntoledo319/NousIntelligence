import os
from flask import Flask, jsonify, render_template, send_from_directory

# Create a minimal Flask application
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "developsecretkey")

# Root route - send a welcome message
@app.route('/')
def index():
    try:
        # Try to render the index template if it exists
        return render_template('index.html')
    except:
        # Fall back to a simple JSON response
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running",
            "service": "Welcome to NOUS Personal Assistant"
        })

# Static files route
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "environment": os.environ.get("FLASK_ENV", "production"),
        "version": "1.0.0"
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Get port from environment variable or use 8080 as default
    port = int(os.environ.get("PORT", 8080))
    
    # Run the app with the correct host and port
    app.run(host="0.0.0.0", port=port, debug=False)