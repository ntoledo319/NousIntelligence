"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
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

Index Routes Module

This module defines routes for the main pages of the application.

@module routes.index
@description Main application routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from datetime import datetime
from models.user import User
from app_factory import db

# Create blueprint
index_bp = Blueprint('index', __name__)
logger = logging.getLogger(__name__)

@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Render the index page with integrated login functionality"""
    # For public preview access - always render the welcome page
    # This change is for Replit deploy button to work without login
    if request.host.endswith('.repl.co') or 'REPLIT_DEPLOYMENT' in request.environ:
        return render_template('index_public.html', public_preview=True)

    # If user is already logged in, just show the index page
    if ('user' in session and session['user']):
        return render_template('index.html')

    # Handle login form submission if this is a POST request
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Validate input
        if not email or not password:
            flash('Please fill in all fields.', 'warning')
            return render_template('index.html')

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('index.html')

        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Log in user
        login_user(user, remember=remember)
        logger.info(f"User {email} logged in successfully from index page")

        # Redirect to dashboard
        return redirect(url_for('dashboard.dashboard'))

    # GET request - show index page with login form
    return render_template('index.html')

@index_bp.route('/help')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def help_page():
    """Render the help page"""
    return render_template('help.html')