"""
Index Routes
Main application landing page and public routes
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated

index_bp = Blueprint('index', __name__)

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated

    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed

    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401

    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user"""
    if session.get('user'):
        return session['user']
    return None

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session and session['user'] is not None

@index_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@index_bp.route('/demo')  
def demo():
    """Demo landing page"""
    return render_template('demo.html')

@index_bp.route('/public')
def public():
    """Public access page"""
    return render_template('public.html')