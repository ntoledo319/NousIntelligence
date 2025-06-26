"""
NOUS Personal Assistant - Deployment Script

This script directly runs the Flask application with public access settings.
Designed to work with the Replit deploy button with minimal complexity.
"""
import os
import sys
import logging
import json
import uuid
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create required directories
dirs = ['static', 'templates', 'logs', 'flask_session', 'instance']
for directory in dirs:
    os.makedirs(directory, exist_ok=True)

# Set environment variables
os.environ["PORT"] = "8080"
os.environ["PUBLIC_ACCESS"] = "true"

# Load Google OAuth credentials from client_secret.json
def load_google_credentials():
    """Load Google OAuth credentials from client_secret.json"""
    try:
        if os.path.exists("client_secret.json"):
            with open("client_secret.json", "r") as f:
                client_info = json.load(f)
                if "web" in client_info:
                    web_info = client_info["web"]
                    os.environ["GOOGLE_CLIENT_ID"] = web_info.get("client_id", "")
                    os.environ["GOOGLE_CLIENT_SECRET"] = web_info.get("client_secret", "")
                    os.environ["GOOGLE_REDIRECT_URI"] = web_info.get("redirect_uris", [""])[0]
                    logger.info("Google OAuth credentials loaded successfully")
                    return True
    except Exception as e:
        logger.error(f"Error loading Google credentials: {e}")
    return False

# Load credentials at startup
load_google_credentials()

# Create Flask app
app = Flask(__name__)

# App configuration
app.config.update(
    # Security settings
    SECRET_KEY=os.environ.get("SESSION_SECRET", "nous-secure-key-2025"),
    
    # Session settings
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    
    # Database settings
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///instance/nous.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # Public access settings
    PUBLIC_ACCESS=True
)

# Initialize database
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    # User model for authentication
    class User(UserMixin, db.Model):
        """User model for authentication"""
        __tablename__ = 'users'
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        username = db.Column(db.String(64), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(256))
        active = db.Column(db.Boolean, default=True)
        google_id = db.Column(db.String(128), unique=True, nullable=True)
        first_name = db.Column(db.String(50))
        last_name = db.Column(db.String(50))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __init__(self, **kwargs):
            if 'id' not in kwargs:
                kwargs['id'] = str(uuid.uuid4())
            super().__init__(**kwargs)
        
        @property
        def is_active(self):
            """Check if user account is active"""
            return self.active
            
        def check_password(self, password):
            """Check if provided password matches the hash"""
            return check_password_hash(self.password_hash, password)
    
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
except Exception as e:
    logger.error(f"Database initialization error: {e}")
    # Continue without database if it fails

# Configure Flask-Login
try:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # This will work at runtime despite LSP error
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID"""
        return User.query.get(user_id)
except Exception as e:
    logger.error(f"Login manager initialization error: {e}")

# Routes
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', title="Home")

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
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

@app.route('/features')
def features():
    """Features overview page"""
    return render_template('features.html', title="Features")

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', title="About")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Demo login with default credentials
        if email == "demo@example.com" and password == "demo123":
            # Create a demo user if it doesn't exist
            try:
                user = User.query.filter_by(email=email).first()
                if not user:
                    user = User(
                        username="demo",
                        email="demo@example.com",
                        password_hash=generate_password_hash("demo123"),
                        active=True
                    )
                    db.session.add(user)
                    db.session.commit()
                
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                logger.error(f"Login error: {e}")
                flash('Login system error', 'danger')
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')

@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth flow"""
    try:
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if not client_id:
            flash('Google OAuth not configured', 'error')
            return redirect(url_for('login'))
        
        # Generate state for CSRF protection
        state = str(uuid.uuid4())
        session['oauth_state'] = state
        
        # Build authorization URL
        auth_params = {
            'client_id': client_id,
            'redirect_uri': os.environ.get("GOOGLE_REDIRECT_URI", ""),
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = "https://accounts.google.com/o/oauth2/auth?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Google login error: {e}")
        flash('Google login failed', 'error')
        return redirect(url_for('login'))

@app.route('/callback/google')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            flash('Invalid state parameter', 'error')
            return redirect(url_for('login'))
        
        # Check for error
        if request.args.get('error'):
            flash(f"Google OAuth error: {request.args.get('error')}", 'error')
            return redirect(url_for('login'))
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            flash('No authorization code received', 'error')
            return redirect(url_for('login'))
        
        # Exchange code for token
        token_data = {
            'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
            'client_secret': os.environ.get("GOOGLE_CLIENT_SECRET"),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': os.environ.get("GOOGLE_REDIRECT_URI", "")
        }
        
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash('Failed to get access token', 'error')
            return redirect(url_for('login'))
        
        # Get user info
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {token_json['access_token']}"}
        )
        user_data = user_response.json()
        
        # Find or create user
        user = User.query.filter_by(google_id=user_data['id']).first()
        if not user:
            user = User.query.filter_by(email=user_data['email']).first()
            if user:
                # Link existing account
                user.google_id = user_data['id']
            else:
                # Create new user
                user = User(
                    username=user_data['email'].split('@')[0],
                    email=user_data['email'],
                    google_id=user_data['id'],
                    first_name=user_data.get('given_name', ''),
                    last_name=user_data.get('family_name', ''),
                    active=True
                )
                db.session.add(user)
        
        db.session.commit()
        login_user(user)
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        flash('Google authentication failed', 'error')
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
def logout():
    """Log out the current user"""
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found", code=404, title="Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error="Internal server error", code=500, title="Error"), 500

# Add headers to bypass Replit login requirement
@app.after_request
def add_header(response):
    """Add headers to enable public access without Replit login"""
    # CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    # Headers to bypass Replit login requirement
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['X-Replit-Auth-Bypass'] = 'true'
    
    # Special header to fix blank page issue in Replit deployment
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https://*;"
    
    return response

# Run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    logger.info("Public access enabled (no Replit login required)")
    logger.info("Google authentication maintained for protected routes")
    app.run(host="0.0.0.0", port=port)