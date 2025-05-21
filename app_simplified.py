"""
NOUS Personal Assistant - Simplified Version

This is a simplified version of the NOUS application that's guaranteed to work
on Replit deployment. It provides the core functionality while being more
resilient to deployment issues.
"""

import os
import logging
from flask import Flask, jsonify, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET", os.urandom(24))

# Apply ProxyFix to ensure proper URL generation behind proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 20
}

# Initialize database
db = SQLAlchemy(app)

# Create database tables if configured to do so
if os.environ.get("AUTO_CREATE_TABLES", "false").lower() == "true":
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

# Define routes
@app.route('/')
def index():
    """Render homepage"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {str(e)}")
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running",
            "info": "This is a simplified version for reliable deployment"
        })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    health_data = {
        "status": "ok",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production")
    }
    
    # Check database connection if DATABASE_URL is available
    if os.environ.get("DATABASE_URL"):
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            health_data["database"] = "connected"
        except Exception as e:
            health_data["status"] = "degraded"
            health_data["database"] = f"error: {str(e)}"
    else:
        health_data["database"] = "not configured"
    
    return jsonify(health_data)

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "ok",
        "api_version": "1.0.0",
        "message": "API is operational"
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)