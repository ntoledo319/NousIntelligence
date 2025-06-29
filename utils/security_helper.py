"""
Security Helper Utilities
Provides rate limiting, account lockout, and input sanitization for authentication
"""

import logging
import time
import re
from functools import wraps
from flask import request, jsonify, session
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory storage for rate limiting and lockouts
# In production, use Redis or database
_rate_limit_data = {}
_failed_login_attempts = {}
_account_lockouts = {}

class SecurityConfig:
    """Security configuration settings"""
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    RATE_LIMIT_REQUESTS = 10
    RATE_LIMIT_WINDOW_MINUTES = 1

def rate_limit(max_requests: int = None, window_minutes: int = None):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed in window
        window_minutes: Time window in minutes
    """
    max_req = max_requests or SecurityConfig.RATE_LIMIT_REQUESTS
    window = window_minutes or SecurityConfig.RATE_LIMIT_WINDOW_MINUTES
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_id = get_client_identifier()
            now = time.time()
            window_start = now - (window * 60)
            
            # Clean old entries
            if client_id in _rate_limit_data:
                _rate_limit_data[client_id] = [
                    timestamp for timestamp in _rate_limit_data[client_id]
                    if timestamp > window_start
                ]
            else:
                _rate_limit_data[client_id] = []
            
            # Check rate limit
            if len(_rate_limit_data[client_id]) >= max_req:
                logger.warning(f"Rate limit exceeded for {client_id}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window * 60
                }), 429
            
            # Record this request
            _rate_limit_data[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def record_failed_login(identifier: str):
    """
    Record a failed login attempt
    
    Args:
        identifier: User email or IP address
    """
    now = datetime.now()
    
    if identifier not in _failed_login_attempts:
        _failed_login_attempts[identifier] = []
    
    # Clean old attempts (older than lockout duration)
    cutoff_time = now - timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
    _failed_login_attempts[identifier] = [
        attempt for attempt in _failed_login_attempts[identifier]
        if attempt > cutoff_time
    ]
    
    # Record this attempt
    _failed_login_attempts[identifier].append(now)
    
    # Check if account should be locked
    if len(_failed_login_attempts[identifier]) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
        _account_lockouts[identifier] = now + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
        logger.warning(f"Account locked for {identifier} due to too many failed attempts")

def reset_failed_login(identifier: str):
    """
    Reset failed login attempts for identifier
    
    Args:
        identifier: User email or IP address
    """
    if identifier in _failed_login_attempts:
        del _failed_login_attempts[identifier]
    
    if identifier in _account_lockouts:
        del _account_lockouts[identifier]
    
    logger.info(f"Reset failed login attempts for {identifier}")

def is_account_locked(identifier: str) -> bool:
    """
    Check if account is currently locked
    
    Args:
        identifier: User email or IP address
        
    Returns:
        True if account is locked
    """
    if identifier not in _account_lockouts:
        return False
    
    lockout_until = _account_lockouts[identifier]
    now = datetime.now()
    
    if now < lockout_until:
        return True
    else:
        # Lockout expired, clean up
        del _account_lockouts[identifier]
        if identifier in _failed_login_attempts:
            del _failed_login_attempts[identifier]
        return False

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Raw input string
        
    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        return str(input_str)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\'\&\$\;]', '', input_str)
    
    # Limit length
    sanitized = sanitized[:1000]
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    issues = []
    score = 0
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    else:
        score += 1
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    else:
        score += 1
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    else:
        score += 1
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one number")
    else:
        score += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    else:
        score += 1
    
    return {
        'valid': len(issues) == 0,
        'score': score,
        'max_score': 5,
        'issues': issues
    }

def get_client_identifier() -> str:
    """
    Get unique identifier for client (for rate limiting)
    
    Returns:
        Client identifier string
    """
    # Try to get user ID from session
    if 'user' in session and session['user']:
        return f"user_{get_current_user().get('id', 'unknown')}"
    
    # Fall back to IP address
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        # Take first IP if multiple (proxy chain)
        ip = ip.split(',')[0].strip()
    
    return f"ip_{ip or 'unknown'}"

def log_security_event(event_type: str, details: Dict[str, Any]):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    logger.info(f"Security event: {event_type}", extra={
        'event_type': event_type,
        'client_id': get_client_identifier(),
        'timestamp': datetime.now().isoformat(),
        'details': details
    })

def check_suspicious_activity(user_data: Dict[str, Any]) -> bool:
    """
    Check for suspicious login activity
    
    Args:
        user_data: User information
        
    Returns:
        True if activity seems suspicious
    """
    # Simple heuristics for suspicious activity
    client_id = get_client_identifier()
    
    # Check if multiple failed attempts recently
    if client_id in _failed_login_attempts:
        recent_attempts = len(_failed_login_attempts[client_id])
        if recent_attempts >= 3:
            log_security_event("suspicious_login_pattern", {
                "failed_attempts": recent_attempts,
                "user": user_data.get('email', 'unknown')
            })
            return True
    
    return False

def generate_csrf_token() -> str:
    """
    Generate CSRF token for forms
    
    Returns:
        CSRF token string
    """
    import secrets
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token

def validate_csrf_token(token: str) -> bool:
    """
    Validate CSRF token
    
    Args:
        token: CSRF token to validate
        
    Returns:
        True if valid
    """
    session_token = session.get('csrf_token')
    return session_token and session_token == token