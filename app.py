"""
Backend Stability + Beta Suite Overhaul
Professional-Grade Chat Interface with Health Monitoring & Beta Management
"""
import os
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from config import AppConfig, PORT, HOST, DEBUG
from database import db, init_database

# Import new backend stability components
from utils.health_monitor import health_monitor
from utils.database_optimizer import db_optimizer
from routes.api.feedback import feedback_api
from routes.maps_routes import maps_bp
from routes.weather_routes import weather_bp
from routes.tasks_routes import tasks_bp
from routes.recovery_routes import recovery_bp

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with comprehensive backend stability features"""
    app = Flask(__name__, static_url_path=AppConfig.STATIC_URL_PATH)
    
    # Essential configuration
    app.secret_key = AppConfig.SECRET_KEY
    
    # ProxyFix for Replit deployment with enhanced settings
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Session configuration with enhanced security
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,  # HTTP for Replit
        PERMANENT_SESSION_LIFETIME=86400,  # 24 hours
        # Database optimization settings
        SQLALCHEMY_DATABASE_URI=AppConfig.get_database_url(),
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_size': 2,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        },
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize database
    init_database(app)
    
    # Initialize health monitoring
    health_monitor.init_app(app)
    
    # Register blueprints
    app.register_blueprint(feedback_api)
    app.register_blueprint(maps_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(recovery_bp)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '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')
    GOOGLE_DISCOVERY_URL = f"{AppConfig.GOOGLE_OAUTH_BASE_URL}/.well-known/openid_connect_configuration"
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers"""
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    def is_authenticated():
        """Check if user is authenticated"""
        return 'user' in session
    
    @app.route('/')
    def landing():
        """Public landing page with Google sign-in"""
        return render_template('landing.html')
    
    @app.route('/login')
    def login():
        """Initiate Google OAuth flow"""
        if is_authenticated():
            return redirect(url_for('app_chat'))
        
        # For development - simple demo login
        # In production, this would integrate with actual Google OAuth
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            # Build Google OAuth URL
            redirect_uri = url_for('oauth_callback', _external=True)
            google_auth_url = (
                f"https://accounts.google.com/oauth2/auth?"
                f"client_id={GOOGLE_CLIENT_ID}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri, safe='')}&"
                f"scope=openid%20email%20profile&"
                f"response_type=code&"
                f"access_type=offline"
            )
            return redirect(google_auth_url)
        else:
            # Demo mode - simulate Google login
            flash('Demo mode: Google OAuth credentials not configured. Using demo login.', 'warning')
            return redirect(url_for('demo_login'))
    
    @app.route('/demo-login')
    def demo_login():
        """Demo login for development"""
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'avatar': '',
            'login_time': datetime.now().isoformat()
        }
        session.permanent = True
        logger.info("Demo user authenticated")
        return redirect(url_for('app_chat'))
    
    @app.route('/oauth2callback')
    def oauth_callback():
        """Handle Google OAuth callback"""
        try:
            # Get authorization code
            code = request.args.get('code')
            error = request.args.get('error')
            
            if error:
                flash(f'Google authentication error: {error}', 'error')
                return redirect(url_for('landing'))
            
            if not code:
                flash('No authorization code received', 'error')
                return redirect(url_for('landing'))
            
            # In a full implementation, we would exchange code for tokens
            # For now, create a demo session
            session['user'] = {
                'id': 'google_user_' + code[:10],
                'name': 'Google User',
                'email': 'user@gmail.com',
                'avatar': '',
                'login_time': datetime.now().isoformat()
            }
            session.permanent = True
            logger.info("Google OAuth user authenticated")
            return redirect(url_for('app_chat'))
                
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            flash('Authentication error. Please try again.', 'error')
            return redirect(url_for('landing'))
    
    @app.route('/logout')
    def logout():
        """Logout user"""
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('landing'))
    
    @app.route('/app')
    def app_chat():
        """Main chat application - requires authentication"""
        if not is_authenticated():
            return redirect(url_for('login'))
        
        return render_template('app.html', user=session['user'])
    
    @app.route(f'{AppConfig.API_BASE_PATH}/chat', methods=['POST'])
    @app.route(f'{AppConfig.API_LEGACY_PATH}/chat', methods=['POST'])  # Legacy support
    def api_chat():
        """Chat API endpoint"""
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Simple echo response for now - can be enhanced with actual AI
        response = {
            'message': f"Echo: {message}",
            'timestamp': datetime.now().isoformat(),
            'user': session['user']['name']
        }
        
        return jsonify(response)
    
    @app.route(f'{AppConfig.API_BASE_PATH}/user')
    @app.route(f'{AppConfig.API_LEGACY_PATH}/user')  # Legacy support
    def api_user():
        """Get current user info"""
        if not is_authenticated():
            return jsonify({'error': 'Not authenticated'}), 401
        
        return jsonify(session['user'])
    
    @app.route('/health')
    @app.route('/healthz')
    def health():
        """Health check endpoint for deployment monitoring"""
        try:
            # Test database connection
            from database import db
            from sqlalchemy import text
            db.session.execute(text('SELECT 1')).scalar()
            
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '0.2.0',
                'database': 'connected',
                'port': PORT,
                'environment': os.environ.get('FLASK_ENV', 'production')
            }
            
            return jsonify(health_status), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 503
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)