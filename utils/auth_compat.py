"""
Authentication Compatibility Layer
Bridges session-based authentication (app.py) with Flask-Login patterns (routes)
"""

from flask import session, request, redirect, url_for, jsonify, g
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CurrentUser:
    """Mock current_user object that uses session data"""
    
    @property
    def is_authenticated(self):
        return 'user' in session and session['user'] is not None
    
    @property
    def is_anonymous(self):
        return not self.is_authenticated
    
    @property
    def is_active(self):
        return self.is_authenticated
    
    @property
    def id(self):
        if self.is_authenticated:
            return session['user'].get('id', 'anonymous')
        return None
    
    @property
    def name(self):
        if self.is_authenticated:
            return session['user'].get('name', 'Anonymous')
        return 'Anonymous'
    
    @property
    def email(self):
        if self.is_authenticated:
            return session['user'].get('email', 'anonymous@example.com')
        return 'anonymous@example.com'
    
    def get(self, key, default=None):
        if self.is_authenticated:
            return session['user'].get(key, default)
        return default
    
    def get_id(self):
        return self.id

# Global current_user object
current_user = CurrentUser()

def login_required(f):
    """Decorator that requires authentication, with demo mode support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication
        if 'user' in session and session['user']:
            return f(*args, **kwargs)
        
        # Allow demo mode
        if request.args.get('demo') == 'true':
            # Create temporary demo user in session
            session['user'] = {
                'id': 'demo_user',
                'name': 'Demo User',
                'email': 'demo@nous.app',
                'demo': True
            }
            return f(*args, **kwargs)
        
        # For API endpoints, return JSON error
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Authentication required', 
                'demo_available': True,
                'demo_url': request.url + '?demo=true'
            }), 401
        
        # For web routes, redirect to login
        return redirect(url_for('login'))
    
    return decorated_function

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        # Create temporary demo user in session
        session['user'] = {
            'id': 'demo_user',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo': True
        }
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Authentication required', 
            'demo_available': True,
            'demo_url': request.url + '?demo=true'
        }), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    if 'user' in session and session['user']:
        return session['user']
    return {
        'id': 'anonymous',
        'name': 'Anonymous User',
        'email': 'anonymous@example.com',
        'demo': True
    }

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session and session['user']

# Flask-Login compatibility functions
def login_user(user, remember=False):
    """Login user by storing in session"""
    session['user'] = user
    session.permanent = remember
    logger.info(f"User logged in: {user.get('email', 'unknown')}")

def logout_user():
    """Logout user by clearing session"""
    session.pop('user', None)
    logger.info("User logged out")

def fresh_login_required(f):
    """Alias for login_required"""
    return login_required(f)
