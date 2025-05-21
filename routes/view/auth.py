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
    
    # Render the login page with Google authentication option
    return render_template('login.html')

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

@auth_bp.route('/admin-login', methods=['GET'])
def admin_login():
    """
    Special admin login for development and testing
    
    Returns:
        Redirect to dashboard or login page
    """
    from models import User, db
    from flask_login import login_user
    import uuid
    from datetime import datetime
    
    # This is only for development/testing purposes
    admin_email = 'toledonick98@gmail.com'
    
    # Check if admin user exists
    user = User.query.filter_by(email=admin_email).first()
    
    if not user:
        # Create admin user if it doesn't exist
        logger.info(f"Creating admin user for {admin_email}")
        user = User()
        user.id = str(uuid.uuid4())
        user.email = admin_email
        user.username = 'admin_' + admin_email.split('@')[0]
        user.first_name = 'Admin'
        user.last_name = 'User'
        user.active = True
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Update admin flag directly in database
        from sqlalchemy import text
        try:
            db.session.execute(text("UPDATE users SET is_admin = TRUE WHERE email = :email"), 
                               {"email": admin_email})
            db.session.commit()
            logger.info(f"Admin privileges granted to {admin_email}")
        except Exception as e:
            logger.error(f"Failed to set admin privileges: {str(e)}")
    
    # Log in the admin user
    user.last_login = datetime.utcnow()
    db.session.commit()
    login_user(user)
    
    flash("Welcome, Admin! You've been logged in automatically.", "success")
    logger.info(f"Admin user {admin_email} logged in via admin-login route")
    
    return redirect(url_for('dashboard.dashboard'))

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