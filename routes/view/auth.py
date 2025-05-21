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
    
@auth_bp.route('/email-login', methods=['POST'])
def email_login():
    """
    Handle email/password login
    
    Returns:
        Redirect to dashboard on success or login page on failure
    """
    from models import User, UserSettings, db
    from flask_login import login_user
    from werkzeug.security import generate_password_hash, check_password_hash
    import uuid
    from datetime import datetime
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please enter both email and password', 'danger')
        return redirect(url_for('auth.login'))
    
    # Check if this is the admin user with the special password
    admin_email = 'toledonick98@gmail.com'
    admin_password = 'nousadmin2025'
    
    # Look up the user by email
    user = User.query.filter_by(email=email).first()
    
    # Special admin login path
    if email == admin_email and password == admin_password:
        logger.info(f"Admin login attempt for {email}")
        
        # If admin user doesn't exist, create it
        if not user:
            logger.info(f"Creating admin user for {email}")
            user = User()
            user.id = str(uuid.uuid4())
            user.email = email
            user.username = 'admin_' + email.split('@')[0]
            user.first_name = 'Admin'
            user.last_name = 'User'
            user.active = True
            user.password_hash = generate_password_hash(admin_password)
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # Create default settings
            settings = UserSettings()
            settings.user_id = user.id
            db.session.add(settings)
            db.session.commit()
            
            # Update admin flag directly in database
            from sqlalchemy import text
            try:
                db.session.execute(text("UPDATE users SET is_admin = TRUE WHERE email = :email"), 
                                  {"email": email})
                db.session.commit()
                logger.info(f"Admin privileges granted to {email}")
            except Exception as e:
                logger.error(f"Failed to set admin privileges: {str(e)}")
        
        # Log in the admin user
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        
        flash("Welcome, Admin! You've been logged in successfully.", "success")
        logger.info(f"Admin user {email} logged in via email login")
        
        return redirect(url_for('dashboard.dashboard'))
    
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