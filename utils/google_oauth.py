
"""
Google OAuth 2.0 Authentication Service
Implements secure Google OAuth flow for NOUS application
"""

import os
import logging
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from models.user import User
from database import db
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Google OAuth 2.0 service for user authentication"""
    
    def __init__(self, app=None):
        self.oauth = OAuth()
        self.google = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize OAuth with Flask app"""
        try:
            self.oauth.init_app(app)
            
            # Check if OAuth credentials are available
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.warning("Google OAuth credentials not found in environment variables")
                logger.warning("OAuth login will not be available. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
                return False
            
            # Configure Google OAuth client with refresh token support
            self.google = self.oauth.register(
                name='google',
                client_id=client_id,
                client_secret=client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks',
                    'access_type': 'offline',  # Request refresh token
                    'prompt': 'consent'  # Force consent to get refresh token
                }
            )
            
            logger.info("Google OAuth initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google OAuth: {e}")
            return False
    
    def is_configured(self):
        """Check if OAuth is properly configured"""
        return self.google is not None
    
    def get_authorization_url(self, redirect_uri):
        """Get Google OAuth authorization URL with CSRF protection"""
        if not self.google:
            raise ValueError("OAuth not initialized - missing credentials")
        
        # Fix redirect URI for Replit deployment
        redirect_uri = self._fix_redirect_uri(redirect_uri)
        logger.info(f"Using redirect URI: {redirect_uri}")
        
        # Generate and store state parameter for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        return self.google.authorize_redirect(redirect_uri, state=state)
    
    def _fix_redirect_uri(self, redirect_uri):
        """Fix redirect URI for Replit deployment"""
        # If we're on Replit, ensure we use the correct domain
        if 'replit.dev' in redirect_uri or 'replit.app' in redirect_uri:
            return redirect_uri
            
        # Check for common Replit patterns in environment
        repl_url = os.environ.get('REPL_URL')
        if repl_url:
            return f"{repl_url}/auth/google/callback"
            
        # For local development or other deployments, use as-is
        return redirect_uri
    
    def handle_callback(self, redirect_uri):
        """Handle OAuth callback and create/login user"""
        if not self.google:
            raise ValueError("OAuth not initialized")
        
        # Fix redirect URI for consistency
        redirect_uri = self._fix_redirect_uri(redirect_uri)
        logger.info(f"Processing callback with redirect URI: {redirect_uri}")
        
        # Validate state parameter for CSRF protection
        received_state = request.args.get('state')
        stored_state = session.pop('oauth_state', None)
        
        if not received_state or not stored_state or received_state != stored_state:
            raise ValueError("Invalid OAuth state parameter - possible CSRF attack")
        
        try:
            # Get access token from callback
            token = self.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if not user_info:
                # Fallback: get user info from Google's userinfo endpoint
                resp = self.google.get('userinfo')
                user_info = resp.json()
            
            # Extract user information
            google_id = user_info.get('sub')
            email = user_info.get('email')
            name = user_info.get('name', '')
            
            if not google_id or not email:
                raise ValueError("Invalid user information from Google")
            
            # Find or create user
            user = User.query.filter_by(google_id=google_id).first()
            
            if not user:
                # Check if user exists with same email
                user = User.query.filter_by(email=email).first()
                if user:
                    # Link Google account to existing user
                    user.google_id = google_id
                else:
                    # Create new user
                    user = User()
                    user.username = self._generate_unique_username(name or email.split('@')[0])
                    user.email = email
                    user.google_id = google_id
                    user.active = True
                    user.created_at = datetime.utcnow()
                    db.session.add(user)
            
            # Store OAuth tokens securely
            user.google_access_token = token.get('access_token')
            user.google_refresh_token = token.get('refresh_token')
            if token.get('expires_at'):
                user.google_token_expires_at = datetime.fromtimestamp(token['expires_at'])
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return user
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def logout(self):
        """Logout current user"""
        logout_user()
        session.clear()
    
    def is_configured(self):
        """Check if OAuth is properly configured"""
        return (
            os.environ.get('GOOGLE_CLIENT_ID') and 
            os.environ.get('GOOGLE_CLIENT_SECRET')
        )
    
    def _generate_unique_username(self, base_username):
        """Generate a unique username to handle collisions"""
        username = base_username
        counter = 1
        
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username
    
    def refresh_token(self, user):
        """Refresh user's Google OAuth token"""
        if not user.google_refresh_token:
            return None
            
        try:
            # Use the refresh token to get a new access token
            token_data = {
                'refresh_token': user.google_refresh_token,
                'grant_type': 'refresh_token'
            }
            
            refresh_response = self.google.fetch_access_token(**token_data)
            
            if refresh_response and refresh_response.get('access_token'):
                user.google_access_token = refresh_response['access_token']
                if refresh_response.get('expires_in'):
                    expires_at = datetime.utcnow().timestamp() + refresh_response['expires_in']
                    user.google_token_expires_at = datetime.fromtimestamp(expires_at)
                db.session.commit()
                return refresh_response['access_token']
                
        except Exception as e:
            # Log error without exposing sensitive information
            logger.error(f"Token refresh failed for user {user.id}: {type(e).__name__}")
            return None
        
        return None


# Global OAuth service instance
oauth_service = GoogleOAuthService()


def init_oauth(app):
    """Initialize OAuth service with app"""
    success = oauth_service.init_app(app)
    if success:
        return oauth_service
    else:
        return None


def user_loader(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def require_auth():
    """Check if authentication is required and redirect if needed"""
    if not current_user.is_authenticated:
        # Store the requested URL for redirect after login
        session['next'] = request.url
        return redirect(url_for('auth.login'))
    return None
