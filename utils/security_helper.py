"""
Security helper module for implementing security best practices
"""
import os
import secrets
import re
from functools import wraps
from flask import session, request, redirect, url_for, flash, abort
from flask_login import current_user
import logging
from datetime import datetime, timedelta

# Constants
MAX_FAILED_ATTEMPTS = 5  # Number of failed login attempts before lockout
LOCKOUT_DURATION = 15  # Lockout duration in minutes
SESSION_TIMEOUT = 60  # Session timeout in minutes
CSRF_TOKEN_TIMEOUT = 30  # CSRF token timeout in minutes
PASSWORD_MIN_LENGTH = 12

# Global dict to track failed login attempts
# In production, this should be in a database
failed_login_attempts = {}
account_lockouts = {}

def generate_csrf_token():
    """Generate a secure CSRF token"""
    if 'csrf_token' not in session or 'csrf_token_time' not in session:
        session['csrf_token'] = secrets.token_hex(32)
        session['csrf_token_time'] = datetime.utcnow().timestamp()
    elif datetime.utcnow().timestamp() - session['csrf_token_time'] > CSRF_TOKEN_TIMEOUT * 60:
        # Regenerate token if it's expired
        session['csrf_token'] = secrets.token_hex(32)
        session['csrf_token_time'] = datetime.utcnow().timestamp()
    return session['csrf_token']

def validate_csrf_token(token):
    """Validate a CSRF token against the one in the session"""
    if 'csrf_token' not in session:
        return False
    if 'csrf_token_time' not in session:
        return False
    if datetime.utcnow().timestamp() - session['csrf_token_time'] > CSRF_TOKEN_TIMEOUT * 60:
        return False
    return secrets.compare_digest(token, session['csrf_token'])

def csrf_protect(f):
    """Decorator to protect routes from CSRF attacks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            csrf_token = request.form.get('csrf_token')
            if not csrf_token or not validate_csrf_token(csrf_token):
                logging.warning(f"CSRF attack detected from IP: {get_client_ip()}")
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    """Get the client's IP address from the request"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

def record_failed_login(email):
    """Record a failed login attempt"""
    if email in failed_login_attempts:
        failed_login_attempts[email]['count'] += 1
        failed_login_attempts[email]['last_attempt'] = datetime.utcnow()
    else:
        failed_login_attempts[email] = {
            'count': 1,
            'last_attempt': datetime.utcnow()
        }
    
    # Check if account should be locked
    if failed_login_attempts[email]['count'] >= MAX_FAILED_ATTEMPTS:
        account_lockouts[email] = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION)
        logging.warning(f"Account locked: {email} - too many failed login attempts")

def reset_failed_login(email):
    """Reset failed login attempts for an email"""
    if email in failed_login_attempts:
        del failed_login_attempts[email]
    if email in account_lockouts:
        del account_lockouts[email]

def is_account_locked(email):
    """Check if an account is currently locked"""
    if email in account_lockouts:
        if datetime.utcnow() < account_lockouts[email]:
            time_left = account_lockouts[email] - datetime.utcnow()
            minutes_left = int(time_left.total_seconds() / 60) + 1
            return True, minutes_left
        else:
            # Lockout period expired
            del account_lockouts[email]
    return False, 0

def check_session_timeout():
    """Check if the user's session has timed out"""
    if 'last_activity' in session:
        last_activity = datetime.fromtimestamp(session['last_activity'])
        if datetime.utcnow() - last_activity > timedelta(minutes=SESSION_TIMEOUT):
            return True
    session['last_activity'] = datetime.utcnow().timestamp()
    return False

def session_timeout_check(f):
    """Decorator to check session timeout before processing a request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and check_session_timeout():
            from replit_auth import replit
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for('replit_auth.logout'))
        return f(*args, **kwargs)
    return decorated_function

def check_password_strength(password):
    """Check password strength against security requirements"""
    # Check length
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    # Check complexity (at least 3 of the 4 character types)
    checks = [
        any(c.islower() for c in password),  # Lowercase
        any(c.isupper() for c in password),  # Uppercase
        any(c.isdigit() for c in password),  # Digits
        bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))  # Special chars
    ]
    
    if sum(checks) < 3:
        return False, "Password must contain at least 3 of: lowercase, uppercase, digits, and special characters"
    
    # Check for common passwords or patterns (basic check)
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']
    for common in common_passwords:
        if common in password.lower():
            return False, "Password contains a common word or pattern"
    
    return True, "Password meets strength requirements"

def sanitize_input(input_str):
    """Basic input sanitization for displayed content"""
    if input_str is None:
        return ""
    # Replace potentially dangerous characters with entities
    return (input_str.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\"", "&quot;")
                    .replace("'", "&#x27;"))

def rate_limit(max_requests, time_window):
    """Decorator to rate limit API requests
    
    Args:
        max_requests: Maximum number of requests allowed in the time window
        time_window: Time window in seconds
    """
    request_history = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = get_client_ip()
            current_time = datetime.utcnow().timestamp()
            
            # Initialize or update request history
            if ip not in request_history:
                request_history[ip] = []
            
            # Clean up old requests
            request_history[ip] = [t for t in request_history[ip] if current_time - t < time_window]
            
            # Check if rate limit is exceeded
            if len(request_history[ip]) >= max_requests:
                logging.warning(f"Rate limit exceeded from IP: {ip}")
                return {"error": "Rate limit exceeded"}, 429
            
            # Add current request to history
            request_history[ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def encrypt_sensitive_data(data):
    """Placeholder for data encryption - in a real app, implement strong encryption"""
    # In production, implement proper encryption with a library like cryptography
    # This is just a placeholder to indicate where encryption should be used
    return f"encrypted_{data}"

def decrypt_sensitive_data(encrypted_data):
    """Placeholder for data decryption - in a real app, implement strong decryption"""
    # In production, implement proper decryption with a library like cryptography
    # This is just a placeholder to indicate where decryption should be used
    if encrypted_data and encrypted_data.startswith("encrypted_"):
        return encrypted_data[10:]  # Remove the "encrypted_" prefix
    return encrypted_data

def require_https(f):
    """Decorator to ensure a route is only accessible via HTTPS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Forwarded-Proto') != 'https' and not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details, severity="INFO"):
    """Log security-related events"""
    ip = get_client_ip()
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    
    logging.log(
        getattr(logging, severity, logging.INFO),
        f"SECURITY EVENT - {event_type}: User={user_id}, IP={ip}, Details={details}"
    )