"""
Admin Routes Routes
Admin Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

admin_routes_bp = Blueprint('admin_routes', __name__)

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_demo_user():
    """Get current user from session with demo fallback"""
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

"""
Admin Routes

This module provides routes for admin functionality.
"""

import logging
from flask import flash, abort

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Set up logger
logger = logging.getLogger(__name__)

@admin_bp.route('/')
def index():
    """Admin dashboard"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    # Check if user is admin (placeholder)
    if not ('user' in session and session['user']) or not getattr(session.get('user'), 'is_admin', False):
        return jsonify({"error": "Demo mode - limited access", "demo": True}), 200
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
def users():
    """User management"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    # Check if user is admin (placeholder)
    if not ('user' in session and session['user']) or not getattr(session.get('user'), 'is_admin', False):
        return jsonify({"error": "Demo mode - limited access", "demo": True}), 200
    # Placeholder for user list
    users = []
    return render_template('admin/users.html', users=users)