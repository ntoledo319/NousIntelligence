"""
Authentication Routes

This module implements the core authentication routes for the application.

@module auth.routes
@description Core authentication routes
"""

import logging
import uuid
import time
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import secrets

from auth import auth_bp
from models import User, UserSettings, db
from utils.login_security import track_login_attempt, log_security_event, is_secure_password, cleanup_expired_sessions

logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with enhanced security"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    # For anti-CSRF protection
    if request.method == 'GET':
        session['login_csrf_token'] = secrets.token_hex(16)
        
    if request.method == 'POST':
        # Verify CSRF token
        csrf_token = session.pop('login_csrf_token', None)
        form_csrf_token = request.form.get('csrf_token')
        if not csrf_token or not form_csrf_token or csrf_token != form_csrf_token:
            logger.warning(f"CSRF token mismatch during login attempt from {request.remote_addr}")
            flash('Session expired. Please try again.', 'warning')
            return render_template('login.html', csrf_token=secrets.token_hex(16))
            
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        # Insert short delay to prevent timing attacks
        time.sleep(0.1)
        
        # Validate input
        if not email or not password:
            flash('Please fill in all fields.', 'warning')
            return render_template('login.html', csrf_token=secrets.token_hex(16))
        
        # Check for account lockout
        is_allowed, lockout_minutes = track_login_attempt(email, success=False)
        if not is_allowed:
            flash(f'Account temporarily locked due to too many failed attempts. '
                  f'Please try again in {lockout_minutes} minutes.', 'danger')
            log_security_event('account_lockout', details=f"Account {email} locked for {lockout_minutes} minutes")
            return render_template('login.html', csrf_token=secrets.token_hex(16))
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Create a default admin user if none exists and this is a special login
        if not user and email == 'admin@example.com' and password == 'admin123':
            try:
                # Create a new admin user
                user = User()
                user.id = str(uuid.uuid4())
                user.email = 'admin@example.com'
                user.username = 'admin'
                user.first_name = 'Admin'
                user.last_name = 'User'
                user.active = True
                
                # Set password with better security
                user.set_password('admin123')
                
                # Add user to database
                db.session.add(user)
                db.session.commit()
                
                # Create settings for the user
                settings = UserSettings()
                settings.user_id = user.id
                settings.theme = 'light'
                settings.language = 'en'
                settings.timezone = 'UTC'
                settings.notifications_enabled = True
                
                # Add settings to database
                db.session.add(settings)
                db.session.commit()
                
                logger.info("Default admin user created during login attempt")
                log_security_event('admin_created', user.id, "Default admin user created")
                flash('Default admin account created. Welcome!', 'success')
            except Exception as e:
                logger.error(f"Error creating default user: {str(e)}")
                db.session.rollback()
                flash('Error creating default user. Please try again.', 'danger')
                return render_template('login.html', csrf_token=secrets.token_hex(16))
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for {email} from {request.remote_addr}")
            flash('Please check your login details and try again.', 'danger')
            return render_template('login.html', csrf_token=secrets.token_hex(16))
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Login attempt on inactive account: {email}")
            flash('This account has been deactivated. Please contact support.', 'danger')
            log_security_event('inactive_account_login_attempt', user.id, f"Login attempt on inactive account from {request.remote_addr}")
            return render_template('login.html', csrf_token=secrets.token_hex(16))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Reset failed login attempts
        track_login_attempt(email, success=True)
        
        # Log in user
        login_user(user, remember=remember)
        logger.info(f"User {email} logged in successfully from {request.remote_addr}")
        log_security_event('login_success', user.id, f"User logged in from {request.remote_addr}")
        
        # Clean up expired sessions
        cleanup_expired_sessions()
        
        # Redirect to intended URL or dashboard
        next_url = session.get('next_url')
        if next_url:
            session.pop('next_url', None)
            return redirect(next_url)
        return redirect(url_for('dashboard.dashboard'))
    
    # GET request - show login form with CSRF token
    return render_template('login.html', csrf_token=session.get('login_csrf_token', ''))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with enhanced security"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    # For anti-CSRF protection
    if request.method == 'GET':
        session['register_csrf_token'] = secrets.token_hex(16)
        return render_template('register.html', csrf_token=session.get('register_csrf_token', ''))
        
    if request.method == 'POST':
        # Verify CSRF token
        csrf_token = session.pop('register_csrf_token', None)
        form_csrf_token = request.form.get('csrf_token')
        if not csrf_token or not form_csrf_token or csrf_token != form_csrf_token:
            logger.warning(f"CSRF token mismatch during registration attempt from {request.remote_addr}")
            flash('Session expired. Please try again.', 'warning')
            return redirect(url_for('auth.register'))
            
        # Get form data
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        
        # Validate input
        if not email or not username or not password or not confirm:
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('auth.register'))
            
        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check password security
        is_secure, reason = is_secure_password(password)
        if not is_secure:
            flash(f'Password not secure: {reason}', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            # Don't reveal if user exists for security reasons
            flash('Registration failed. Please try again with different credentials.', 'warning')
            log_security_event('registration_duplicate_attempt', details=f"Duplicate registration attempt for {email}")
            return redirect(url_for('auth.register'))
        
        # Check if username is taken
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username is already taken. Please choose another.', 'warning')
            return redirect(url_for('auth.register'))
        
        try:
            # Create new user
            new_user = User()
            new_user.id = str(uuid.uuid4())
            new_user.email = email
            new_user.username = username
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.set_password(password)
            new_user.email_verified = False  # Require verification
            new_user.active = True
            
            # Add user to database
            db.session.add(new_user)
            db.session.commit()
            
            # Create default settings for the user
            settings = UserSettings()
            settings.user_id = new_user.id
            
            # Add settings to the database
            db.session.add(settings)
            db.session.commit()
            
            logger.info(f"New user registered: {email}")
            log_security_event('user_registered', new_user.id, f"New user registered from {request.remote_addr}")
            
            # Log in the new user
            login_user(new_user)
            
            # Redirect to email verification page or welcome page
            flash('Your account has been created successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    # GET request - display registration form
    return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout with enhanced security"""
    user_id = current_user.id if current_user.is_authenticated else None
    
    # Log security event before logout
    if user_id:
        log_security_event('logout', user_id, f"User logged out from {request.remote_addr}")
        logger.info(f"User {current_user.email} logged out")
    
    # Perform logout
    logout_user()
    
    # Clear session data
    session.clear()
    
    # Create a new CSRF token for security
    session['csrf_token'] = secrets.token_hex(16)
    
    # Display feedback
    flash('You have been logged out successfully.', 'success')
    
    # Redirect to login page
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change with enhanced security"""
    if request.method == 'GET':
        session['password_csrf_token'] = secrets.token_hex(16)
        return render_template('change_password.html', csrf_token=session.get('password_csrf_token', ''))
        
    if request.method == 'POST':
        # Verify CSRF token
        csrf_token = session.pop('password_csrf_token', None)
        form_csrf_token = request.form.get('csrf_token')
        if not csrf_token or not form_csrf_token or csrf_token != form_csrf_token:
            logger.warning(f"CSRF token mismatch during password change attempt from {request.remote_addr}")
            flash('Session expired. Please try again.', 'warning')
            return redirect(url_for('auth.change_password'))
            
        # Get form data
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all fields.', 'warning')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('New passwords do not match.', 'warning')
            return redirect(url_for('auth.change_password'))
            
        # Verify current password
        if not current_user.check_password(current_password):
            logger.warning(f"Invalid current password during password change for {current_user.email}")
            flash('Current password is incorrect.', 'danger')
            log_security_event('password_change_failed', current_user.id, "Invalid current password")
            return redirect(url_for('auth.change_password'))
            
        # Check if new password is different from current
        if current_password == new_password:
            flash('New password must be different from current password.', 'warning')
            return redirect(url_for('auth.change_password'))
            
        # Check password security
        is_secure, reason = is_secure_password(new_password)
        if not is_secure:
            flash(f'Password not secure: {reason}', 'warning')
            return redirect(url_for('auth.change_password'))
            
        try:
            # Update password
            current_user.set_password(new_password)
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log security event
            log_security_event('password_changed', current_user.id, f"Password changed from {request.remote_addr}")
            logger.info(f"Password changed for user {current_user.email}")
            
            # Notify user
            flash('Your password has been changed successfully.', 'success')
            
            # Redirect to profile page
            return redirect(url_for('dashboard.profile'))
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('auth.change_password'))
    
    # GET request - show password change form
    return redirect(url_for('auth.change_password')) 