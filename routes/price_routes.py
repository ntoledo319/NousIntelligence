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

Price Tracking Routes

This module provides routes for price tracking functionality.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

# Create blueprint
price_tracking_bp = Blueprint('price_tracking', __name__, url_prefix='/price-tracking')

# Set up logger
logger = logging.getLogger(__name__)

@price_tracking_bp.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Price tracking homepage"""
    return render_template('price_tracking/index.html')

@price_tracking_bp.route('/tracked-items')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def tracked_items():
    """View tracked items"""
    return render_template('price_tracking/tracked_items.html')

@price_tracking_bp.route('/add', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_item():
    """Add new item to track"""
    if request.method == 'GET':
        return render_template('price_tracking/add_item.html')

    # POST handling (placeholder)
    flash('Item added successfully', 'success')
    return redirect(url_for('price_tracking.tracked_items'))