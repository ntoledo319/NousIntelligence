"""
NOUS Personal Assistant - Public Final Application

A Flask application configured for public access without Replit login,
while maintaining internal Google authentication functionality.
"""
import os
import logging
from datetime import datetime, timedelta
import platform
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

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

# Ensure required directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# User model for authentication
class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=True)
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self):
        """Check if user account is active"""
        return self.active
        
    def check_password(self, password):
        """Verify password"""
        from werkzeug.security import check_password_hash
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# Set login view 
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Manually set login view (this might raise an LSP error but works at runtime)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # For demo purposes - create a test user if none exists
        if not User.query.first():
            from werkzeug.security import generate_password_hash
            import uuid
            
            test_user = User(
                id=str(uuid.uuid4()),
                username="demo",
                email="demo@example.com",
                first_name="Demo",
                last_name="User",
                password_hash=generate_password_hash("demo123"),
                active=True
            )
            db.session.add(test_user)
            db.session.commit()
            logger.info("Created demo user")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')
    
@app.route('/google_login')
def google_login():
    """Redirect to Google login"""
    try:
        # This would integrate with the real Google auth module
        from auth.google_auth import google_bp
        return redirect(url_for('google_auth.login'))
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        flash('Google login integration is ready but requires setup with your Google credentials', 'info')
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

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}, debug mode: {app.debug}")
    app.run(host='0.0.0.0', port=port)