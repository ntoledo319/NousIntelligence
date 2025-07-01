"""
Secure JWT Authentication Service - Fixed Implementation
Replaces the problematic jwt_auth.py with clean, secure code
"""

import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, Any, Optional

import jwt
from flask import request, jsonify, current_app, session, redirect, url_for

logger = logging.getLogger(__name__)

class JWTConfig:
    """JWT Configuration with secure defaults"""
    SECRET_KEY = None
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

def init_jwt_config(app):
    """Initialize JWT configuration from Flask app"""
    secret_key = app.config.get('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY is required for JWT authentication")
    if len(secret_key) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long for security")
    JWTConfig.SECRET_KEY = secret_key
    logger.info("JWT configuration initialized securely")

def generate_jwt_token(user_data: Dict[str, Any], token_type: str = 'access') -> str:
    """Generate secure JWT token"""
    if not JWTConfig.SECRET_KEY:
        raise ValueError("JWT not properly configured")
    
    now = datetime.now(timezone.utc)
    
    if token_type == 'access':
        expire_delta = timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire_delta = timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'email': user_data.get('email'),
        'exp': now + expire_delta,
        'iat': now,
        'jti': secrets.token_hex(16),  # Unique token ID
        'type': token_type
    }
    
    try:
        token = jwt.encode(payload, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
        logger.info(f"JWT token generated for user {user_data.get('id')}")
        return token
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        raise ValueError("Failed to generate authentication token")

def validate_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate JWT token with comprehensive security checks"""
    if not token or not JWTConfig.SECRET_KEY:
        return None
    
    try:
        payload = jwt.decode(
            token,
            JWTConfig.SECRET_KEY,
            algorithms=[JWTConfig.ALGORITHM],
            options={"verify_exp": True, "verify_iat": True}
        )
        
        # Additional security validations
        if payload.get('type') not in ['access', 'refresh']:
            logger.warning("Invalid token type in payload")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error validating JWT token: {e}")
        return None

def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization', '')
    
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    
    return None

def jwt_required(f):
    """Decorator requiring valid JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        
        if not token:
            return jsonify({'error': 'Authorization token is required'}), 401
        
        payload = validate_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store payload for use in the route
        request.jwt_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_jwt_auth(f):
    """Decorator for optional JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        
        if token:
            payload = validate_jwt_token(token)
            if payload:
                request.jwt_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_user_from_token() -> Optional[Dict[str, Any]]:
    """Get current user data from JWT token in request"""
    token = extract_token_from_request()
    if not token:
        return None
    
    payload = validate_jwt_token(token)
    if not payload:
        return None
    
    return {
        'id': payload.get('user_id'),
        'username': payload.get('username'),
        'email': payload.get('email')
    }

def is_authenticated_via_jwt() -> bool:
    """Check if current request is authenticated via JWT"""
    return get_user_from_token() is not None

def is_authenticated_via_session() -> bool:
    """Check if current request is authenticated via session"""
    return 'user' in session and session['user'] is not None

def is_authenticated() -> bool:
    """Check if current request is authenticated via any method"""
    return is_authenticated_via_jwt() or is_authenticated_via_session()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user from JWT token or session"""
    # Try JWT first
    user = get_user_from_token()
    if user:
        return user
    
    # Fall back to session
    if 'user' in session:
        return session['user']
    
    return None

def get_demo_user() -> Dict[str, Any]:
    """Get demo user for public access"""
    return {
        'id': 'demo',
        'username': 'demo_user',
        'email': 'demo@example.com',
        'name': 'Demo User'
    }

def create_token_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create complete token response"""
    try:
        access_token = generate_jwt_token(user_data, 'access')
        refresh_token = generate_jwt_token(user_data, 'refresh')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            'user': {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email')
            }
        }
    except Exception as e:
        logger.error(f"Error creating token response: {e}")
        raise ValueError("Failed to create authentication tokens")

# Compatibility functions for existing code
def login_required(f):
    """Compatibility wrapper - use session or JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            # For API requests, return JSON error
            if request.is_json or 'api' in request.path:
                return jsonify({'error': 'Authentication required'}), 401
            # For web requests, redirect to login
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function