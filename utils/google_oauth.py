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
        self.oauth.init_app(app)
        
        # Configure Google OAuth client with refresh token support
        self.google = self.oauth.register(
            name='google',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks',
                'access_type': 'offline',  # Request refresh token
                'prompt': 'consent'  # Force consent to get refresh token
            }
        )
    
    def get_authorization_url(self, redirect_uri):
        """Get Google OAuth authorization URL"""
        if not self.google:
            raise ValueError("OAuth not initialized")
        
        return self.google.authorize_redirect(redirect_uri)
    
    def handle_callback(self, redirect_uri):
        """Handle OAuth callback and create/login user"""
        if not self.google:
            raise ValueError("OAuth not initialized")
        
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
            
            # Log in user
            login_user(user, remember=True)
            
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
            refresh_response = self.google.refresh_token(user.google_refresh_token)
            
            if refresh_response and refresh_response.get('access_token'):
                user.google_access_token = refresh_response['access_token']
                if refresh_response.get('expires_at'):
                    user.google_token_expires_at = datetime.fromtimestamp(refresh_response['expires_at'])
                db.session.commit()
                return refresh_response['access_token']
                
        except Exception as e:
            # Log error without exposing sensitive information
            logger.error(f"Token refresh failed for user {user.id}")
            return None
        
        return None


# Global OAuth service instance
oauth_service = GoogleOAuthService()


def init_oauth(app):
    """Initialize OAuth service with app"""
    oauth_service.init_app(app)
    return oauth_service


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