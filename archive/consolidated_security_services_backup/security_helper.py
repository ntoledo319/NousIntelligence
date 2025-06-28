"""
Security Helper

This module provides security-related functions including:
- CSRF protection
- Admin authorization
- Access controls
- Security event logging
- Input sanitization

@module security_helper
@description Security-related helper functions
"""

import logging
import re
import html
import bleach
from functools import wraps
from datetime import datetime
from flask import request, session, abort, redirect, url_for, flash, current_app
from flask_login import current_user
import uuid

from models import User, SecurityEvent, db

# Configure logging
logger = logging.getLogger(__name__)

def csrf_protect(f):
    """Decorator to protect routes from CSRF attacks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check CSRF token (from form or header)
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        session_token = session.get('csrf_token')

        if not token or not session_token or token != session_token:
            # Log the CSRF attempt
            log_security_event("CSRF_ATTEMPT", "CSRF token validation failed", severity="WARNING")

            if request.content_type == 'application/json':
                # Return JSON error for API
                return {"error": "CSRF validation failed"}, 403
            else:
                # Flash error and redirect for web
                flash("Security validation failed. Please try again.", "danger")
                return redirect(url_for('index.index'))

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))

        if not current_user.is_admin:
            log_security_event("UNAUTHORIZED_ACCESS",
                              f"Non-admin user attempted to access admin route: {request.path}",
                              severity="WARNING")
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for('index.index'))

        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text

    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)

    # Use bleach to sanitize HTML
    allowed_tags = []  # No HTML tags allowed
    allowed_attrs = {}
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)

def log_security_event(event_type, details, user_id=None, severity="INFO"):
    """Log a security event to the database

    Args:
        event_type: Type of security event
        details: Description of the event
        user_id: ID of the user involved (optional)
        severity: Severity level (INFO, WARNING, ERROR)
    """
    try:
        # Get current user if not provided
        if user_id is None and current_user.is_authenticated:
            user_id = current_user.id

        # Get IP address
        ip_address = request.remote_addr

        # Create event record
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            severity=severity
        )

        # Add to database
        db.session.add(event)
        db.session.commit()

        # Also log to application logs
        log_message = f"Security event: {event_type} - {details}"
        if severity == "WARNING":
            logger.warning(log_message)
        elif severity == "ERROR":
            logger.error(log_message)
        else:
            logger.info(log_message)

    except Exception as e:
        # Log to application logs if database logging fails
        logger.error(f"Failed to log security event: {str(e)}")

def set_admin_status(email, status):
    """Set administrator status for a user

    Args:
        email: Email of the user
        status: Boolean indicating admin status

    Returns:
        Boolean indicating success
    """
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = status
            db.session.commit()
            log_security_event(
                "ADMIN_STATUS_CHANGE",
                f"Admin status for {email} set to {status}",
                user_id=user.id,
                severity="WARNING"
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Error setting admin status: {str(e)}")
        return False

def generate_csrf_token():
    """Generate a new CSRF token and store in session

    Returns:
        String CSRF token
    """
    token = str(uuid.uuid4())
    session['csrf_token'] = token
    return token