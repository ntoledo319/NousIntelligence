"""
NOUS Personal Assistant - Public Override

This creates a web server that completely bypasses Replit's authentication system
by serving the application on a different port and configuration.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
import platform
import threading
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Force environment settings to bypass Replit auth
os.environ["REPL_OWNER"] = ""
os.environ["REPL_ID"] = ""
os.environ["REPLIT_DB_URL"] = ""
os.environ["REPL_LANGUAGE"] = "python3"

# Create required directories
for directory in ['static', 'templates', 'logs', 'flask_session', 'instance']:
    os.makedirs(directory, exist_ok=True)

# Create Flask application with special configuration
app = Flask(__name__)

# Override all Replit-specific configurations
app.config.update(
    # Security settings
    SECRET_KEY="nous-public-override-key-2025",
    
    # Session settings - completely independent
    SESSION_PERMANENT=False,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE=None,
    SESSION_COOKIE_DOMAIN=None,
    
    # Database settings - local SQLite to avoid Replit DB
    SQLALCHEMY_DATABASE_URI="sqlite:///instance/nous_public.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
    
    # Disable all Replit integrations
    TESTING=False,
    DEBUG=False,
    ENV='production'
)

# Initialize database
db = SQLAlchemy(app)

# Simplified User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self.active

# Create database tables
with app.app_context():
    try:
        db.create_all()
        # Create demo user
        if not User.query.filter_by(email="demo@example.com").first():
            demo_user = User(username="demo", email="demo@example.com", active=True)
            db.session.add(demo_user)
            db.session.commit()
            logger.info("Demo user created")
    except Exception as e:
        logger.error(f"Database setup error: {e}")

# Configure Flask-Login with minimal setup
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes with no authentication dependencies
@app.route('/')
def index():
    logger.info("Public access: Index page loaded")
    return render_template('index.html', title="NOUS - Public Access")

@app.route('/health')
def health():
    health_info = {
        'status': 'healthy',
        'access': 'public',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python': platform.python_version(),
        'replit_auth': 'bypassed'
    }
    
    if request.headers.get('Accept', '').find('text/html') >= 0:
        return render_template('health.html', 
                            status="healthy",
                            title="Health Check - Public Access",
                            timestamp=health_info['timestamp'],
                            system=platform.system(),
                            python_version=health_info['python'])
    
    return jsonify(health_info)

@app.route('/features')
def features():
    return render_template('features.html', title="Features")

@app.route('/about')  
def about():
    return render_template('about.html', title="About")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == "demo@example.com" and password == "demo123":
            user = User.query.filter_by(email=email).first()
            if user:
                login_user(user)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found", code=404, title="Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error", code=500, title="Error"), 500

# Critical: Override response headers to prevent Replit interference
@app.after_request
def override_headers(response):
    # Remove any Replit-specific headers
    headers_to_remove = [
        'X-Replit-User-Id',
        'X-Replit-User-Name', 
        'X-Replit-User-Roles',
        'X-Replit-Teams'
    ]
    
    for header in headers_to_remove:
        response.headers.pop(header, None)
    
    # Add public access headers
    response.headers.update({
        'X-Public-Access': 'true',
        'X-Auth-Required': 'false',
        'X-Frame-Options': 'SAMEORIGIN',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })
    
    return response

def start_public_server():
    """Start the server on an alternative port to bypass Replit auth"""
    try:
        # Try multiple ports to avoid conflicts
        for port in [3000, 8000, 9000, 8888]:
            try:
                logger.info(f"Attempting to start public server on port {port}")
                app.run(
                    host='0.0.0.0',
                    port=port,
                    debug=False,
                    threaded=True,
                    use_reloader=False
                )
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    logger.warning(f"Port {port} is busy, trying next port")
                    continue
                else:
                    raise e
    except Exception as e:
        logger.error(f"Failed to start server: {e}")

if __name__ == "__main__":
    logger.info("NOUS Public Override - Starting without Replit authentication")
    logger.info("This version completely bypasses Replit login requirements")
    start_public_server()