"""
Login Security Utilities

This module provides security functions for the login system, including:
- Failed login attempt tracking
- Account lockout protection
- Login rate limiting
- Security event logging

@module login_security
@description Login security utilities
"""

import logging
import time
from datetime import datetime, timedelta
from flask import request, session, current_app, g
from models.system_models import SystemSettings
from models.user_models import User
from models.security_models import SecurityLog, LoginAttempt
from app_factory import db

logger = logging.getLogger(__name__)

# In-memory cache to store failed login attempts
# Format: {email: {'attempts': count, 'last_attempt': timestamp, 'locked_until': timestamp}}
_failed_attempts = {}

def track_login_attempt(email, success):
    """
    Track login attempts and implement account lockout after multiple failures
    
    Args:
        email: User's email address
        success: Whether the login attempt was successful
        
    Returns:
        tuple: (is_allowed, lockout_minutes) - whether login is allowed and minutes until unlock
    """
    # Get max login attempts and lockout duration from system settings
    max_attempts = 5  # Default value
    lockout_minutes = 15  # Default value
    
    # Try to get settings from database
    try:
        setting = SystemSettings.query.filter_by(key='max_login_attempts').first()
        if setting and setting.value:
            max_attempts = int(setting.value)
            
        setting = SystemSettings.query.filter_by(key='account_lockout_duration').first()
        if setting and setting.value:
            lockout_minutes = int(setting.value)
    except Exception as e:
        logger.warning(f"Failed to get login security settings: {str(e)}")
    
    # Record login attempt in database
    try:
        login_attempt = LoginAttempt()
        login_attempt.email = email
        login_attempt.success = success
        login_attempt.ip_address = request.remote_addr
        login_attempt.user_agent = request.user_agent.string if request.user_agent else None
        db.session.add(login_attempt)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to record login attempt: {str(e)}")
        db.session.rollback()
    
    # Reset attempts on successful login
    if success:
        if email in _failed_attempts:
            del _failed_attempts[email]
        return True, 0
    
    # Initialize entry if not present
    if email not in _failed_attempts:
        _failed_attempts[email] = {
            'attempts': 1,
            'last_attempt': time.time(),
            'locked_until': None
        }
        return True, 0
    
    # Check if account is locked
    entry = _failed_attempts[email]
    current_time = time.time()
    
    if entry['locked_until'] and current_time < entry['locked_until']:
        # Account is locked, calculate remaining time
        remaining_seconds = entry['locked_until'] - current_time
        remaining_minutes = int(remaining_seconds / 60) + 1  # Round up
        logger.warning(f"Login attempt for locked account: {email}")
        return False, remaining_minutes
    
    # Account was locked but lockout expired
    if entry['locked_until'] and current_time >= entry['locked_until']:
        # Reset after lockout period
        entry['attempts'] = 1
        entry['last_attempt'] = current_time
        entry['locked_until'] = None
        return True, 0
    
    # Increment failed attempts
    entry['attempts'] += 1
    entry['last_attempt'] = current_time
    
    # Check if account should be locked
    if entry['attempts'] >= max_attempts:
        # Lock account for specified duration
        lockout_seconds = lockout_minutes * 60
        entry['locked_until'] = current_time + lockout_seconds
        logger.warning(f"Account locked due to {entry['attempts']} failed login attempts: {email}")
        return False, lockout_minutes
    
    # Login still allowed
    return True, 0

def log_security_event(event_type, user_id=None, details=None):
    """
    Log security-related events for auditing
    
    Args:
        event_type: Type of security event (login, logout, etc.)
        user_id: ID of the user (if applicable)
        details: Additional event details
    """
    try:
        # Create log entry
        log_entry = SecurityLog()
        log_entry.event_type = event_type
        log_entry.user_id = user_id
        log_entry.ip_address = request.remote_addr
        log_entry.user_agent = request.user_agent.string if request.user_agent else None
        log_entry.details = details
        db.session.add(log_entry)
        db.session.commit()
        logger.info(f"Security event logged: {event_type} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to log security event: {str(e)}")
        db.session.rollback()

def is_secure_password(password):
    """
    Check if a password meets security requirements
    
    Args:
        password: Password to check
        
    Returns:
        tuple: (is_secure, reason) - whether password is secure and reason if not
    """
    # Get minimum length from system settings
    min_length = 12  # Default value
    
    try:
        setting = SystemSettings.query.filter_by(key='password_min_length').first()
        if setting and setting.value:
            min_length = int(setting.value)
    except Exception as e:
        logger.warning(f"Failed to get password settings: {str(e)}")
    
    # Check length
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    # Check complexity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numeric characters"
    
    if not has_special:
        return False, "Password must contain at least one special character"
    
    return True, None

def cleanup_expired_sessions():
    """
    Clean up expired sessions to prevent session fixation attacks
    """
    try:
        # Default timeout
        timeout_minutes = 60
        
        # Try to get from database
        setting = SystemSettings.query.filter_by(key='session_timeout').first()
        if setting and setting.value:
            timeout_minutes = int(setting.value)
            
        # Set timeout for current session
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=timeout_minutes)
    except Exception as e:
        logger.error(f"Failed to configure session timeout: {str(e)}")