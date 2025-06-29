"""
from utils.auth_compat import get_demo_user
Smart Shopping Routes Routes
Smart Shopping Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user(), is_authenticated

smart_shopping_routes_bp = Blueprint('smart_shopping_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user(), is_authenticated
    
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

def get_get_demo_user()():
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

Smart Shopping Routes

This module provides routes for smart shopping functionality.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

# Create blueprint
smart_shopping_bp = Blueprint('smart_shopping', __name__, url_prefix='/smart-shopping')

# Set up logger
logger = logging.getLogger(__name__)

@smart_shopping_bp.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Smart shopping homepage"""
    return render_template('smart_shopping/index.html')

@smart_shopping_bp.route('/recommendations')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def recommendations():
    """Product recommendations"""
    return render_template('smart_shopping/recommendations.html')

@smart_shopping_bp.route('/deals')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def deals():
    """Current deals and discounts"""
    return render_template('smart_shopping/deals.html')