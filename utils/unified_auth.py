from functools import wraps
from flask import session, request, jsonify, redirect, url_for
import logging

logger = logging.getLogger(__name__)

def require_auth(allow_demo=False):
    """Unified authentication decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if authenticated
            if 'user' in session and session['user']:
                return f(*args, **kwargs)
                
            # Check demo mode if allowed
            if allow_demo and request.args.get('demo') == 'true':
                session['user'] = {'id': 'demo_user', 'name': 'Demo User', 'is_demo': True}
                return f(*args, **kwargs)
            
            # Handle unauthenticated
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
            
        return decorated_function
    return decorator

# Convenience decorators
login_required = require_auth(allow_demo=False)
demo_allowed = require_auth(allow_demo=True)

def get_demo_user():
    """Get demo user object"""
    return {
        'id': 'demo_user',
        'name': 'Demo User', 
        'email': 'demo@example.com',
        'is_demo': True
    }

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session and session['user'] is not None
