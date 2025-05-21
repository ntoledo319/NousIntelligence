"""
Login Security Module

This module provides enhanced security features for login functionality.
It includes brute force protection, account lockout, and IP-based security controls.

@module utils.login_security
@description Enhanced login security utilities
"""

import logging
import time
import json
import re
import secrets
from datetime import datetime, timedelta
from flask import session, request, current_app, g
from functools import wraps
import ipaddress
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logger = logging.getLogger(__name__)

# In-memory storage for rate limiting and lockouts
# In production this would use Redis or a database
_rate_limit_store = {}
_lockout_store = {}
_suspicious_ips = {}

def track_login_attempt(user_id, email, success, ip_address=None, user_agent=None):
    """
    Track login attempt for security monitoring and brute force protection
    
    Args:
        user_id: User ID (can be None for failed attempts with non-existent users)
        email: Email used in the login attempt
        success: Whether the login was successful
        ip_address: IP address of the request (optional)
        user_agent: User agent of the request (optional)
        
    Returns:
        bool: True if account is now locked, False otherwise
    """
    # Get client information
    ip = ip_address or request.remote_addr
    ua = user_agent or (request.user_agent.string if request.user_agent else "Unknown")
    
    # Create entry in memory store
    timestamp = datetime.utcnow()
    
    # Track by user email
    if email:
        if email not in _rate_limit_store:
            _rate_limit_store[email] = {
                'attempts': [],
                'last_success': None,
                'failed_count': 0
            }
        
        # Add attempt
        _rate_limit_store[email]['attempts'].append({
            'timestamp': timestamp,
            'ip': ip,
            'user_agent': ua,
            'success': success
        })
        
        # Update counters
        if success:
            _rate_limit_store[email]['last_success'] = timestamp
            _rate_limit_store[email]['failed_count'] = 0
        else:
            _rate_limit_store[email]['failed_count'] += 1
    
    # Track by IP address
    if ip:
        if ip not in _rate_limit_store:
            _rate_limit_store[ip] = {
                'attempts': [],
                'unique_accounts': set(),
                'failed_count': 0
            }
        
        # Add attempt
        _rate_limit_store[ip]['attempts'].append({
            'timestamp': timestamp,
            'email': email,
            'success': success
        })
        
        # Update counters
        if email:
            _rate_limit_store[ip]['unique_accounts'].add(email)
        
        if not success:
            _rate_limit_store[ip]['failed_count'] += 1
    
    # Check for account lockout conditions
    if email and _rate_limit_store[email]['failed_count'] >= 5:
        lock_account(email, ip, 'Too many failed login attempts')
        return True
    
    # Check for IP-based throttling
    if ip and _rate_limit_store[ip]['failed_count'] >= 10:
        throttle_ip(ip, reason='High rate of failed login attempts')
    
    # Check for suspicious behavior (multiple accounts from same IP)
    if ip and len(_rate_limit_store[ip]['unique_accounts']) > 5:
        flag_suspicious_ip(ip, 'Multiple account access attempts')
    
    return False

def lock_account(email, ip_address=None, reason='Security policy'):
    """
    Lock an account for security reasons
    
    Args:
        email: Email of the account to lock
        ip_address: IP address that triggered the lockout (optional)
        reason: Reason for the lockout (optional)
        
    Returns:
        tuple: (bool, str) - (success, message)
    """
    # Log the event
    logger.warning(f"Account locked: {email} from IP {ip_address} - Reason: {reason}")
    
    # Set lockout in memory store
    _lockout_store[email] = {
        'locked_at': datetime.utcnow(),
        'reason': reason,
        'ip': ip_address,
        'unlock_at': datetime.utcnow() + timedelta(hours=1),
        'unlock_code': secrets.token_urlsafe(16)
    }
    
    # In a real implementation, this would update a user record in the database
    return True, "Account locked for security reasons"

def is_account_locked(email):
    """
    Check if an account is currently locked
    
    Args:
        email: Email of the account to check
        
    Returns:
        tuple: (bool, dict) - (is_locked, lockout_info)
    """
    if email not in _lockout_store:
        return False, None
    
    lockout = _lockout_store[email]
    
    # Check if lockout has expired
    if lockout['unlock_at'] <= datetime.utcnow():
        # Auto-unlock expired lockouts
        del _lockout_store[email]
        return False, None
    
    return True, lockout

def unlock_account(email, unlock_code=None):
    """
    Unlock a locked account
    
    Args:
        email: Email of the account to unlock
        unlock_code: Unlock code (required for self-service unlock)
        
    Returns:
        tuple: (bool, str) - (success, message)
    """
    if email not in _lockout_store:
        return False, "Account is not locked"
    
    # If unlock code provided, verify it
    if unlock_code:
        if unlock_code != _lockout_store[email]['unlock_code']:
            logger.warning(f"Failed unlock attempt with invalid code for {email}")
            return False, "Invalid unlock code"
    
    # Unlock the account
    del _lockout_store[email]
    
    # Clear failed attempts
    if email in _rate_limit_store:
        _rate_limit_store[email]['failed_count'] = 0
    
    logger.info(f"Account unlocked: {email}")
    return True, "Account unlocked successfully"

def throttle_ip(ip_address, duration_minutes=15, reason=None):
    """
    Throttle requests from an IP address
    
    Args:
        ip_address: IP address to throttle
        duration_minutes: Duration of throttling in minutes (optional)
        reason: Reason for throttling (optional)
        
    Returns:
        bool: True if throttling was applied
    """
    if not ip_address:
        return False
    
    _suspicious_ips[ip_address] = {
        'flagged_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(minutes=duration_minutes),
        'reason': reason or 'Security policy',
        'throttle_level': 'medium'
    }
    
    logger.warning(f"IP throttled: {ip_address} - Reason: {reason or 'Security policy'}")
    return True

def flag_suspicious_ip(ip_address, reason=None):
    """
    Flag an IP address as suspicious
    
    Args:
        ip_address: IP address to flag
        reason: Reason for flagging (optional)
        
    Returns:
        bool: True if IP was flagged
    """
    if not ip_address:
        return False
    
    _suspicious_ips[ip_address] = {
        'flagged_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=24),
        'reason': reason or 'Suspicious activity',
        'throttle_level': 'low'
    }
    
    logger.warning(f"IP flagged as suspicious: {ip_address} - Reason: {reason or 'Suspicious activity'}")
    return True

def block_ip(ip_address, duration_hours=24, reason=None):
    """
    Block an IP address completely
    
    Args:
        ip_address: IP address to block
        duration_hours: Duration of block in hours (optional)
        reason: Reason for blocking (optional)
        
    Returns:
        bool: True if IP was blocked
    """
    if not ip_address:
        return False
    
    _suspicious_ips[ip_address] = {
        'flagged_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=duration_hours),
        'reason': reason or 'Security threat',
        'throttle_level': 'high'
    }
    
    logger.warning(f"IP blocked: {ip_address} - Reason: {reason or 'Security threat'}")
    return True

def is_ip_restricted(ip_address):
    """
    Check if an IP address is restricted
    
    Args:
        ip_address: IP address to check
        
    Returns:
        tuple: (bool, str, str) - (is_restricted, level, reason)
    """
    if not ip_address or ip_address not in _suspicious_ips:
        return False, None, None
    
    data = _suspicious_ips[ip_address]
    
    # Check if restriction has expired
    if data['expires_at'] <= datetime.utcnow():
        # Auto-remove expired restrictions
        del _suspicious_ips[ip_address]
        return False, None, None
    
    return True, data['throttle_level'], data['reason']

def get_client_security_info():
    """
    Get security-related information about the client
    
    Returns:
        dict: Dictionary with client security information
    """
    ip = request.remote_addr
    
    info = {
        'ip_address': ip,
        'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
        'is_tor': is_tor_exit_node(ip),
        'is_proxy': is_known_proxy(ip),
        'is_vpn': is_known_vpn(ip),
        'country': get_country_from_ip(ip) if ip else None,
        'risk_score': calculate_request_risk_score(ip)
    }
    
    # Add restriction info if any
    restricted, level, reason = is_ip_restricted(ip)
    if restricted:
        info['restricted'] = True
        info['restriction_level'] = level
        info['restriction_reason'] = reason
    
    return info

def is_request_suspicious():
    """
    Check if the current request has suspicious characteristics
    
    Returns:
        tuple: (bool, str) - (is_suspicious, reason)
    """
    # Check for missing or suspicious headers
    has_user_agent = bool(request.user_agent)
    has_referer = 'Referer' in request.headers
    
    if not has_user_agent:
        return True, "Missing User-Agent header"
    
    # Check if IP is restricted
    ip = request.remote_addr
    restricted, level, reason = is_ip_restricted(ip)
    if restricted and level in ['medium', 'high']:
        return True, f"IP restriction: {reason}"
    
    # Check for abnormal request characteristics
    if is_tor_exit_node(ip) or is_known_proxy(ip) or is_known_vpn(ip):
        return True, "Request from anonymizing network"
    
    # Calculate overall risk score
    risk_score = calculate_request_risk_score(ip)
    if risk_score >= 70:
        return True, f"High risk score: {risk_score}/100"
    
    return False, None

def calculate_request_risk_score(ip_address):
    """
    Calculate a risk score for a request
    
    Args:
        ip_address: IP address of the request
        
    Returns:
        int: Risk score (0-100)
    """
    score = 0
    
    # Check IP reputation
    if ip_address in _suspicious_ips:
        level = _suspicious_ips[ip_address]['throttle_level']
        if level == 'low':
            score += 20
        elif level == 'medium':
            score += 40
        elif level == 'high':
            score += 60
    
    # Check for anonymizing networks
    if is_tor_exit_node(ip_address):
        score += 30
    
    if is_known_proxy(ip_address) or is_known_vpn(ip_address):
        score += 20
    
    # Check for high rate of failed attempts
    if ip_address in _rate_limit_store:
        failed_count = _rate_limit_store[ip_address].get('failed_count', 0)
        unique_accounts = len(_rate_limit_store[ip_address].get('unique_accounts', set()))
        
        if failed_count > 20:
            score += 30
        elif failed_count > 10:
            score += 20
        elif failed_count > 5:
            score += 10
        
        # Multiple account access attempts
        if unique_accounts > 10:
            score += 30
        elif unique_accounts > 5:
            score += 20
        elif unique_accounts > 3:
            score += 10
    
    # Cap the score at 100
    return min(score, 100)

def is_tor_exit_node(ip_address):
    """Simplified check if IP is a Tor exit node (replace with real data in production)"""
    # In a real implementation, this would use a database of Tor exit nodes
    return False

def is_known_proxy(ip_address):
    """Simplified check if IP is a known proxy (replace with real data in production)"""
    # In a real implementation, this would use a database of proxy IPs
    return False

def is_known_vpn(ip_address):
    """Simplified check if IP is a known VPN (replace with real data in production)"""
    # In a real implementation, this would use a database of VPN IPs
    return False

def get_country_from_ip(ip_address):
    """Simplified country detection (replace with real geolocation in production)"""
    # In a real implementation, this would use a geolocation database
    return "Unknown"

def require_secure_login(f):
    """
    Decorator to apply enhanced security checks on login routes
    
    Args:
        f: View function to decorate
        
    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Apply rate limiting
        ip = request.remote_addr
        
        # Check if IP is blocked
        restricted, level, reason = is_ip_restricted(ip)
        if restricted and level == 'high':
            logger.warning(f"Blocked login attempt from restricted IP: {ip} - {reason}")
            return "Access denied due to security restrictions", 403
        
        # Check for suspicious request characteristics
        suspicious, reason = is_request_suspicious()
        if suspicious:
            logger.warning(f"Suspicious login attempt blocked: {ip} - {reason}")
            return "Access denied due to security restrictions", 403
        
        # If IP is throttled, add a delay
        if restricted and level == 'medium':
            time.sleep(2)  # Add delay to throttle brute force attempts
        
        # Proceed with the login
        return f(*args, **kwargs)
    
    return decorated_function

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
        "123456789", "trustno1", "princess", "sunshine", "nicole"
    ]
    
    if any(pwd in password.lower() for pwd in common_passwords):
        return False, "Password is too common. Please choose a stronger password."
    
    return True, ""

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


def log_security_event(event_type, user_id=None, description=None, ip_address=None, 
                    resource_type=None, resource_id=None, metadata=None, severity='INFO'):
    """
    Log a security event to the audit log
    
    Args:
        event_type: Type of security event (e.g., 'login', 'logout', 'password_change')
        user_id: User ID associated with the event (optional)
        description: Human-readable description of the event (optional)
        ip_address: IP address associated with the event (optional)
        resource_type: Type of resource being accessed (optional)
        resource_id: ID of the resource being accessed (optional)
        metadata: Additional metadata about the event (optional)
        severity: Severity level of the event (default: 'INFO')
        
    Returns:
        bool: True if event was logged successfully
    """
    # Get client information if not provided
    if ip_address is None:
        ip_address = request.remote_addr
    
    # Log the event
    logger.info(f"Security event: {event_type} - User: {user_id} - IP: {ip_address} - {description}")
    
    # In a real implementation, this would save to the database
    try:
        # Import here to avoid circular imports
        from models import db, SecurityLog
        
        # Create log entry
        log = SecurityLog(
            user_id=user_id,
            ip_address=ip_address,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            meta_data=json.dumps(metadata) if metadata else None,
            severity=severity
        )
        
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to log security event: {str(e)}")
        return False


def is_secure_password(password, user=None):
    """
    Check if a password is secure based on strength requirements and user context
    
    Args:
        password: Password to check
        user: User object (optional) - Used to check for personal information in password
        
    Returns:
        tuple: (bool, str) - (is_secure, error_message)
    """
    # Check basic password strength
    is_strong, error = is_password_strong(password)
    if not is_strong:
        return False, error
    
    # If user is provided, check for personal information in password
    if user:
        # Check if password contains username, email, or name
        personal_info = [
            user.username.lower() if hasattr(user, 'username') and user.username else None,
            user.email.lower() if hasattr(user, 'email') and user.email else None,
            user.first_name.lower() if hasattr(user, 'first_name') and user.first_name else None,
            user.last_name.lower() if hasattr(user, 'last_name') and user.last_name else None
        ]
        
        for info in personal_info:
            if info and len(info) > 3 and info in password.lower():
                return False, "Password contains personal information. Please choose a different password."
    
    return True, ""


def cleanup_expired_sessions():
    """
    Clean up expired sessions to prevent session buildup
    
    Returns:
        int: Number of sessions cleaned up
    """
    # This is a placeholder for session cleanup
    # In a real implementation, this would clean up expired sessions in the database or file system
    logger.info("Cleaning up expired sessions")
    return 0