"""
NOUS Personal Assistant - Application Entry Point

This module provides the Flask application instance for deployment.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

# Create and configure the application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Add ProxyFix middleware for proper handling of forwarded requests
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions
db.init_app(app)

# Create required directories
os.makedirs('static', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Define routes
@app.route('/')
def index():
    """Homepage with welcome message"""
    try:
        logger.info("Rendering index page")
        return render_template('index_public.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return f"""
        <html>
            <head><title>NOUS - Error Recovery</title></head>
            <body>
                <h1>NOUS Personal Assistant</h1>
                <p>We encountered an error, but we're still here! Please try refreshing the page.</p>
                <p>Error details (for debugging): {str(e)}</p>
            </body>
        </html>
        """

@app.route('/dashboard')
def dashboard():
    """Dashboard view"""
    try:
        logger.info("Rendering dashboard")
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return render_template('error.html', 
                              code=500, 
                              title="Dashboard Error", 
                              message=str(e))

@app.route('/health')
def health():
    """Health check endpoint"""
    # For API clients requesting JSON format
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "production"),
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    # For browser requests, return HTML page
    return render_template('health.html', 
                          version="1.0.0", 
                          environment=os.environ.get("FLASK_ENV", "production"),
                          timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/smart-shopping')
def smart_shopping():
    """Smart shopping homepage"""
    try:
        return render_template('smart_shopping/index.html')
    except Exception as e:
        logger.error(f"Error rendering smart shopping: {str(e)}")
        return render_template('error.html', 
                              code=500, 
                              title="Smart Shopping Error", 
                              message=str(e))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return render_template('error.html', 
                          code=404, 
                          title="Page Not Found", 
                          message="The requested page could not be found."), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    return render_template('error.html', 
                          code=500, 
                          title="Internal Server Error", 
                          message="The server encountered an error. Please try again later."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all uncaught exceptions"""
    logger.error(f"Uncaught exception: {str(e)}")
    return render_template('error.html', 
                          code=500, 
                          title="Server Error", 
                          message=f"An unexpected error occurred: {str(e)}"), 500

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Run the app when executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)