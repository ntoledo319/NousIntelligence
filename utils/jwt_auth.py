"""
JWT Authentication Module

This module provides JWT (JSON Web Token) authentication functionality for the NOUS API.
It includes token generation, validation, and refresh capabilities along with
decorators for protecting API routes.

@module: jwt_auth
@author: NOUS Development Team
"""
import os
import jwt
import time
import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, Callable

from flask import request, jsonify, current_app, g
from flask_login import current_user

# Configure logger
logger = logging.getLogger(__name__)

# Constants
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.environ.get('FLASK_SECRET', 'dev_jwt_secret'))
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '15'))  # minutes
JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', '7'))  # days
JWT_BLACKLIST = set()  # In production, use Redis or database

def generate_jwt_token(user_id: int, token_type: str = 'access') -> Tuple[str, float]:
    """
    Generate a JWT token for a user
    
    Args:
        user_id: User ID to generate token for
        token_type: Type of token ('access' or 'refresh')
        
    Returns:
        Tuple of (token, expiry_timestamp)
    """
    now = datetime.utcnow()
    
    # Set expiry based on token type
    if token_type == 'access':
        expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRES)
    elif token_type == 'refresh':
        expires_delta = timedelta(days=JWT_REFRESH_TOKEN_EXPIRES)
    else:
        raise ValueError("Invalid token type. Must be 'access' or 'refresh'")
    
    # Token expiry timestamp
    expires_at = now + expires_delta
    
    # Token payload
    payload = {
        'sub': user_id,
        'iat': now.timestamp(),
        'exp': expires_at.timestamp(),
        'type': token_type
    }
    
    # Generate token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Log token creation
    logger.info(f"Generated {token_type} token for user {user_id}")
    
    return token, expires_at.timestamp()

def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Validate a JWT token
    
    Args:
        token: The JWT token to validate
        
    Returns:
        Dict containing token payload if valid
        
    Raises:
        jwt.PyJWTError: If token is invalid
    """
    try:
        # Check if token is blacklisted
        if token in JWT_BLACKLIST:
            raise jwt.InvalidTokenError("Token has been blacklisted")
        
        # Decode and validate token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Additional checks
        if payload['exp'] < time.time():
            raise jwt.ExpiredSignatureError("Token has expired")
        
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise

def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist
    
    Args:
        token: The token to blacklist
    """
    JWT_BLACKLIST.add(token)
    logger.info("Token blacklisted")

def cleanup_blacklist() -> None:
    """
    Remove expired tokens from blacklist
    """
    now = time.time()
    to_remove = set()
    
    for token in JWT_BLACKLIST:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_signature": True})
            if payload['exp'] < now:
                to_remove.add(token)
        except jwt.PyJWTError:
            to_remove.add(token)
    
    JWT_BLACKLIST.difference_update(to_remove)
    logger.debug(f"Removed {len(to_remove)} expired tokens from blacklist")

def jwt_required(f: Callable) -> Callable:
    """
    Decorator to protect routes with JWT authentication
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function that requires a valid JWT token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Authentication required', 'message': 'Missing JWT token'}), 401
        
        try:
            # Validate token
            payload = validate_jwt_token(token)
            
            # Check token type
            if payload['type'] != 'access':
                return jsonify({'error': 'Invalid token type', 'message': 'Refresh token cannot access this resource'}), 401
            
            # Store user ID in flask.g for use in the route
            g.user_id = payload['sub']
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired', 'message': 'Please refresh your token or login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token', 'message': 'Token verification failed'}), 401
        
    return decorated

def refresh_token_required(f: Callable) -> Callable:
    """
    Decorator for routes that require a refresh token
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function that requires a valid refresh token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Authentication required', 'message': 'Missing refresh token'}), 401
        
        try:
            # Validate token
            payload = validate_jwt_token(token)
            
            # Check token type
            if payload['type'] != 'refresh':
                return jsonify({'error': 'Invalid token type', 'message': 'Access token cannot be used to refresh'}), 401
            
            # Store user ID in flask.g for use in the route
            g.user_id = payload['sub']
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token expired', 'message': 'Please login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token', 'message': 'Token verification failed'}), 401
        
    return decorated

def get_token_from_request() -> Optional[str]:
    """
    Extract token from request headers or query parameters
    
    Returns:
        JWT token or None if not found
    """
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split('Bearer ')[1]
    
    # Check form or JSON data
    if request.form:
        token = request.form.get('token')
        if token:
            return token
    
    if request.is_json:
        data = request.get_json()
        if data and 'token' in data:
            return data['token']
    
    # Check query parameters
    return request.args.get('token')

# Schedule regular cleanup of blacklist
def init_token_cleanup(app):
    """
    Initialize scheduled cleanup of token blacklist
    
    Args:
        app: Flask application instance
    """
    import threading
    
    def cleanup_worker():
        """Worker function to periodically clean up blacklisted tokens"""
        while True:
            cleanup_blacklist()
            time.sleep(3600)  # Run every hour
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    
    # Register cleanup on application shutdown
    @app.teardown_appcontext
    def shutdown_cleanup(exception=None):
        """Perform final cleanup on application shutdown"""
        cleanup_blacklist() 