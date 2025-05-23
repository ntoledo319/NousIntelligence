"""
NOUS Personal Assistant - Simplified Deployment Application
This version is designed to ensure reliable deployment on Replit
"""
import os
import sys
from flask import Flask, render_template, jsonify

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Routes
@app.route('/')
def index():
    """Homepage with welcome message"""
    return render_template('index.html', title='NOUS Personal Assistant')

@app.route('/dashboard')
def dashboard():
    """Dashboard view"""
    return render_template('dashboard.html', title='Dashboard')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', title='Page Not Found', 
                          error_code=404, message="The page you requested was not found."), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', title='Server Error', 
                          error_code=500, message="An internal server error occurred."), 500

# Entry point for running the application
if __name__ == '__main__':
    # Get port from environment variable or use default 3000
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)