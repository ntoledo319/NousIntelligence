"""
Authentication View Routes

This module contains view routes for user authentication,
including login, logout and registration.

@module routes.view.auth
@author NOUS Development Team
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, logout_user, current_user

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logger
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Unified login handler - redirects to Google authentication
    
    Returns:
        Redirects to the Google OAuth login route
    """
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    # Get the next URL if it exists
    next_url = request.args.get('next', '')
    
    # Store next URL in session for post-login redirect
    if next_url:
        session['next'] = next_url
    
    # Log access to login page
    client_ip = request.remote_addr
    logger.info(f"Login page accessed from IP: {client_ip}, redirecting to Google auth")
    
    # Redirect to Google auth login to maintain a single sign-in flow
    return redirect(url_for("google_auth.login"))

@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    Logout the current user and redirect to home page
    
    Returns:
        Redirect to the home page after logout
    """
    # Get user info for logging
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    logger.info(f"User logged out: {user_email}")
    
    # Log the user out
    logout_user()
    
    # Clear session data
    session.clear()
    
    # Flash message
    flash("You have been successfully logged out.", "success")
    
    # Redirect to home page
    return redirect(url_for('index.index'))