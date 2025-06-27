"""
Scorched Earth UI Rebuild - Google-Only Authentication
Professional-Grade Chat Interface with Modern Design
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with Google-only authentication"""
    app = Flask(__name__)
    
    # Essential configuration
    app.secret_key = os.environ.get('SESSION_SECRET', 'scorched-earth-rebuild-2025')
    
    # ProxyFix for Replit deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Session configuration
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,  # HTTP for Replit
        PERMANENT_SESSION_LIFETIME=86400  # 24 hours
    )
    
    # OAuth setup
    oauth = OAuth(app)
    
    # Google OAuth configuration
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid_connect_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
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
        
        redirect_uri = url_for('oauth_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    
    @app.route('/oauth2callback')
    def oauth_callback():
        """Handle Google OAuth callback"""
        try:
            token = google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if user_info:
                session['user'] = {
                    'id': user_info['sub'],
                    'name': user_info['name'],
                    'email': user_info['email'],
                    'avatar': user_info.get('picture', ''),
                    'login_time': datetime.now().isoformat()
                }
                session.permanent = True
                logger.info(f"User authenticated: {user_info['email']}")
                return redirect(url_for('app_chat'))
            else:
                flash('Authentication failed. Please try again.', 'error')
                return redirect(url_for('landing'))
                
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
    
    @app.route('/api/chat', methods=['POST'])
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
    
    @app.route('/api/user')
    def api_user():
        """Get current user info"""
        if not is_authenticated():
            return jsonify({'error': 'Not authenticated'}), 401
        
        return jsonify(session['user'])
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'authenticated_users': 1 if is_authenticated() else 0
        })
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)