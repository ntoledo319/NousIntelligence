"""

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
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

User Routes

This module provides routes for user account management,
including profile viewing and editing.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Set up logger
logger = logging.getLogger(__name__)

@user_bp.route('/profile')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def profile():
    """Display user profile page"""
    return render_template('user/profile.html')

@user_bp.route('/preferences')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def preferences():
    """Display user preferences page"""
    return render_template('user/preferences.html')

@user_bp.route('/activity')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def activity():
    """Display user activity history"""
    return render_template('user/activity.html')