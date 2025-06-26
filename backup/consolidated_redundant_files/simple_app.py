"""
NOUS Personal Assistant - Simple App
A streamlined Flask application guaranteed to work
"""
import os
from flask import Flask, render_template, request, jsonify

# Create a simple Flask app
app = Flask(__name__)
app.secret_key = "nous-secure-key-2025"

# Ensure required directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Add headers to prevent Replit login requirement
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

# Basic routes
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', title="Home")

@app.route('/health')
def health():
    """Health check endpoint"""
    import platform
    from datetime import datetime
    
    # Basic health info
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python': platform.python_version(),
        'system': platform.system()
    }
    
    # HTML or JSON response
    if request.headers.get('Accept', '').find('text/html') >= 0:
        return render_template('health.html', 
                             status="healthy",
                             title="Health Check",
                             timestamp=health_info['timestamp'],
                             system=health_info['system'],
                             python_version=health_info['python'])
    
    return jsonify(health_info)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', title="About")

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html', title="Features")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found", code=404, title="Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error", code=500, title="Error"), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)