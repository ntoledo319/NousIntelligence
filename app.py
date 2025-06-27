"""
Scorched Earth UI Rebuild - Google-Only Authentication
Professional-Grade Chat Interface with Modern Design
"""
import os
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from werkzeug.middleware.proxy_fix import ProxyFix

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
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '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')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_connect_configuration"
    
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