"""
Enhanced Authentication Compatibility Layer
Provides comprehensive session-based authentication with demo mode support
"""

from flask import session, request, redirect, url_for, jsonify
from functools import wraps

def get_current_user():
    """Get current user from session or return demo user"""
    if 'user' in session and session['user']:
        return session['user']
    
    # Demo mode support
    if request and request.args.get('demo') == 'true':
        return {
            'id': 'demo_user',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True
        }
    
    # Return None for unauthenticated users
    return None

def is_authenticated():
    """Check if user is authenticated or in demo mode"""
    user = get_current_user()
    return user is not None

def login_required(f):
    """Enhanced login required decorator with demo mode support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        # Allow access if user is authenticated or in demo mode
        if user:
            return f(*args, **kwargs)
        
        # For API endpoints, return JSON
        if request and request.path.startswith('/api/'):
            return jsonify({
                'error': 'Authentication required',
                'demo_available': True,
                'demo_url': request.url + '?demo=true'
            }), 401
        
        # For web pages, redirect to demo
        return redirect('/demo')
    
    return decorated_function

def require_authentication():
    """Check authentication and return appropriate response"""
    user = get_current_user()
    
    if user:
        return None  # User is authenticated
    
    # For API endpoints
    if request and request.path.startswith('/api/'):
        return jsonify({
            'error': 'Demo mode - limited access',
            'demo': True
        }), 200
    
    # For web pages
    return redirect('/demo')

# Legacy compatibility
current_user = type('CurrentUser', (), {
    'is_authenticated': property(lambda self: is_authenticated()),
    'id': property(lambda self: get_current_user().get('id') if get_current_user() else None),
    'name': property(lambda self: get_current_user().get('name') if get_current_user() else None),
    'email': property(lambda self: get_current_user().get('email') if get_current_user() else None),
    'get': lambda self, key, default=None: get_current_user().get(key, default) if get_current_user() else default
})()
