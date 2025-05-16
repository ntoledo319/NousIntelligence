"""
Security helper module for implementing security best practices

This module provides security functions for authentication, authorization,
input validation, and protection against common web vulnerabilities.

@module: security_helper
@author: NOUS Development Team
"""
import os
import secrets
import re
import hashlib
import hmac
from functools import wraps
from flask import session, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user
import logging
from datetime import datetime, timedelta

# Try to import monitoring middleware (if available)
try:
    from utils.monitoring_middleware import log_rate_limit_hit
    has_monitoring = True
except ImportError:
    has_monitoring = False

# Constants - load from environment with reasonable defaults
MAX_FAILED_ATTEMPTS = int(os.environ.get('MAX_FAILED_LOGINS', '5'))
LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION_MINUTES', '15'))
SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT_MINUTES', '60'))
CSRF_TOKEN_TIMEOUT = int(os.environ.get('CSRF_TOKEN_TIMEOUT_MINUTES', '30'))
PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '12'))
ENFORCE_HTTPS = os.environ.get('ENFORCE_HTTPS', 'true').lower() == 'true'

# Global dict to track failed login attempts
# In production, this should be in a database
failed_login_attempts = {}
account_lockouts = {}

# Rate limiting data
rate_limits = {}
rate_limit_locks = {}

def generate_csrf_token():
    """
    Generate a secure CSRF token using a cryptographically secure random generator
    
    Returns:
        str: A secure random hex token
    """
    # Generate a unique token with timestamp
    token = secrets.token_hex(32)
    session['csrf_token'] = token
    session['csrf_token_time'] = datetime.utcnow().timestamp()
    return token

def validate_csrf_token(token):
    """
    Validate a CSRF token against the one in the session using constant-time comparison
    
    Args:
        token (str): The token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token or 'csrf_token' not in session:
        return False
    
    # Check token expiration
    if 'csrf_token_time' not in session:
        return False
        
    token_age = datetime.utcnow().timestamp() - session['csrf_token_time']
    if token_age > CSRF_TOKEN_TIMEOUT * 60:
        # Token expired
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(token, session['csrf_token'])

def csrf_protect(f):
    """
    Decorator to protect routes from CSRF attacks
    
    This decorator checks for a valid CSRF token on all POST, PUT, DELETE requests.
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Check for token in form, headers or JSON data
            token = None
            if request.form:
                token = request.form.get('csrf_token')
            elif request.is_json:
                token = request.json.get('csrf_token')
            if not token:
                token = request.headers.get('X-CSRF-Token')
                
            if not token or not validate_csrf_token(token):
                ip = get_client_ip()
                logging.warning(f"CSRF attack detected from IP: {ip}")
                log_security_event("csrf_failure", f"Invalid CSRF token from {ip}", "WARNING")
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    """
    Get the client's IP address from the request, handling proxies
    
    Returns:
        str: The client's IP address
    """
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    return request.remote_addr

def record_failed_login(email):
    """
    Record a failed login attempt and check if account should be locked
    
    Args:
        email (str): The email address that failed login
    """
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
        log_security_event("account_lockout", f"Account {email} locked after {MAX_FAILED_ATTEMPTS} failed attempts", "WARNING")

def reset_failed_login(email):
    """
    Reset failed login attempts for an email
    
    Args:
        email (str): The email address to reset
    """
    if email in failed_login_attempts:
        del failed_login_attempts[email]
    if email in account_lockouts:
        del account_lockouts[email]

def is_account_locked(email):
    """
    Check if an account is currently locked
    
    Args:
        email (str): The email address to check
        
    Returns:
        tuple: (is_locked, minutes_left)
    """
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
    """
    Check if the user's session has timed out
    
    Returns:
        bool: True if session has timed out, False otherwise
    """
    if 'last_activity' not in session:
        session['last_activity'] = datetime.utcnow().timestamp()
        return False
        
    last_activity = datetime.fromtimestamp(session['last_activity'])
    if datetime.utcnow() - last_activity > timedelta(minutes=SESSION_TIMEOUT):
        return True
        
    # Update last activity timestamp
    session['last_activity'] = datetime.utcnow().timestamp()
    return False

def session_timeout_check(f):
    """
    Decorator to check session timeout before processing a request
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and check_session_timeout():
            # Log this event
            log_security_event("session_timeout", f"Session timeout for user {current_user.id}", "INFO")
            
            # Clear the session
            from flask_login import logout_user
            logout_user()
            session.clear()
            
            # Notify the user
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for('google_auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def check_password_strength(password):
    """
    Check password strength against security requirements
    
    Args:
        password (str): The password to check
        
    Returns:
        tuple: (is_strong, message)
    """
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
    
    # Check for common passwords or patterns
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome', 'letmein', 'monkey']
    for common in common_passwords:
        if common in password.lower():
            return False, "Password contains a common word or pattern"
    
    return True, "Password meets strength requirements"

def sanitize_input(input_str):
    """
    Basic input sanitization for displayed content
    
    Args:
        input_str: The string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if input_str is None:
        return ""
        
    # Convert to string if not already
    if not isinstance(input_str, str):
        input_str = str(input_str)
        
    # Replace potentially dangerous characters with entities
    return (input_str.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\"", "&quot;")
                    .replace("'", "&#x27;")
                    .replace("/", "&#x2F;"))

def rate_limit(max_requests, time_window):
    """
    Decorator to add rate limiting to a function
    
    Args:
        max_requests: Maximum number of requests allowed in the time window
        time_window: Time window in seconds
    
    Returns:
        Decorated function with rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the endpoint name and client IP
            endpoint = request.endpoint or f.__name__
            ip = get_client_ip()
            key = f"{ip}:{endpoint}"
            
            # Get current time
            now = datetime.utcnow()
            
            # Get all timestamps for this client and endpoint
            timestamps = rate_limits.get(key, [])
            
            # Remove old timestamps
            timestamps = [ts for ts in timestamps if (now - ts).total_seconds() < time_window]
            
            # Check if rate limit exceeded
            if len(timestamps) >= max_requests:
                # Log rate limit hit if monitoring is available
                if has_monitoring and current_app:
                    log_rate_limit_hit(current_app, endpoint)
                
                log_security_event("rate_limit", f"Rate limit exceeded for {endpoint} from {ip}", "WARNING")
                response = {"error": "Rate limit exceeded", "retry_after": time_window}
                return response, 429
            
            # Add current timestamp and update rate limits
            timestamps.append(now)
            rate_limits[key] = timestamps
            
            # Call the original function
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def secure_hash(data, salt=None):
    """
    Create a secure hash of data
    
    Args:
        data (str): The data to hash
        salt (str, optional): Salt to use. If None, a random salt is generated
        
    Returns:
        tuple: (hash_hex, salt_hex)
    """
    if salt is None:
        salt = os.urandom(32)  # 32 bytes = 256 bits
    elif isinstance(salt, str):
        salt = bytes.fromhex(salt)
        
    if isinstance(data, str):
        data = data.encode('utf-8')
        
    # Use PBKDF2 with HMAC-SHA256
    key = hashlib.pbkdf2_hmac(
        'sha256',
        data,
        salt,
        100000,  # 100,000 iterations
        dklen=32
    )
    
    return key.hex(), salt.hex()

def require_https(f):
    """
    Decorator to require HTTPS for a route
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ENFORCE_HTTPS and not request.is_secure and not request.headers.get('X-Forwarded-Proto', 'http') == 'https':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details, severity="INFO"):
    """
    Log security-related events
    
    Args:
        event_type (str): Type of security event
        details (str): Details about the event
        severity (str): Event severity (INFO, WARNING, ERROR, CRITICAL)
    """
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    ip = get_client_ip()
    timestamp = datetime.utcnow().isoformat()
    
    event = {
        "timestamp": timestamp,
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip,
        "details": details,
        "severity": severity
    }
    
    if severity == "INFO":
        logging.info(f"SECURITY: {event_type} - {details}")
    elif severity == "WARNING":
        logging.warning(f"SECURITY: {event_type} - {details}")
    elif severity == "ERROR":
        logging.error(f"SECURITY: {event_type} - {details}")
    elif severity == "CRITICAL":
        logging.critical(f"SECURITY: {event_type} - {details}")
    
    # In production, you might want to store these events in a database

def admin_required(f):
    """
    Decorator to require admin privileges for a route
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            log_security_event(
                "unauthorized_access", 
                f"Non-admin user attempted to access admin route: {request.path}",
                "WARNING"
            )
            flash("You do not have permission to access this resource.", "error")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function