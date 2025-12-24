
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
from models.database import db
from datetime import datetime
from utils.secret_manager import SecretManager

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
            
            # Check if OAuth credentials are available using correct environment variable names
            # Support both naming conventions for backwards compatibility
            client_id = os.environ.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
            
            # Handle case where client_id might contain JSON data instead of just the ID
            if client_id and len(client_id) > 100:  # Normal client IDs are ~70 chars
                try:
                    import json
                    # Try to parse as JSON and extract client_id
                    cred_data = json.loads(client_id)
                    if isinstance(cred_data, dict) and 'client_id' in cred_data:
                        client_id = cred_data['client_id']
                        logger.info("Extracted client_id from JSON credentials")
                except (json.JSONDecodeError, KeyError):
                    # If it's not valid JSON, assume it's already the client_id
                    pass
            
            # Validate client secret strength using SecretManager if available
            if client_secret:
                try:
                    is_valid, msg = SecretManager.validate_secret_strength(client_secret)
                    if not is_valid:
                        logger.warning(f"Weak OAuth client secret: {msg}")
                except:
                    # SecretManager may not be available - continue anyway
                    pass
            
            if not client_id or not client_secret:
                logger.warning("Google OAuth credentials not found - OAuth login will not be available")
                logger.warning("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment")
                return False
            
            # Configure Google OAuth client with direct endpoint configuration
            # Using direct URLs instead of discovery document to avoid network issues
            self.google = self.oauth.register(
                name='google',
                client_id=client_id,
                client_secret=client_secret,
                authorize_url='https://accounts.google.com/oauth2/auth',
                access_token_url='https://oauth2.googleapis.com/token',
                userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
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
    
    def _extract_client_id(self, raw_client_id):
        """Extract correct client ID from potentially malformed environment variable"""
        if not raw_client_id:
            return None
            
        # If it looks like a normal client ID, return as-is
        if len(raw_client_id) < 100 and 'apps.googleusercontent.com' in raw_client_id:
            return raw_client_id
        
        # Try to extract from malformed data
        if 'apps.googleusercontent.com' in raw_client_id:
            import re
            # Look for the client ID pattern - extract full domain
            match = re.search(r'(\d{10,15}-[a-zA-Z0-9]+\.apps\.googleusercontent\.com)', raw_client_id)
            if match:
                return match.group(1)  # Return the full match including domain
        
        return None
    
    def _extract_client_secret(self, raw_client_secret):
        """Extract correct client secret from potentially malformed environment variable"""
        if not raw_client_secret:
            return None
            
        # If it looks like a normal client secret, return as-is
        if len(raw_client_secret) < 50 and 'GOCSPX-' in raw_client_secret:
            return raw_client_secret
        
        # Try to extract from malformed data
        if 'GOCSPX-' in raw_client_secret:
            import re
            # Look for the client secret pattern
            match = re.search(r'(GOCSPX-[a-zA-Z0-9_-]+)', raw_client_secret)
            if match:
                return match.group(1)
        
        return None
    
    def is_configured(self):
        """Check if OAuth is properly configured"""
        client_id = os.environ.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        return self.google is not None and client_id and client_secret
    
    def get_authorization_url(self, redirect_uri):
        """Get Google OAuth authorization URL with enhanced CSRF protection"""
        if not self.google:
            raise ValueError("OAuth not initialized - missing credentials")
        
        # Fix redirect URI for Replit deployment
        redirect_uri = self._fix_redirect_uri(redirect_uri)
        logger.info(f"Using redirect URI: {redirect_uri}")
        
        # Get user fingerprint data for enhanced security
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Generate secure state using enhanced state manager
        try:
            from utils.oauth_state_manager import OAuthStateManager
            from flask import current_app
            state_manager = OAuthStateManager(current_app.secret_key)
            state = state_manager.generate_state(user_ip, user_agent)
        except ImportError:
            # Fallback to simple state generation
            import secrets
            state = secrets.token_urlsafe(32)
        
        # Store state with additional validation data
        session['oauth_state'] = state
        session['oauth_state_timestamp'] = datetime.utcnow().timestamp()
        session['oauth_state_ip'] = user_ip
        
        return self.google.authorize_redirect(redirect_uri, state=state)
    
    def _fix_redirect_uri(self, redirect_uri):
        """Fix redirect URI for deployment environments (Render, Replit, etc.)"""
        # Check for Render deployment
        if os.environ.get('RENDER'):
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                return f"{render_url}/callback/google"
            hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
            if hostname:
                return f"https://{hostname}/callback/google"

        # If we're on Replit, ensure we use the correct domain
        if 'replit.dev' in redirect_uri or 'replit.app' in redirect_uri:
            return redirect_uri

        # Check for common Replit patterns in environment
        repl_url = os.environ.get('REPL_URL')
        if repl_url:
            return f"{repl_url}/callback/google"

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
            
            # Store OAuth tokens securely with encryption
            try:
                from utils.token_encryption import token_encryption
                if token_encryption:
                    # Encrypt tokens before storage
                    user.google_access_token = token_encryption.encrypt_token(token.get('access_token'))
                    user.google_refresh_token = token_encryption.encrypt_token(token.get('refresh_token'))
                else:
                    # Fallback to direct storage (log warning)
                    logger.warning("Token encryption not available - storing tokens in plain text")
                    user.google_access_token = token.get('access_token')
                    user.google_refresh_token = token.get('refresh_token')
            except ImportError:
                # Fallback for missing encryption module
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
    

    
    def _generate_unique_username(self, base_username):
        """Generate a unique username to handle collisions"""
        username = base_username
        counter = 1
        
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username
    
    def refresh_token(self, user):
        """Refresh user's Google OAuth token with secure handling"""
        if not user.google_refresh_token:
            return None
            
        try:
            # Decrypt the stored refresh token
            refresh_token = user.google_refresh_token
            try:
                from utils.token_encryption import token_encryption
                if token_encryption:
                    refresh_token = token_encryption.decrypt_token(user.google_refresh_token)
                    if not refresh_token:
                        logger.error("Failed to decrypt refresh token")
                        return None
            except ImportError:
                pass  # Use token as-is if encryption not available
            
            # Use the refresh token to get a new access token
            token_data = {
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            refresh_response = self.google.fetch_access_token(**token_data)
            
            if refresh_response and refresh_response.get('access_token'):
                # Store the new encrypted access token
                try:
                    from utils.token_encryption import token_encryption
                    if token_encryption:
                        user.google_access_token = token_encryption.encrypt_token(refresh_response['access_token'])
                        # Update refresh token if provided (token rotation)
                        if refresh_response.get('refresh_token'):
                            user.google_refresh_token = token_encryption.encrypt_token(refresh_response['refresh_token'])
                    else:
                        user.google_access_token = refresh_response['access_token']
                        if refresh_response.get('refresh_token'):
                            user.google_refresh_token = refresh_response['refresh_token']
                except ImportError:
                    user.google_access_token = refresh_response['access_token']
                    if refresh_response.get('refresh_token'):
                        user.google_refresh_token = refresh_response['refresh_token']
                
                # Update token expiry
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
    
    def get_deployment_url(self):
        """Get the current deployment URL"""
        from flask import request, has_request_context

        # Check for Render deployment first
        if os.environ.get('RENDER'):
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                return render_url
            hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
            if hostname:
                return f"https://{hostname}"

        # Try Replit environment variables
        for env_var in ['REPL_URL', 'REPLIT_DOMAIN']:
            env_value = os.environ.get(env_var)
            if env_value:
                if not env_value.startswith('http'):
                    return f"https://{env_value}"
                return env_value

        # Try to get from request context
        if has_request_context():
            # Check X-Forwarded-Proto for proxied HTTPS
            scheme = 'https' if (request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https') else 'http'
            return f"{scheme}://{request.host}"

        # Fallback for local development
        return "http://localhost:8080"


# Global OAuth service instance
oauth_service = GoogleOAuthService()


def init_oauth(app):
    """Initialize OAuth service with app. Returns the service on success or None on failure."""
    success = oauth_service.init_app(app)
    return oauth_service if success else None


def user_loader(user_id):
    """Flask-Login user loader: load User by ID."""
    return User.query.get(int(user_id)) if user_id else None


def require_auth():
    """Decorator or utility to enforce login for certain routes."""
    if not current_user.is_authenticated:
        # Save next URL for redirect after login
        session['next'] = request.url
        # Redirect to login with a flash message
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('auth.login'))
    return None
