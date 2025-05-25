"""
NOUS Personal Assistant - Public Deployment Version

A simplified Flask application that ensures public access without Replit login,
while maintaining internal Google authentication functionality.
"""
import os
import logging
from datetime import datetime, timedelta
import platform
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_session import Session

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# App configuration
app.config.update(
    # Security settings
    SECRET_KEY=os.environ.get("SESSION_SECRET", "nous-secure-key-2025"),
    
    # Session settings
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR="flask_session",
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    
    # Database settings
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///instance/nous.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_pre_ping': True,
        'pool_recycle': 300,
    },
    
    # Public access settings - no login required
    PUBLIC_ACCESS=True,
    PRESERVE_CONTEXT_ON_EXCEPTION=False
)

# Initialize Flask-Session
Session(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Use local login view
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Ensure required directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Import database after app is configured
from database import db

# Initialize database with the app
db.init_app(app)

# Import models after db is initialized
from models import User

# Create database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Routes
@app.route('/')
def index():
    """Main landing page"""
    logger.info("Rendering index page")
    return render_template('index.html', title="Home")

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    
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

@app.route('/features')
def features():
    """Features overview page"""
    logger.info("Rendering features page")
    return render_template('features.html', title="Features")

@app.route('/about')
def about():
    """About page"""
    logger.info("Rendering about page")
    return render_template('about.html', title="About")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return render_template('error.html', error="Page not found", code=404, title="Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}")
    return render_template('error.html', error="Internal server error", code=500, title="Error"), 500

# Add authentication routes
def create_auth_routes():
    """Add authentication routes to the app"""
    from flask import flash
    from flask_login import login_user, logout_user, login_required, current_user
    from models import User, UserSettings
    import secrets
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Simple login page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        return render_template('login.html')
        
    @app.route('/google_login')
    def google_login():
        """Redirect to Google login"""
        try:
            from auth.google_auth import google_bp
            return redirect(url_for('google_auth.login'))
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            flash('Google login is currently unavailable', 'danger')
            return redirect(url_for('login'))
    
    @app.route('/logout')
    @login_required
    def logout():
        """Log out the current user"""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        return render_template('dashboard.html', user=current_user)

# Add headers to bypass Replit login requirement
@app.after_request
def add_header(response):
    """Add headers to enable public access without Replit login"""
    # CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    # Headers to bypass Replit login requirement
    response.headers['X-Frame-Options'] = 'ALLOWALL'  # Allow framing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['X-Replit-Auth-Bypass'] = 'true'  # Custom header to bypass Replit auth
    
    # Special header to fix blank page issue in Replit deployment
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https://*;"
    
    return response

# Login status route to check if user is logged in
@app.route('/auth/status')
def auth_status():
    """Check if user is logged in"""
    if current_user.is_authenticated:
        return jsonify({
            'logged_in': True,
            'username': current_user.username,
            'email': current_user.email
        })
    return jsonify({'logged_in': False})

# Initialize app
def init_app():
    """Initialize the app with all required components"""
    # Create authentication routes
    create_auth_routes()
    logger.info("Application initialization complete")

# Run the app
if __name__ == '__main__':
    # Initialize app components
    init_app()
    
    # Run the Flask app
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}, debug mode: {app.debug}")
    app.run(host='0.0.0.0', port=port)