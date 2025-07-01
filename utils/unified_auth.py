"""
Unified Authentication System - Secure Implementation
Replaces all previous authentication implementations with secure, production-ready code
"""

import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, Any, Optional, Union

from flask import request, jsonify, session, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class AuthConfig:
    """Authentication configuration with secure defaults"""
    SECRET_KEY = None
    SESSION_LIFETIME_HOURS = 24
    TOKEN_LIFETIME_MINUTES = 60
    
    @classmethod
    def init_from_app(cls, app):
        """Initialize auth config from Flask app"""
        cls.SECRET_KEY = app.config.get('SECRET_KEY')
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY is required for authentication")
        if len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        logger.info("✅ Authentication configuration initialized")

class User:
    """Simple user class for authentication"""
    def __init__(self, user_id: str, username: str, email: str, is_demo: bool = False):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_demo = is_demo
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_demo': self.is_demo
        }

# Session-based authentication (primary method)
def create_user_session(user_data: Dict[str, Any]) -> None:
    """Create secure user session"""
    session.permanent = True
    session['user_id'] = user_data.get('id')
    session['username'] = user_data.get('username')
    session['email'] = user_data.get('email')
    session['is_demo'] = user_data.get('is_demo', False)
    session['created_at'] = datetime.now(timezone.utc).isoformat()
    logger.info(f"Session created for user {user_data.get('id')}")

def get_current_user() -> Optional[User]:
    """Get current authenticated user from session"""
    if 'user_id' not in session:
        return None
    
    # Check session expiry
    created_at = session.get('created_at')
    if created_at:
        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if datetime.now(timezone.utc) - created_time > timedelta(hours=AuthConfig.SESSION_LIFETIME_HOURS):
            clear_user_session()
            return None
    
    return User(
        user_id=session['user_id'],
        username=session.get('username', ''),
        email=session.get('email', ''),
        is_demo=session.get('is_demo', False)
    )

def clear_user_session() -> None:
    """Clear user session"""
    user_id = session.get('user_id', 'unknown')
    session.clear()
    logger.info(f"Session cleared for user {user_id}")

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return get_current_user() is not None

# Token-based authentication (for API access)
def generate_api_token(user_data: Dict[str, Any]) -> str:
    """Generate secure API token"""
    if not AuthConfig.SECRET_KEY:
        raise ValueError("Authentication not properly configured")
    
    # Simple secure token generation without JWT dependency
    token_data = {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'created': datetime.now(timezone.utc).timestamp(),
        'random': secrets.token_hex(16)
    }
    
    # Create a simple signed token
    import hmac
    import hashlib
    import json
    import base64
    
    payload = base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()
    signature = hmac.new(
        AuthConfig.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token = f"{payload}.{signature}"
    logger.info(f"API token generated for user {user_data.get('id')}")
    return token

def validate_api_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate API token"""
    if not token or not AuthConfig.SECRET_KEY:
        return None
    
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        
        payload_b64, signature = parts
        
        # Verify signature
        import hmac
        import hashlib
        expected_signature = hmac.new(
            AuthConfig.SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid token signature")
            return None
        
        # Decode payload
        import json
        import base64
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
        
        # Check expiry
        created = payload.get('created', 0)
        if datetime.now(timezone.utc).timestamp() - created > (AuthConfig.TOKEN_LIFETIME_MINUTES * 60):
            logger.warning("Token expired")
            return None
        
        return payload
        
    except Exception as e:
        logger.warning(f"Token validation error: {e}")
        return None

# Authentication decorators
def require_auth(f):
    """Decorator that requires authentication (session or token)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None
        
        # Try session authentication first
        user = get_current_user()
        
        # Try token authentication if no session
        if not user:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                token_data = validate_api_token(token)
                if token_data:
                    user = User(
                        user_id=token_data['user_id'],
                        username=token_data.get('username', ''),
                        email='',  # Token doesn't include email
                        is_demo=False
                    )
        
        if not user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                return jsonify({'error': 'Please log in to access this page'}), 401
        
        # Make user available to the route
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator that allows both authenticated and anonymous access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        # Try token authentication if no session
        if not user:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                token_data = validate_api_token(token)
                if token_data:
                    user = User(
                        user_id=token_data['user_id'],
                        username=token_data.get('username', ''),
                        email='',
                        is_demo=False
                    )
        
        g.current_user = user  # Can be None
        return f(*args, **kwargs)
    
    return decorated_function

# Demo mode utilities
def create_demo_user() -> User:
    """Create a demo user for public access"""
    demo_user = User(
        user_id=f"demo_{secrets.token_hex(8)}",
        username="Demo User",
        email="demo@nous.app",
        is_demo=True
    )
    create_user_session(demo_user.to_dict())
    return demo_user

# Flask-Login compatibility layer
def login_required(f):
    """Flask-Login compatible decorator"""
    return require_auth(f)

# Initialize authentication system
def init_auth(app):
    """Initialize authentication system with Flask app"""
    AuthConfig.init_from_app(app)
    logger.info("✅ Unified authentication system initialized")
