"""
Simple Authentication Service - No External Dependencies
Secure session-based authentication without JWT dependencies
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional

from flask import request, session, redirect, url_for, jsonify, current_app

logger = logging.getLogger(__name__)

class SimpleAuth:
    """Simple session-based authentication system"""
    
    @staticmethod
    def init_app(app):
        """Initialize authentication with Flask app"""
        if not app.config.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY is required for authentication")
        
        # Configure session security
        app.config.update(
            SESSION_COOKIE_SECURE=True if app.config.get('ENV') == 'production' else False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
        )
        
        logger.info("Simple authentication initialized")
    
    @staticmethod
    def login_user(user_data: Dict[str, Any]):
        """Log in a user with session"""
        if not user_data or not user_data.get('id'):
            raise ValueError("Valid user data required for login")
        
        session.permanent = True
        session['user'] = {
            'id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'logged_in_at': datetime.now().isoformat()
        }
        session['authenticated'] = True
        
        logger.info(f"User logged in: {user_data.get('username')}")
    
    @staticmethod
    def logout_user():
        """Log out current user"""
        if 'user' in session:
            logger.info(f"User logged out: {session['user'].get('username')}")
        
        session.clear()
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if current user is authenticated"""
        return session.get('authenticated', False) and 'user' in session
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if SimpleAuth.is_authenticated():
            return session.get('user')
        return None
    
    @staticmethod
    def get_demo_user() -> Dict[str, Any]:
        """Get demo user for public access"""
        return {
            'id': 'demo',
            'username': 'demo_user',
            'email': 'demo@example.com',
            'name': 'Demo User',
            'is_demo': True
        }
    
    @staticmethod
    def require_auth(f):
        """Decorator requiring authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SimpleAuth.is_authenticated():
                # For API requests, return JSON error
                if request.is_json or '/api/' in request.path:
                    return jsonify({'error': 'Authentication required'}), 401
                # For web requests, redirect to login
                try:
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    logger.warning(f"Failed to redirect to auth.login: {e}")
                    return redirect('/login')
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def optional_auth(f):
        """Decorator for optional authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Authentication is optional - proceed regardless
            return f(*args, **kwargs)
        
        return decorated_function

# Create compatibility functions for existing code
def init_jwt_config(app):
    """Compatibility function - initialize simple auth instead"""
    SimpleAuth.init_app(app)

def is_authenticated() -> bool:
    """Compatibility function"""
    return SimpleAuth.is_authenticated()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Compatibility function"""
    return SimpleAuth.get_current_user()

def login_required(f):
    """Compatibility decorator"""
    return SimpleAuth.require_auth(f)

def optional_jwt_auth(f):
    """Compatibility decorator"""
    return SimpleAuth.optional_auth(f)

def get_demo_user() -> Dict[str, Any]:
    """Get demo user for public access"""
    return SimpleAuth.get_demo_user()

def is_authenticated_via_session() -> bool:
    """Check session authentication"""
    return SimpleAuth.is_authenticated()

def is_authenticated_via_jwt() -> bool:
    """Compatibility - always return False since no JWT"""
    return False

# Generate secure tokens without JWT
def generate_secure_token(length: int = 32) -> str:
    """Generate secure token for API access"""
    return secrets.token_urlsafe(length)

def create_api_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

def create_error_response(error: str, code: int = 400) -> tuple:
    """Create standardized error response"""
    return jsonify({
        'success': False,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }), code