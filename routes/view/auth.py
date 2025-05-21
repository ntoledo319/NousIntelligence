"""
Authentication View Routes

This module contains view routes for user authentication,
including login, logout and registration.

@module routes.view.auth
@description Authentication routes with enhanced security
"""

import logging
import os
import secrets
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logger
logger = logging.getLogger(__name__)

# Create CSRF protection
csrf = CSRFProtect()

@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Login handler - renders the login page with Google authentication option
    
    Returns:
        Rendered login page or redirect to dashboard if already logged in
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
    logger.info(f"Login page accessed from IP: {client_ip}")
    
    # Generate CSRF token
    csrf_token = generate_csrf()
    
    # Render the login page with Google authentication option
    return render_template('login.html', csrf_token=csrf_token)
    
@auth_bp.route('/email-login', methods=['POST'])
def email_login():
    """
    Handle email/password login
    
    Returns:
        Redirect to dashboard on success or login page on failure
    """
    from models import User, UserSettings, db
    from flask_login import login_user
    from datetime import datetime
    
    # Rate limiting check
    if not check_rate_limit(request.remote_addr, 'login_attempt'):
        flash('Too many login attempts. Please try again later.', 'danger')
        logger.warning(f"Rate limit exceeded for login from IP: {request.remote_addr}")
        return redirect(url_for('auth.login'))
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please enter both email and password', 'danger')
        return redirect(url_for('auth.login'))
    
    # Look up the user by email
    user = User.query.filter_by(email=email).first()
    
    # Regular user login path
    if user and user.password_hash and check_password_hash(user.password_hash, password):
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        
        flash("You have been logged in successfully.", "success")
        logger.info(f"User {email} logged in via email login")
        
        # Redirect to intended page if set, otherwise dashboard
        next_page = session.get('next')
        if next_page:
            session.pop('next', None)
            return redirect(next_page)
            
        return redirect(url_for('dashboard.dashboard'))
    
    # Login failed
    flash("Invalid email or password. Please try again.", "danger")
    logger.warning(f"Failed login attempt for {email}")
    return redirect(url_for('auth.login'))

@auth_bp.route('/direct-google-login', methods=['GET'])
def direct_google_login():
    """
    Direct redirect to Google authentication
    
    Returns:
        Redirects to the Google OAuth login route
    """
    # Log the direct Google auth attempt
    logger.info("Direct Google authentication requested")
    
    # Redirect to Google auth login
    return redirect(url_for("google_auth.login"))

# Remove insecure admin_login route
# Admin access should only be done through secure authentication

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

def check_rate_limit(ip_address, action_type):
    """
    Check if the rate limit has been exceeded for an IP address and action
    
    Args:
        ip_address: The client's IP address
        action_type: The type of action (login_attempt, etc.)
        
    Returns:
        Boolean indicating if the action should be allowed
    """
    try:
        from models import RateLimit, db
        from datetime import datetime, timedelta
        
        # Define rate limits based on action type
        limits = {
            'login_attempt': {'count': 5, 'window': 5},  # 5 attempts in 5 minutes
            'password_reset': {'count': 3, 'window': 60},  # 3 attempts in 60 minutes
            'account_creation': {'count': 3, 'window': 60}  # 3 attempts in 60 minutes
        }
        
        if action_type not in limits:
            return True  # No limit defined for this action
            
        limit_config = limits[action_type]
        
        # Calculate the start of the window period
        window_start = datetime.utcnow() - timedelta(minutes=limit_config['window'])
        
        # Check for existing rate limit records
        attempts = RateLimit.query.filter(
            RateLimit.ip_address == ip_address,
            RateLimit.action_type == action_type,
            RateLimit.timestamp > window_start
        ).count()
        
        if attempts >= limit_config['count']:
            return False  # Rate limit exceeded
            
        # Record this attempt
        rate_limit = RateLimit(
            ip_address=ip_address,
            action_type=action_type,
            timestamp=datetime.utcnow()
        )
        db.session.add(rate_limit)
        db.session.commit()
        
        return True  # Rate limit not exceeded
    except Exception as e:
        logger.error(f"Error in rate limiting: {str(e)}")
        return True  # Allow the action in case of error