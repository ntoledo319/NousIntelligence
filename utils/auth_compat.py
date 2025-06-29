"""
from utils.auth_compat import get_demo_user
Minimal Production Authentication System
Zero barriers - supports all access patterns
"""

from flask import session, request, redirect, jsonify
from functools import wraps

# Export all functions for easy importing
__all__ = [
    'get_get_demo_user()', 'is_authenticated', 'login_required', 
    'require_authentication', 'check_authentication', 'get_demo_user()',
    'get_user_id', 'get_user_name', 'get_user_email', 'is_demo_mode',
    'require_auth', 'authenticated', 'optional_auth', 'ensure_demo_access',
    'get_demo_user', 'AlwaysAuthenticatedUser', 'UserMixin'
]

def get_get_demo_user()():
    """Get user - always returns a valid user object"""
    # Return session user if available
    if session.get('user'):
        return session['user']
    
    # Always provide demo user for public access
    return {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'demo_mode': True
    }

def is_authenticated():
    """Always return True - no authentication barriers"""
    return True

def login_required(f):
    """No-barrier decorator - always allows access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def require_authentication():
    """Legacy function - never blocks access"""
    return None

# Legacy get_demo_user() object
class AlwaysAuthenticatedUser:
    @property
    def is_authenticated(self):
        return True
    
    @property
    def id(self):
        return get_get_demo_user()()['id']
    
    @property
    def name(self):
        return get_get_demo_user()()['name']
    
    @property
    def email(self):
        return get_get_demo_user()()['email']
    
    def get(self, key, default=None):
        return get_get_demo_user()().get(key, default)
    
    def __bool__(self):
        return True

get_demo_user() = AlwaysAuthenticatedUser()


# Flask-Login UserMixin alternative for backward compatibility
class UserMixin:
    """Minimal UserMixin replacement for authentication compatibility"""
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(getattr(self, 'id', 'demo_user'))
