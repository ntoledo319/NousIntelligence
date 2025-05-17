"""
NOUS Application Entry Point

This module serves as the entry point for the NOUS application.
It initializes the Flask application and starts the development server.
"""
import os
import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Set up logging early
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET") or "change_this_in_production!"

# Use proxy fix for HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
database_url = os.environ.get("DATABASE_URL")
# Make sure DATABASE_URL is in the correct format for SQLAlchemy
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url:
    logger.info(f"Using database URL: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,     # Verify connections before using from pool
        'pool_recycle': 600,       # Recycle connections every 10 minutes
        'pool_size': 20,           # Maximum connections in pool
        'max_overflow': 10,        # Overflow connections
        'pool_timeout': 30,        # Timeout for getting a connection from pool (seconds)
        'pool_use_lifo': True,     # Use last-in-first-out to reduce number of open connections
    }
else:
    logger.error("No DATABASE_URL found in environment variables")
    
# Import db and models for initialization
from models import db, User, UserSettings

# Initialize database
db.init_app(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Route to our login function in the auth blueprint
login_manager.login_message = "Please sign in to access this page."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(user_id)

# Initialize authentication
from auth import init_auth
init_auth(app)

# Create the database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created (if they didn't exist already)")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Routes
@app.route("/")
def index():
    """Home page route"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page for authenticated users"""
    return render_template("dashboard.html", user=current_user)

@app.route("/settings")
@login_required
def settings():
    """User settings page"""
    return render_template("settings.html", user=current_user, settings=current_user.settings)

# Health check endpoint
@app.route("/health")
def health_check():
    """Health check endpoint for monitoring system health"""
    try:
        # Simple database connectivity check
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "error"
    
    return {"status": "ok", "database": db_status, "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    # Get port from environment or use default 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Start the server
    app.run(host="0.0.0.0", port=port, debug=True)
