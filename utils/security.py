"""
Security Utilities Module

This module provides utility functions for security features.

@module utils.security
@description Security utility functions
"""

import logging
import json
import secrets
import re
import time
from datetime import datetime, timedelta
from flask import session, request, current_app
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import ipaddress

# Configure logging
logger = logging.getLogger(__name__)

def generate_csrf_token():
    """
    Generate a new CSRF token and store it in the session

    Returns:
        str: The generated CSRF token
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """
    Validate a CSRF token against the one stored in the session

    Args:
        token: CSRF token to validate

    Returns:
        bool: True if token is valid, False otherwise
    """
    return token and 'csrf_token' in session and session['csrf_token'] == token

def require_csrf_token(f):
    """
    Decorator to require a valid CSRF token for a view function

    Args:
        f: View function to decorate

    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token')
            if not token or not validate_csrf_token(token):
                from flask import flash, redirect, url_for
                flash('Invalid CSRF token. Please try again.', 'danger')
                return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, user_id=None, description=None, ip_address=None,
                     resource_type=None, resource_id=None, metadata=None, severity='INFO'):
    """
    Log a security event to the database

    Args:
        event_type: Type of security event
        user_id: User ID (optional)
        description: Description of the event (optional)
        ip_address: IP address where the event originated (optional)
        resource_type: Type of resource affected (optional)
        resource_id: ID of resource affected (optional)
        metadata: Additional metadata as a string or dict (optional)
        severity: Severity level of the event (default: 'INFO')

    Returns:
        SecurityAuditLog: The created log entry
    """
    try:
        from models.security_models import SecurityAuditLog
        from models import db

        # Format metadata to JSON string if it's a dict
        meta_str = None
        if metadata:
            if isinstance(metadata, dict):
                meta_str = json.dumps(metadata)
            else:
                meta_str = str(metadata)

        # Get IP address from request if not provided
        if not ip_address and request:
            ip_address = request.remote_addr

        # Create log entry
        log = SecurityAuditLog(
            user_id=user_id,
            ip_address=ip_address,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            meta_data=meta_str,
            severity=severity
        )

        db.session.add(log)
        db.session.commit()

        # Also log to application logs for high severity events
        if severity in ['ERROR', 'CRITICAL', 'WARNING']:
            logger.warning(f"Security event: {event_type} - {description}")

        return log
    except Exception as e:
        logger.error(f"Error logging security event: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return None

def is_password_strong(password):
    """
    Check if a password meets strong password requirements

    Args:
        password: Password to check

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."

    checks = [
        (re.search(r'[A-Z]', password), "Password must contain at least one uppercase letter."),
        (re.search(r'[a-z]', password), "Password must contain at least one lowercase letter."),
        (re.search(r'[0-9]', password), "Password must contain at least one number."),
        (re.search(r'[^A-Za-z0-9]', password), "Password must contain at least one special character.")
    ]

    for check, message in checks:
        if not check:
            return False, message

    # Check for common passwords
    common_passwords = [
        "password", "123456", "qwerty", "admin", "welcome",
        "letmein", "monkey", "1234", "12345", "football",
        "iloveyou", "1234567", "123123", "abc123", "111111",
        "123456789", "trustno1", "princess", "sunshine", "nicole",
        "daniel", "babygirl", "monkey", "lovely", "jessica",
        "654321", "michael", "ashley", "password1", "lovely",
        "000000", "michelle", "tigger", "chocolate", "charlie",
        "Password1", "Welcome1"
    ]

    if any(pwd in password.lower() for pwd in common_passwords):
        return False, "Password is too common. Please choose a stronger password."

    # Check for repeated characters
    if re.search(r'(.)\1{3,}', password):
        return False, "Password should not contain sequences of repeated characters."

    # Check for sequential characters
    sequences = ['abcdefghijklmnopqrstuvwxyz', '0123456789']
    for seq in sequences:
        for i in range(len(seq) - 3):
            if seq[i:i+4].lower() in password.lower():
                return False, "Password should not contain sequential characters."

    return True, ""

def hash_password(password):
    """
    Generate a secure password hash

    Args:
        password: Password to hash

    Returns:
        str: Password hash
    """
    return generate_password_hash(password)

def check_password(password_hash, password):
    """
    Check if a password matches a hash

    Args:
        password_hash: Stored password hash
        password: Password to check

    Returns:
        bool: True if password matches hash
    """
    return check_password_hash(password_hash, password)

def is_ip_in_allowed_range(ip_address, allowed_ranges=None):
    """
    Check if an IP address is in an allowed range

    Args:
        ip_address: IP address to check
        allowed_ranges: List of allowed ranges (optional)

    Returns:
        bool: True if IP is in allowed range
    """
    if not allowed_ranges:
        # Default to allow all if no ranges specified
        return True

    try:
        ip = ipaddress.ip_address(ip_address)

        for range_str in allowed_ranges:
            ip_range = ipaddress.ip_network(range_str, strict=False)
            if ip in ip_range:
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking IP range: {str(e)}")
        return False

def rate_limit_exceeded(key, limit, period):
    """
    Check if a rate limit has been exceeded

    Args:
        key: Rate limit key (e.g., user ID or IP address)
        limit: Maximum number of requests allowed
        period: Time period in seconds

    Returns:
        bool: True if rate limit exceeded
    """
    from flask import g
    from redis import Redis
    import os

    # Get Redis connection
    redis_url = current_app.config.get('RATELIMIT_STORAGE_URL')

    if redis_url and redis_url.startswith('redis://'):
        # Use Redis for rate limiting if available
        if not hasattr(g, '_rate_limit_redis'):
            g._rate_limit_redis = Redis.from_url(redis_url)

        # Create a unique key for this rate limit
        redis_key = f"rate_limit:{key}:{period}"

        # Get the current count
        count = g._rate_limit_redis.get(redis_key)

        if count is None:
            # Key doesn't exist, set it to 1
            g._rate_limit_redis.setex(redis_key, period, 1)
            return False

        count = int(count)

        if count >= limit:
            return True

        # Increment the counter
        g._rate_limit_redis.incr(redis_key)
        return False
    else:
        # Fall back to in-memory rate limiting

        if not hasattr(g, '_rate_limit_store'):
            g._rate_limit_store = {}

        # Create a unique key for this rate limit
        memory_key = f"rate_limit:{key}:{period}"

        now = time.time()

        if memory_key in g._rate_limit_store:
            entry = g._rate_limit_store[memory_key]

            # Clear expired entries
            if now - entry['start'] > period:
                entry['count'] = 1
                entry['start'] = now
                return False

            # Check if limit exceeded
            if entry['count'] >= limit:
                return True

            # Increment the counter
            entry['count'] += 1
            return False
        else:
            # Create a new entry
            g._rate_limit_store[memory_key] = {
                'count': 1,
                'start': now
            }
            return False

def get_client_info():
    """
    Get information about the client making the request

    Returns:
        dict: Dictionary with client information
    """
    client_info = {
        'ip_address': request.remote_addr,
        'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
        'browser': request.user_agent.browser if request.user_agent else 'Unknown',
        'platform': request.user_agent.platform if request.user_agent else 'Unknown',
        'referrer': request.referrer or 'Direct',
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add Cloudflare headers if available
    if request.headers.get('CF-Connecting-IP'):
        client_info['cf_ip'] = request.headers.get('CF-Connecting-IP')
        client_info['cf_country'] = request.headers.get('CF-IPCountry')
        client_info['cf_ray'] = request.headers.get('CF-RAY')

    return client_info

def sanitize_input(input_str, allowed_tags=None):
    """
    Sanitize user input to prevent XSS attacks

    Args:
        input_str: Input string to sanitize
        allowed_tags: List of allowed HTML tags (optional)

    Returns:
        str: Sanitized string
    """
    import bleach

    if not input_str:
        return ""

    # If no allowed tags specified, strip all HTML
    if allowed_tags is None:
        return bleach.clean(input_str, strip=True)

    # Use bleach to sanitize with allowed tags
    return bleach.clean(
        input_str,
        tags=allowed_tags,
        attributes={tag: ['class', 'style'] for tag in allowed_tags},
        strip=True
    )