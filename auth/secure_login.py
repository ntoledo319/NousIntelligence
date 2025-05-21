"""
Secure Login Module

This module provides enhanced security for login functionality.
It includes measures against brute force attacks, credential stuffing, and other common threats.

@module auth.secure_login
@description Enhanced login security handlers
"""

import logging
import time
import secrets
import re
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from models import db, User

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
secure_login_bp = Blueprint('secure_login', __name__, url_prefix='/auth')

# In-memory stores for temporary security features
# In production, these would use Redis or a database
_failed_attempts = {}  # Track failed login attempts by email and IP
_lockouts = {}  # Track account lockouts
_ip_limits = {}  # Track IP-based rate limiting

def track_login_attempt(email, ip_address, success):
    """
    Track login attempts to detect and prevent brute force attacks
    
    Args:
        email: Email used in the login attempt
        ip_address: IP address of the request
        success: Whether the login was successful
    
    Returns:
        bool: True if account is now locked, False otherwise
    """
    timestamp = datetime.utcnow()
    
    # Track by email
    if email:
        if email not in _failed_attempts:
            _failed_attempts[email] = []
        
        # Add the attempt
        _failed_attempts[email].append({
            'timestamp': timestamp,
            'ip': ip_address,
            'success': success
        })
        
        # Keep only last 24 hours of attempts
        _failed_attempts[email] = [
            a for a in _failed_attempts[email]
            if a['timestamp'] > timestamp - timedelta(hours=24)
        ]
        
        # Check for too many recent failed attempts
        recent_failures = [
            a for a in _failed_attempts[email]
            if not a['success'] and a['timestamp'] > timestamp - timedelta(minutes=30)
        ]
        
        if len(recent_failures) >= 5:
            # Lock the account
            lock_account(email, ip_address, "Too many failed login attempts")
            return True
    
    # Track by IP
    if ip_address:
        if ip_address not in _ip_limits:
            _ip_limits[ip_address] = []
        
        # Add the attempt
        _ip_limits[ip_address].append({
            'timestamp': timestamp,
            'email': email,
            'success': success
        })
        
        # Keep only last 24 hours
        _ip_limits[ip_address] = [
            a for a in _ip_limits[ip_address]
            if a['timestamp'] > timestamp - timedelta(hours=24)
        ]
        
        # Check if this IP is trying too many different accounts (credential stuffing)
        recent_attempts = [
            a for a in _ip_limits[ip_address]
            if a['timestamp'] > timestamp - timedelta(minutes=10)
        ]
        
        unique_emails = set(a['email'] for a in recent_attempts if a['email'])
        
        if len(unique_emails) > 5:
            # This could be credential stuffing - log and throttle
            logger.warning(f"Possible credential stuffing from {ip_address}: {len(unique_emails)} accounts in 10 minutes")
            # Implement some form of IP throttling here
    
    return False

def lock_account(email, ip_address=None, reason="Security policy"):
    """
    Lock an account for security reasons
    
    Args:
        email: Email of the account to lock
        ip_address: IP address that triggered the lockout (optional)
        reason: Reason for the lockout
    """
    # Set lockout with 1 hour duration by default
    _lockouts[email] = {
        'locked_at': datetime.utcnow(),
        'reason': reason,
        'ip': ip_address,
        'unlock_at': datetime.utcnow() + timedelta(hours=1)
    }
    
    logger.warning(f"Account locked: {email} from {ip_address} - {reason}")
    
    # If integrated with database, update user record
    user = User.query.filter_by(email=email).first()
    if user:
        # This would be stored in the security_audit_log in a full implementation
        # Here we just log it
        logger.info(f"Security event: account_locked for user {user.id} ({email})")

def is_account_locked(email):
    """
    Check if an account is currently locked
    
    Args:
        email: Email of the account to check
        
    Returns:
        tuple: (is_locked, reason, unlock_time)
    """
    if email not in _lockouts:
        return False, None, None
    
    lockout = _lockouts[email]
    
    # Check if lockout has expired
    if lockout['unlock_at'] <= datetime.utcnow():
        # Auto-unlock
        del _lockouts[email]
        return False, None, None
    
    return True, lockout['reason'], lockout['unlock_at']

def unlock_account(email):
    """
    Manually unlock an account
    
    Args:
        email: Email of the account to unlock
        
    Returns:
        bool: True if account was unlocked, False if it wasn't locked
    """
    if email in _lockouts:
        del _lockouts[email]
        
        # Clear failed attempts
        if email in _failed_attempts:
            _failed_attempts[email] = []
        
        logger.info(f"Account manually unlocked: {email}")
        return True
    
    return False

def is_password_leaked(password):
    """
    Check if a password appears in known data breaches
    (Simplified version - in production would use services like HaveIBeenPwned)
    
    Args:
        password: Password to check
        
    Returns:
        bool: True if password appears to be leaked
    """
    # Common passwords that have appeared in data breaches
    common_passwords = [
        "123456", "password", "123456789", "12345678", "12345", "qwerty",
        "1234567", "111111", "1234567890", "123123", "abc123", "1234", 
        "password1", "iloveyou", "1q2w3e4r", "000000", "qwerty123", 
        "zaq12wsx", "dragon", "sunshine", "princess", "letmein", "welcome",
        "monkey", "admin", "login", "football"
    ]
    
    return password.lower() in common_passwords

def is_password_strong(password):
    """
    Check if a password meets strong password requirements
    
    Args:
        password: Password to check
        
    Returns:
        tuple: (is_strong, message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    # Check for various character types
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[^A-Za-z0-9]', password))
    
    if not (has_uppercase and has_lowercase and has_digit and has_special):
        return False, "Password must include uppercase and lowercase letters, numbers, and special characters"
    
    # Check for common patterns
    if re.search(r'12345|qwerty|asdfgh|zxcvb', password.lower()):
        return False, "Password contains a common pattern"
    
    # Check for repeated characters
    if re.search(r'(.)\1{2,}', password):
        return False, "Password contains too many repeated characters"
    
    return True, "Password meets security requirements"

def generate_secure_token():
    """
    Generate a cryptographically secure token
    
    Returns:
        str: Secure token
    """
    return secrets.token_urlsafe(32)

def log_security_event(event_type, user_id=None, description=None):
    """
    Log a security-related event
    
    Args:
        event_type: Type of security event
        user_id: User ID (if available)
        description: Description of the event
    """
    # In a full implementation, this would write to a database
    # For now, we just log it
    ip = request.remote_addr
    user_agent = request.user_agent.string if request.user_agent else "Unknown"
    
    logger.info(f"Security event: {event_type} - User: {user_id} - IP: {ip} - UA: {user_agent} - {description}")

# Define routes

@secure_login_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced secure login route"""
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Track login IP for security
    ip_address = request.remote_addr
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = secrets.token_hex(16)
        session['csrf_token'] = csrf_token
        
        return render_template('auth/login.html', csrf_token=csrf_token)
    
    elif request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            log_security_event('csrf_validation_failed', None, f"CSRF validation failed from {ip_address}")
            return redirect(url_for('secure_login.login'))
        
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Validate input
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html', csrf_token=csrf_token)
        
        # Check if account is locked
        locked, reason, unlock_time = is_account_locked(email)
        if locked:
            flash(f'This account is temporarily locked. Please try again later or contact support.', 'danger')
            log_security_event('login_attempt_locked_account', None, f"Login attempt on locked account {email}")
            return render_template('auth/login.html', csrf_token=csrf_token, locked=True, unlock_time=unlock_time)
        
        # Get user from database
        user = User.query.filter_by(email=email).first()
        
        # Check for invalid credentials
        if not user or not check_password_hash(user.password_hash, password):
            # Track failed attempt
            track_login_attempt(email, ip_address, False)
            
            # Generic error message to prevent username enumeration
            flash('Invalid email or password. Please try again.', 'danger')
            
            # Log the failed attempt
            if user:
                log_security_event('failed_login', user.id, f"Failed login attempt for {email}")
            else:
                log_security_event('failed_login_nonexistent_user', None, f"Failed login attempt for nonexistent user {email}")
            
            return render_template('auth/login.html', csrf_token=csrf_token)
        
        # Check if account is active
        if hasattr(user, 'is_active') and not user.is_active:
            flash('This account has been deactivated. Please contact support.', 'danger')
            log_security_event('login_attempt_inactive_account', user.id, f"Login attempt on inactive account {email}")
            return render_template('auth/login.html', csrf_token=csrf_token)
        
        # Login successful
        login_user(user, remember=remember)
        
        # Update user's last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Clear any failed attempts
        if email in _failed_attempts:
            _failed_attempts[email] = []
        
        # Track successful login
        track_login_attempt(email, ip_address, True)
        
        # Log successful login
        log_security_event('successful_login', user.id, f"Successful login for {email}")
        
        # Get redirect target (with safety check to prevent open redirects)
        next_page = request.args.get('next')
        if next_page and not next_page.startswith('/'):
            next_page = None
        
        # Show password age warning if password is old
        if hasattr(user, 'password_last_changed'):
            password_age_days = (datetime.utcnow() - user.password_last_changed).days if user.password_last_changed else 90
            if password_age_days > 90:
                flash('Your password is over 90 days old. Please consider changing it.', 'warning')
        
        flash('Login successful!', 'success')
        return redirect(next_page or url_for('index'))

@secure_login_bp.route('/logout')
@login_required
def logout():
    """Secure logout route"""
    user_id = current_user.id if current_user.is_authenticated else None
    
    # Log the logout event
    log_security_event('logout', user_id, f"User logged out")
    
    # Clear session data
    session.clear()
    
    # Perform logout
    logout_user()
    
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@secure_login_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Secure password change route"""
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = secrets.token_hex(16)
        session['csrf_token'] = csrf_token
        
        return render_template('auth/change_password.html', csrf_token=csrf_token)
    
    elif request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('secure_login.change_password'))
        
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            log_security_event('password_change_failed', current_user.id, "Current password verification failed")
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Verify password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Check if new password is the same as current password
        if check_password_hash(current_user.password_hash, new_password):
            flash('New password must be different from your current password.', 'danger')
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Check password strength
        is_strong, message = is_password_strong(new_password)
        if not is_strong:
            flash(f'Password is not strong enough: {message}', 'danger')
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Check if password has been leaked
        if is_password_leaked(new_password):
            flash('This password has appeared in a data breach. Please choose a different password.', 'danger')
            return render_template('auth/change_password.html', csrf_token=csrf_token)
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        
        # Update password change timestamp if available
        if hasattr(current_user, 'password_last_changed'):
            current_user.password_last_changed = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        # Log password change
        log_security_event('password_changed', current_user.id, "Password changed successfully")
        
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('index'))

@secure_login_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request a password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = secrets.token_hex(16)
        session['csrf_token'] = csrf_token
        
        return render_template('auth/reset_password_request.html', csrf_token=csrf_token)
    
    elif request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('secure_login.reset_password_request'))
        
        email = request.form.get('email', '').lower().strip()
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('auth/reset_password_request.html', csrf_token=csrf_token)
        
        # Always show the same message whether the user exists or not
        # to prevent username enumeration
        flash('If your email address exists in our database, you will receive a password reset link at your email address in a few minutes.', 'info')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Log attempted reset for non-existent user
            log_security_event('password_reset_nonexistent_user', None, f"Password reset requested for nonexistent user: {email}")
            return redirect(url_for('secure_login.login'))
        
        # Check if account is locked
        locked, reason, unlock_time = is_account_locked(email)
        if locked:
            # Don't reveal that the account is locked, but log it
            log_security_event('password_reset_locked_account', user.id, f"Password reset requested for locked account: {email}")
            return redirect(url_for('secure_login.login'))
        
        # Generate reset token
        token = generate_secure_token()
        
        # Store token in user record with expiration
        user.reset_token = token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # Send reset email (would be actual email in production)
        reset_url = url_for('secure_login.reset_password', token=token, _external=True)
        logger.info(f"Password reset link for {email}: {reset_url}")
        
        # Log password reset request
        log_security_event('password_reset_requested', user.id, f"Password reset requested for: {email}")
        
        return redirect(url_for('secure_login.login'))

@secure_login_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Find user with this reset token
    user = User.query.filter_by(reset_token=token).first()
    
    # Check if token is valid and not expired
    if not user or not user.reset_token_expires_at or user.reset_token_expires_at < datetime.utcnow():
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('secure_login.reset_password_request'))
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = secrets.token_hex(16)
        session['csrf_token'] = csrf_token
        
        return render_template('auth/reset_password.html', csrf_token=csrf_token, token=token)
    
    elif request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('secure_login.reset_password', token=token))
        
        # Get form data
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/reset_password.html', csrf_token=csrf_token, token=token)
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', csrf_token=csrf_token, token=token)
        
        # Check password strength
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash(f'Password is not strong enough: {message}', 'danger')
            return render_template('auth/reset_password.html', csrf_token=csrf_token, token=token)
        
        # Check if password has been leaked
        if is_password_leaked(password):
            flash('This password has appeared in a data breach. Please choose a different password.', 'danger')
            return render_template('auth/reset_password.html', csrf_token=csrf_token, token=token)
        
        # Update password
        user.password_hash = generate_password_hash(password)
        
        # Update password change timestamp if available
        if hasattr(user, 'password_last_changed'):
            user.password_last_changed = datetime.utcnow()
        
        # Clear reset token
        user.reset_token = None
        user.reset_token_expires_at = None
        
        # Save changes
        db.session.commit()
        
        # Unlock account if locked
        unlock_account(user.email)
        
        # Log password reset
        log_security_event('password_reset_successful', user.id, f"Password reset successfully for: {user.email}")
        
        flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
        return redirect(url_for('secure_login.login'))

@secure_login_bp.route('/unlock-account-request', methods=['GET', 'POST'])
def unlock_account_request():
    """Request account unlock"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = secrets.token_hex(16)
        session['csrf_token'] = csrf_token
        
        return render_template('auth/unlock_account_request.html', csrf_token=csrf_token)
    
    elif request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('secure_login.unlock_account_request'))
        
        email = request.form.get('email', '').lower().strip()
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('auth/unlock_account_request.html', csrf_token=csrf_token)
        
        # Always show the same message to prevent username enumeration
        flash('If your account is locked, you will receive an unlock link at your email address.', 'info')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Log attempted unlock for non-existent user
            log_security_event('unlock_nonexistent_user', None, f"Account unlock requested for nonexistent user: {email}")
            return redirect(url_for('secure_login.login'))
        
        # Check if account is actually locked
        locked, reason, unlock_time = is_account_locked(email)
        if not locked:
            # Don't reveal that the account is not locked, but log it
            log_security_event('unlock_not_locked_account', user.id, f"Account unlock requested for non-locked account: {email}")
            return redirect(url_for('secure_login.login'))
        
        # In a full implementation, this would send an email with unlock link
        # For now, just unlock the account
        unlock_account(email)
        
        # Log account unlock
        log_security_event('account_unlocked', user.id, f"Account unlocked for: {email}")
        
        return redirect(url_for('secure_login.login'))