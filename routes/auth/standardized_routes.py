"""

from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
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

Standardized Authentication Routes

This module implements authentication routes using standardized routing patterns.
"""

import logging
from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify

# Import our standardized URL utilities
from utils.url_utils import normalize_path, validate_url_path

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint with standardized naming
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def login():
    """
    Handle user login

    This endpoint handles both the login form display (GET)
    and the login form submission (POST).
    """
    if request.method == 'GET':
        return render_template('auth/login.html', title='Login')

    # Handle login POST request
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        # Log login attempt (without password)
        logger.info(f"Login attempt for user: {username}")

        # TODO: Implement actual authentication logic

        # Simulate successful login
        session['logged_in'] = True
        session['username'] = username

        # Redirect to requested page or default to dashboard
        next_page = request.args.get('next')
        if next_page and validate_url_path(next_page):
            return redirect(next_page)
        else:
            return redirect(url_for('main.dashboard'))

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        flash('Login failed. Please try again.', 'error')
        return render_template('auth/login.html', title='Login'), 401

@auth_bp.route('/logout')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def logout():
    """
    Handle user logout

    This endpoint clears the user session and redirects to the login page.
    """
    # Clear session data
    session.clear()

    # Redirect to login page
    return redirect(url_for("main.demo"))

@auth_bp.route('/register', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def register():
    """
    Handle user registration

    This endpoint handles both the registration form display (GET)
    and the registration form submission (POST).
    """
    if request.method == 'GET':
        return render_template('auth/register.html', title='Register')

    # Handle registration POST request
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Log registration attempt (without password)
        logger.info(f"Registration attempt for user: {username}, email: {email}")

        # TODO: Implement actual registration logic

        # Simulate successful registration
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for("main.demo"))

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html', title='Register'), 400

@auth_bp.route('/password/reset', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def password_reset_request():
    """
    Handle password reset request

    This endpoint handles both the password reset request form display (GET)
    and the form submission (POST).
    """
    if request.method == 'GET':
        return render_template('auth/password_reset_request.html', title='Reset Password')

    # Handle password reset request POST
    try:
        email = request.form.get('email')

        # Log password reset request
        logger.info(f"Password reset requested for email: {email}")

        # TODO: Implement actual password reset logic

        # Simulate successful request
        flash('If your email is registered, you will receive password reset instructions.', 'info')
        return redirect(url_for("main.demo"))

    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return render_template('auth/password_reset_request.html', title='Reset Password'), 400

@auth_bp.route('/password/reset/<token>', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def password_reset(token):
    """
    Handle password reset with token

    This endpoint handles both the password reset form display (GET)
    and the form submission (POST).

    Args:
        token: Password reset token
    """
    # Validate token
    # TODO: Implement actual token validation

    if request.method == 'GET':
        return render_template('auth/password_reset.html', token=token, title='Set New Password')

    # Handle password reset POST
    try:
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/password_reset.html', token=token, title='Set New Password')

        # Log password reset (without password)
        logger.info(f"Password reset with token: {token}")

        # TODO: Implement actual password reset logic

        # Simulate successful reset
        flash('Your password has been reset. Please log in with your new password.', 'success')
        return redirect(url_for("main.demo"))

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return render_template('auth/password_reset.html', token=token, title='Set New Password'), 400