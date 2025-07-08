"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
JWT Authentication Utilities
Provides JWT token generation, validation, and management for API authentication
"""

import jwt
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app, session
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Token blacklist (in production, use Redis or database)
_token_blacklist = set()

class JWTConfig:
    """JWT Configuration settings"""
    SECRET_KEY = None
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

def init_jwt_config(app):
    """Initialize JWT configuration from Flask app"""
    secret_key = app.config.get('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY is required for JWT authentication")
    JWTConfig.SECRET_KEY = secret_key

def generate_jwt_token(user_data: Dict[str, Any], token_type: str = 'access') -> str:
    """
    Generate JWT token for user
    
    Args:
        user_data: User information to encode in token
        token_type: 'access' or 'refresh'
    
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    
    if token_type == 'access':
        expire_delta = timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire_delta = timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        'user_id': user_data.get('id'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'type': token_type,
        'iat': now,
        'exp': now + expire_delta,
        'jti': f"{user_data.get('id')}_{token_type}_{int(now.timestamp())}"
    }
    
    try:
        token = jwt.encode(payload, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
        logger.info(f"Generated {token_type} token for user {user_data.get('id')}")
        return token
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        raise

def validate_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Check if token is blacklisted
        if token in _token_blacklist:
            logger.warning("Attempted use of blacklisted token")
            return None
        
        payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
        
        # Check if token is expired
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], timezone.utc):
            logger.warning("Token expired")
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None

def blacklist_token(token: str) -> bool:
    """
    Add token to blacklist
    
    Args:
        token: JWT token to blacklist
        
    Returns:
        True if successful
    """
    try:
        _token_blacklist.add(token)
        logger.info("Token blacklisted successfully")
        return True
    except Exception as e:
        logger.error(f"Token blacklisting failed: {e}")
        return False

def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers or query params"""
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Check query parameter
    token = request.args.get('token')
    if token:
        return token
    
    # Check JSON body
    if request.is_json:
        data = request.get_json()
        if data and 'token' in data:
            return data['token']
    
    return None

def jwt_required(f):
    """
    Decorator to require valid JWT token for endpoint access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = validate_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Make user data available to the endpoint
        request.jwt_payload = payload
        return f(*args, **kwargs)
    
    return decorated_function

def refresh_token_required(f):
    """
    Decorator to require valid refresh token for endpoint access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        
        if not token:
            return jsonify({'error': 'Refresh token required'}), 401
        
        payload = validate_jwt_token(token)
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        request.jwt_payload = payload
        return f(*args, **kwargs)
    
    return decorated_function

def get_get_demo_user()_from_token() -> Optional[Dict[str, Any]]:
    """Get current user data from JWT token in request"""
    token = extract_token_from_request()
    if not token:
        return None
    
    payload = validate_jwt_token(token)
    if not payload:
        return None
    
    return {
        'id': payload.get('user_id'),
        'email': payload.get('email'),
        'name': payload.get('name')
    }

def is_authenticated_via_jwt() -> bool:
    """Check if current request is authenticated via JWT"""
    return get_get_demo_user()_from_token() is not None

def is_authenticated_via_session() -> bool:
    """Check if current request is authenticated via session"""
    return 'user' in session and session['user'] is not None

def is_authenticated() -> bool:
    """Check if current request is authenticated via any method"""
    return is_authenticated_via_jwt() or is_authenticated_via_session()

def get_get_demo_user()() -> Optional[Dict[str, Any]]:
    """Get current user from JWT token or session"""
    # Try JWT first
    user = get_get_demo_user()_from_token()
    if user:
        return user
    
    # Fall back to session
    if 'user' in session:
        return session['user']
    
    return None

# Initialize when imported
try:
    if current_app:
        init_jwt_config(current_app)
except RuntimeError:
    # Not in app context, will initialize later
    pass