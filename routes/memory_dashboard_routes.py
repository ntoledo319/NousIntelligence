"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Memory Dashboard Routes Routes
Memory Dashboard Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

memory_dashboard_routes_bp = Blueprint('memory_dashboard_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
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

Memory Dashboard Routes

This module provides routes for the memory dashboard UI, displaying
the user's accumulated conversation history and memory data.

@module routes.memory_dashboard_routes
@description User memory dashboard routes
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash

from services.memory_service import get_memory_service

logger = logging.getLogger(__name__)

# Create blueprint
memory_dashboard_bp = Blueprint('memory_dashboard', __name__, url_prefix='/memory')

@memory_dashboard_bp.route('/', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def memory_dashboard():
    """
    Display the memory dashboard with user memory data

    Returns:
        Rendered memory dashboard template
    """
    try:
        memory_service = get_memory_service()

        # Ensure memory is initialized for the user
        memory_service.initialize_memory_for_user(session.get('user', {}).get('id', 'demo_user'))

        # Render the dashboard
        return render_template('memory_dashboard.html')
    except Exception as e:
        logger.error(f"Error displaying memory dashboard: {str(e)}")
        flash("An error occurred while loading your memory dashboard", "danger")
        return redirect(url_for('dashboard.dashboard'))

def register_memory_dashboard_routes(app):
    """Register memory dashboard routes with the Flask app"""
    app.register_blueprint(memory_dashboard_bp)
    logger.info("Memory dashboard routes registered")