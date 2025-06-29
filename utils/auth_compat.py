"""
Complete Authentication Compatibility Layer
Provides full demo user support with zero authentication barriers
"""

from flask import session, request
from datetime import datetime
from functools import wraps

class DemoUser:
    """Demo user class with Flask-Login compatibility"""
    def __init__(self):
        self.id = 'demo_user_123'
        self.name = 'Demo User'
        self.email = 'demo@nous.app'
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.demo_mode = True
        self.login_time = datetime.now().isoformat()
    
    def get_id(self):
        return self.id

def get_demo_user():
    """Get demo user instance"""
    return DemoUser()

def is_authenticated():
    """Always return True for demo mode"""
    return True

def login_required(f):
    """No-barrier decorator that ensures demo user in session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure demo user is in session
        if 'user' not in session:
            session['user'] = {
                'id': 'demo_user_123',
                'name': 'Demo User',
                'email': 'demo@nous.app',
                'demo_mode': True
            }
        return f(*args, **kwargs)
    return decorated_function

def auth_not_required(f):
    """Alias for login_required (no barriers)"""
    return login_required(f)

# Global instances for compatibility
current_user = get_demo_user()

def ensure_demo_session():
    """Ensure demo user is in Flask session"""
    if 'user' not in session:
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User', 
            'email': 'demo@nous.app',
            'demo_mode': True,
            'is_authenticated': True
        }
    return session['user']

def get_current_user():
    """Get current user (always demo user)"""
    ensure_demo_session()
    return get_demo_user()
