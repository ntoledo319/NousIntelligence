"""
Secure JWT Authentication Service
Replaces the problematic jwt_auth.py with proper security implementation
"""

import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, Any, Optional, Union

import jwt
from flask import request, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class SecureJWTAuth:
    """Secure JWT authentication service with proper error handling"""
    
    def __init__(self, app=None):
        self.app = app
        self.secret_key = None
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.token_blacklist = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize JWT service with Flask app"""
        self.app = app
        self.secret_key = app.config.get('SECRET_KEY')
        
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required for JWT authentication. Please set SESSION_SECRET environment variable.")
        
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security")
        
        logger.info("Secure JWT authentication initialized")
    
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Generate secure access token"""
        try:
            payload = {
                'user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
                'iat': datetime.now(timezone.utc),
                'jti': secrets.token_hex(16),  # Unique token identifier
                'type': 'access'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token generated for user {user_data.get('id')}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            raise ValueError("Failed to generate access token")
    
    def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Generate secure refresh token"""
        try:
            payload = {
                'user_id': user_data.get('id'),
                'exp': datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days),
                'iat': datetime.now(timezone.utc),
                'jti': secrets.token_hex(16),
                'type': 'refresh'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Refresh token generated for user {user_data.get('id')}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating refresh token: {e}")
            raise ValueError("Failed to generate refresh token")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decode JWT token"""
        try:
            if token in self.token_blacklist:
                logger.warning("Attempted use of blacklisted token")
                return None
            
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_iat": True}
            )
            
            # Additional security checks
            if payload.get('type') not in ['access', 'refresh']:
                logger.warning("Invalid token type")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Allow expired tokens for blacklisting
            )
            
            jti = payload.get('jti')
            if jti:
                self.token_blacklist.add(jti)
                logger.info(f"Token blacklisted: {jti}")
            
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
    
    def create_token_response(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete token response with access and refresh tokens"""
        try:
            access_token = self.generate_access_token(user_data)
            refresh_token = self.generate_refresh_token(user_data)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': self.access_token_expire_minutes * 60,
                'user': {
                    'id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'email': user_data.get('email')
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating token response: {e}")
            raise ValueError("Failed to create authentication tokens")

def jwt_required(f):
    """Secure decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token is required'}), 401
        
        try:
            jwt_service = SecureJWTAuth(current_app)
            payload = jwt_service.validate_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Store payload in request context for use in route
            request.jwt_payload = payload
            
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_jwt_auth(f):
    """Decorator that allows optional JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass
        
        if token:
            try:
                jwt_service = SecureJWTAuth(current_app)
                payload = jwt_service.validate_token(token)
                if payload:
                    request.jwt_payload = payload
            except Exception as e:
                logger.warning(f"Optional JWT validation failed: {e}")
        
        return f(*args, **kwargs)
    
    return decorated_function

# Global JWT service instance
jwt_service = SecureJWTAuth()