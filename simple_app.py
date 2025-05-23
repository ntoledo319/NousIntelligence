import os
from flask import Flask, jsonify

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Routes
@app.route('/')
def index():
    """Homepage with welcome message"""
    return "Welcome to NOUS Personal Assistant! The application is working correctly."

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Run the application
if __name__ == '__main__':
    # Try different ports until we find one that works
    for port in [3000, 4000, 5000, 6000, 7000]:
        try:
            app.run(host='0.0.0.0', port=port)
            break
        except OSError:
            print(f"Port {port} is in use, trying another...")