"""
Google OAuth 2.0 Authentication Service (Security Fixed)
Implements secure Google OAuth flow for NOUS application with enhanced state management
"""

import os
import logging
import hmac
import hashlib
import secrets
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from models.user import User
from database import db
from datetime import datetime, timedelta
from utils.secret_manager import SecretManager

logger = logging.getLogger(__name__)


class SecureOAuthStateManager:
    """Secure OAuth state management with CSRF protection"""
    
    @staticmethod
    def generate_state(client_ip, user_agent, secret_key):
        """Generate cryptographically secure OAuth state with client fingerprinting"""
        timestamp = datetime.utcnow().timestamp()
        nonce = secrets.token_urlsafe(32)
        
        # Create fingerprint from client data
        fingerprint_data = f"{client_ip}:{user_agent}:{timestamp}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        # Create HMAC-signed state
        state_data = f"{nonce}:{timestamp}:{fingerprint}"
        signature = hmac.new(
            secret_key.encode(), 
            state_data.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return f"{state_data}:{signature}"
    
    @staticmethod
    def validate_state(stored_state, received_state, client_ip, user_agent, secret_key, max_age=600):
        """Validate OAuth state with comprehensive security checks"""
        
        if not stored_state or not received_state:
            return False, "Missing state parameters"
        
        # Timing-safe comparison to prevent timing attacks
        if not hmac.compare_digest(stored_state, received_state):
            return False, "State mismatch - possible CSRF attack"
        
        try:
            # Parse state components
            parts = received_state.split(':')
            if len(parts) != 4:
                return False, "Invalid state format"
            
            nonce, timestamp_str, fingerprint, signature = parts
            timestamp = float(timestamp_str)
            
            # Verify HMAC signature
            state_data = f"{nonce}:{timestamp_str}:{fingerprint}"
            expected_signature = hmac.new(
                secret_key.encode(),
                state_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid state signature"
            
            # Check expiration
            if datetime.utcnow().timestamp() - timestamp > max_age:
                return False, "State expired"
            
            # Verify client fingerprint
            fingerprint_data = f"{client_ip}:{user_agent}:{timestamp}"
            expected_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
            
            if not hmac.compare_digest(fingerprint, expected_fingerprint):
                return False, "Client fingerprint mismatch"
            
            return True, "State valid"
            
        except (ValueError, TypeError) as e:
            return False, f"State validation error: {e}"


class GoogleOAuthService:
    """Google OAuth 2.0 service with enhanced security"""
    
    def __init__(self, app=None):
        self.oauth = OAuth()
        self.google = None
        self.state_manager = SecureOAuthStateManager()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize OAuth with Flask app"""
        try:
            self.oauth.init_app(app)
            
            # Check if OAuth credentials are available
            raw_client_id = os.environ.get('GOOGLE_CLIENT_ID')
            raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
            
            # Validate client secret strength using SecretManager
            if raw_client_secret:
                is_valid, msg = SecretManager.validate_secret_strength(raw_client_secret)
                if not is_valid:
                    logger.warning(f"Weak GOOGLE_CLIENT_SECRET: {msg}")
            
            # Extract correct credentials from potentially malformed environment variables
            client_id = self._extract_client_id(raw_client_id)
            client_secret = self._extract_client_secret(raw_client_secret)
            
            if not client_id or not client_secret:
                logger.warning("Google OAuth credentials not found in environment variables")
                return False
            
            # Configure Google OAuth client
            self.google = self.oauth.register(
                name='google',
                client_id=client_id,
                client_secret=client_secret,
                authorize_url='https://accounts.google.com/oauth2/auth',
                access_token_url='https://oauth2.googleapis.com/token',
                userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
                client_kwargs={
                    'scope': 'openid email profile',
                    'access_type': 'offline',
                    'prompt': 'consent'
                }
            )
            
            logger.info("Google OAuth initialized successfully with enhanced security")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google OAuth: {e}")
            return False
    
    def _extract_client_id(self, raw_client_id):
        """Extract correct client ID from potentially malformed environment variable"""
        if not raw_client_id:
            return None
            
        if len(raw_client_id) < 100 and 'apps.googleusercontent.com' in raw_client_id:
            return raw_client_id
        
        if 'apps.googleusercontent.com' in raw_client_id:
            import re
            match = re.search(r'(\d{10,15}-[a-zA-Z0-9]+\.apps\.googleusercontent\.com)', raw_client_id)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_client_secret(self, raw_client_secret):
        """Extract correct client secret from potentially malformed environment variable"""
        if not raw_client_secret:
            return None
            
        if len(raw_client_secret) < 50 and 'GOCSPX-' in raw_client_secret:
            return raw_client_secret
        
        if 'GOCSPX-' in raw_client_secret:
            import re
            match = re.search(r'(GOCSPX-[a-zA-Z0-9_-]+)', raw_client_secret)
            if match:
                return match.group(1)
        
        return None
    
    def is_configured(self):
        """Check if OAuth is properly configured"""
        raw_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        raw_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        client_id = self._extract_client_id(raw_client_id)
        client_secret = self._extract_client_secret(raw_client_secret)
        return self.google is not None and client_id and client_secret
    
    def get_authorization_url(self, redirect_uri):
        """Get Google OAuth authorization URL with enhanced CSRF protection"""
        if not self.google:
            raise ValueError("OAuth not initialized - missing credentials")
        
        # Fix redirect URI for deployment
        redirect_uri = self._fix_redirect_uri(redirect_uri)
        logger.info(f"Using redirect URI: {redirect_uri}")
        
        # Get client fingerprint data
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
        user_agent = request.headers.get('User-Agent', '') or 'unknown'
        
        # Generate secure state
        from flask import current_app
        state = self.state_manager.generate_state(client_ip, user_agent, current_app.secret_key)
        
        # Store state securely in session with metadata
        session['oauth_state'] = state
        session['oauth_client_ip'] = client_ip
        session['oauth_user_agent'] = user_agent
        session['oauth_timestamp'] = datetime.utcnow().timestamp()
        
        # Mark session as modified for persistence
        session.modified = True
        
        logger.info("OAuth state generated and stored securely")
        return self.google.authorize_redirect(redirect_uri, state=state)
    
    def _fix_redirect_uri(self, redirect_uri):
        """Fix redirect URI for deployment"""
        # Validate redirect URI to prevent open redirect attacks
        allowed_hosts = [
            'localhost',
            '127.0.0.1', 
            'nous.app',
            'www.nous.app'
        ]
        
        # Add Replit domains if detected
        repl_url = os.environ.get('REPL_URL')
        if repl_url:
            if 'replit.dev' in repl_url or 'replit.app' in repl_url:
                from urllib.parse import urlparse
                parsed = urlparse(repl_url)
                allowed_hosts.append(parsed.netloc)
                return f"{repl_url}/auth/google/callback"
        
        # Validate redirect URI against allowed hosts
        from urllib.parse import urlparse
        parsed_uri = urlparse(redirect_uri)
        
        if parsed_uri.netloc and parsed_uri.netloc not in allowed_hosts:
            logger.warning(f"Potentially unsafe redirect URI: {redirect_uri}")
            # Use safe fallback
            return "https://nous.app/auth/google/callback"
        
        return redirect_uri
    
    def handle_callback(self, redirect_uri):
        """Handle OAuth callback with enhanced security validation"""
        if not self.google:
            raise ValueError("OAuth not initialized")
        
        # Get stored state and client data
        stored_state = session.get('oauth_state')
        stored_ip = session.get('oauth_client_ip')
        stored_user_agent = session.get('oauth_user_agent')
        
        # Get current request data
        received_state = request.args.get('state')
        current_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
        current_user_agent = request.headers.get('User-Agent', '') or 'unknown'
        
        # Validate OAuth state with comprehensive checks
        from flask import current_app
        is_valid, error_msg = self.state_manager.validate_state(
            stored_state, received_state, current_ip, current_user_agent, current_app.secret_key
        )
        
        if not is_valid:
            logger.warning(f"OAuth state validation failed: {error_msg}")
            # Clear OAuth session data
            for key in ['oauth_state', 'oauth_client_ip', 'oauth_user_agent', 'oauth_timestamp']:
                session.pop(key, None)
            raise ValueError(f"OAuth security validation failed: {error_msg}")
        
        # Additional security checks
        if stored_ip != current_ip:
            logger.warning(f"OAuth IP mismatch: stored={stored_ip}, current={current_ip}")
            # In production, you might want to reject this, but for demo we'll allow with warning
        
        if stored_user_agent != current_user_agent:
            logger.warning("OAuth User-Agent mismatch detected")
        
        # Clear OAuth session data after successful validation
        for key in ['oauth_state', 'oauth_client_ip', 'oauth_user_agent', 'oauth_timestamp']:
            session.pop(key, None)
        
        try:
            # Fix redirect URI for consistency
            redirect_uri = self._fix_redirect_uri(redirect_uri)
            logger.info(f"Processing callback with redirect URI: {redirect_uri}")

            # Get access token from callback
            # CRITICAL: redirect_uri must match exactly what was sent to Google
            token = self.google.authorize_access_token(redirect_uri=redirect_uri)
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
                    user.google_access_token = token_encryption.encrypt_token(token.get('access_token'))
                    user.google_refresh_token = token_encryption.encrypt_token(token.get('refresh_token'))
                else:
                    logger.warning("Token encryption not available - storing tokens in plain text")
                    user.google_access_token = token.get('access_token')
                    user.google_refresh_token = token.get('refresh_token')
            except ImportError:
                user.google_access_token = token.get('access_token')
                user.google_refresh_token = token.get('refresh_token')
                
            if token.get('expires_at'):
                user.google_token_expires_at = datetime.fromtimestamp(token['expires_at'])
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            # Log successful authentication
            logger.info(f"OAuth authentication successful for user {email}")
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"OAuth callback processing failed: {e}")
            raise e
    
    def logout(self):
        """Logout current user and clear OAuth session data"""
        logout_user()
        
        # Clear any remaining OAuth data from session
        oauth_keys = [key for key in session.keys() if key.startswith('oauth_')]
        for key in oauth_keys:
            session.pop(key, None)
        
        session.clear()
    
    def _generate_unique_username(self, base_username):
        """Generate a unique username to handle collisions"""
        username = base_username
        counter = 1
        
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username


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