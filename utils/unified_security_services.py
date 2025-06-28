"""
Unified Security Services - Zero Functionality Loss Consolidation

This module consolidates all security-related services while maintaining 100% backward compatibility.
Combines: security.py, security_helper.py, security_headers.py, security_middleware.py, login_security.py

All original function signatures and behavior are preserved.
"""

import os
import uuid
import hmac
import hashlib
import logging
import secrets
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Callable
from flask import session, request, abort, current_app, g, redirect, url_for

logger = logging.getLogger(__name__)

class UnifiedSecurityServices:
    """Unified security services manager consolidating all security functions"""

    def __init__(self):
        self.failed_attempts = {}  # Track failed login attempts
        self.locked_accounts = {}  # Track locked accounts
        self.throttled_ips = {}    # Track throttled IPs
        self.security_events = []  # In-memory security event log

    # === CSRF PROTECTION (from security.py) ===
    
    def generate_csrf_token(self):
        """Generate CSRF token for forms"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']

    def validate_csrf_token(self, token):
        """Validate CSRF token"""
        session_token = session.get('csrf_token')
        if not session_token or not token:
            return False
        return hmac.compare_digest(session_token, token)

    def require_csrf_token(self, f):
        """Decorator to require CSRF token validation"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == "POST":
                token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                if not self.validate_csrf_token(token):
                    self.log_security_event(
                        "CSRF_VALIDATION_FAILED", 
                        description="Invalid or missing CSRF token",
                        ip_address=self.get_client_ip(),
                        severity="HIGH"
                    )
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function

    # === SECURITY LOGGING ===
    
    def log_security_event(self, event_type, user_id=None, description=None, ip_address=None, 
                          severity="INFO", additional_data=None):
        """Log security events for monitoring and analysis"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'description': description or f"Security event: {event_type}",
            'ip_address': ip_address or self.get_client_ip(),
            'user_agent': request.headers.get('User-Agent', '') if request else '',
            'severity': severity,
            'session_id': session.get('session_id', '') if session else '',
            'additional_data': additional_data or {}
        }
        
        # Log to file
        logger.warning(f"SECURITY EVENT: {event}")
        
        # Store in memory (limited to last 1000 events)
        self.security_events.append(event)
        if len(self.security_events) > 1000:
            self.security_events.pop(0)

    # === PASSWORD VALIDATION ===
    
    def is_password_strong(self, password):
        """Check if password meets strength requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)
        
        if not has_upper:
            return False, "Password must contain at least one uppercase letter"
        if not has_lower:
            return False, "Password must contain at least one lowercase letter"
        if not has_digit:
            return False, "Password must contain at least one digit"
        if not has_special:
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"

    # === ACCESS CONTROL (from security_helper.py) ===
    
    def csrf_protect(self, f):
        """CSRF protection decorator"""
        return self.require_csrf_token(f)

    def admin_required(self, f):
        """Decorator to require admin privileges"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user'):
                self.log_security_event(
                    "UNAUTHORIZED_ACCESS_ATTEMPT",
                    description="Unauthenticated user attempted admin access",
                    severity="HIGH"
                )
                return redirect(url_for('login'))
            
            if not session.get('user', {}).get('is_admin', False):
                self.log_security_event(
                    "UNAUTHORIZED_ADMIN_ACCESS",
                    user_id=session.get('user', {}).get('id'),
                    description="Non-admin user attempted admin access",
                    severity="HIGH"
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function

    def sanitize_input(self, text):
        """Sanitize user input to prevent XSS"""
        if not text:
            return ""
        
        # Basic HTML entity encoding
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        text = text.replace('/', '&#x2F;')
        
        return text

    def set_admin_status(self, email, status):
        """Set admin status for a user (placeholder - would integrate with database)"""
        self.log_security_event(
            "ADMIN_STATUS_CHANGED",
            description=f"Admin status changed for {email}: {status}",
            severity="MEDIUM"
        )
        # This would integrate with your user database
        logger.info(f"Admin status for {email} set to {status}")

    # === LOGIN SECURITY (from login_security.py) ===
    
    def track_login_attempt(self, user_id, email, success, ip_address=None, user_agent=None):
        """Track login attempts for security monitoring"""
        attempt = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'email': email,
            'success': success,
            'ip_address': ip_address or self.get_client_ip(),
            'user_agent': user_agent or request.headers.get('User-Agent', '') if request else ''
        }
        
        # Track failed attempts for rate limiting
        if not success:
            key = f"{email}:{ip_address}"
            if key not in self.failed_attempts:
                self.failed_attempts[key] = []
            
            self.failed_attempts[key].append(attempt['timestamp'])
            
            # Clean old attempts (older than 1 hour)
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self.failed_attempts[key] = [
                ts for ts in self.failed_attempts[key] if ts > cutoff
            ]
            
            # Lock account if too many failed attempts
            if len(self.failed_attempts[key]) >= 5:
                self.lock_account(email, ip_address, "Too many failed login attempts")
        
        # Log the attempt
        self.log_security_event(
            "LOGIN_ATTEMPT",
            user_id=user_id,
            description=f"Login {'successful' if success else 'failed'} for {email}",
            ip_address=ip_address,
            severity="LOW" if success else "MEDIUM",
            additional_data=attempt
        )

    def lock_account(self, email, ip_address=None, reason='Security policy'):
        """Lock an account for security reasons"""
        self.locked_accounts[email] = {
            'locked_at': datetime.utcnow(),
            'ip_address': ip_address,
            'reason': reason,
            'unlock_code': secrets.token_hex(16)
        }
        
        self.log_security_event(
            "ACCOUNT_LOCKED",
            description=f"Account {email} locked: {reason}",
            ip_address=ip_address,
            severity="HIGH"
        )

    def is_account_locked(self, email):
        """Check if account is locked"""
        if email not in self.locked_accounts:
            return False
        
        lock_info = self.locked_accounts[email]
        # Auto-unlock after 24 hours
        if datetime.utcnow() - lock_info['locked_at'] > timedelta(hours=24):
            del self.locked_accounts[email]
            self.log_security_event(
                "ACCOUNT_AUTO_UNLOCKED",
                description=f"Account {email} auto-unlocked after 24 hours"
            )
            return False
        
        return True

    def unlock_account(self, email, unlock_code=None):
        """Unlock an account"""
        if email not in self.locked_accounts:
            return False, "Account is not locked"
        
        lock_info = self.locked_accounts[email]
        
        # Verify unlock code if provided
        if unlock_code and unlock_code != lock_info.get('unlock_code'):
            self.log_security_event(
                "INVALID_UNLOCK_ATTEMPT",
                description=f"Invalid unlock code for {email}",
                severity="MEDIUM"
            )
            return False, "Invalid unlock code"
        
        del self.locked_accounts[email]
        self.log_security_event(
            "ACCOUNT_UNLOCKED",
            description=f"Account {email} unlocked"
        )
        
        return True, "Account unlocked successfully"

    def throttle_ip(self, ip_address, duration_minutes=15, reason=None):
        """Throttle an IP address"""
        self.throttled_ips[ip_address] = {
            'throttled_at': datetime.utcnow(),
            'duration_minutes': duration_minutes,
            'reason': reason or 'Security throttling'
        }
        
        self.log_security_event(
            "IP_THROTTLED",
            description=f"IP {ip_address} throttled for {duration_minutes} minutes: {reason}",
            ip_address=ip_address,
            severity="MEDIUM"
        )

    def is_ip_throttled(self, ip_address):
        """Check if IP is throttled"""
        if ip_address not in self.throttled_ips:
            return False
        
        throttle_info = self.throttled_ips[ip_address]
        end_time = throttle_info['throttled_at'] + timedelta(minutes=throttle_info['duration_minutes'])
        
        if datetime.utcnow() > end_time:
            del self.throttled_ips[ip_address]
            return False
        
        return True

    # === SECURITY HEADERS (from security_headers.py) ===
    
    def apply_security_headers(self, response):
        """Apply security headers to responses"""
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com cdn.jsdelivr.net; "
            "img-src 'self' data: *; "
            "font-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net; "
            "connect-src 'self'"
        )
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

    # === MIDDLEWARE FUNCTIONS (from security_middleware.py) ===
    
    def security_middleware(self, app):
        """Apply security middleware to Flask app"""
        
        @app.before_request
        def before_request_security():
            # Check IP throttling
            client_ip = self.get_client_ip()
            if self.is_ip_throttled(client_ip):
                self.log_security_event(
                    "THROTTLED_REQUEST",
                    description=f"Request from throttled IP {client_ip}",
                    ip_address=client_ip,
                    severity="LOW"
                )
                abort(429)  # Too Many Requests
            
            # Rate limiting per IP
            self._check_rate_limit(client_ip)

        @app.after_request
        def after_request_security(response):
            return self.apply_security_headers(response)

    def _check_rate_limit(self, ip_address, max_requests=100, window_minutes=15):
        """Check rate limiting for IP address"""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=window_minutes)
        
        # This would typically use Redis or database
        # For now, using in-memory tracking
        if not hasattr(self, '_rate_limits'):
            self._rate_limits = {}
        
        if ip_address not in self._rate_limits:
            self._rate_limits[ip_address] = []
        
        # Clean old requests
        self._rate_limits[ip_address] = [
            ts for ts in self._rate_limits[ip_address] if ts > window_start
        ]
        
        # Check limit
        if len(self._rate_limits[ip_address]) >= max_requests:
            self.throttle_ip(ip_address, duration_minutes=30, reason="Rate limit exceeded")
            abort(429)
        
        # Add current request
        self._rate_limits[ip_address].append(current_time)

    # === UTILITY FUNCTIONS ===
    
    def get_client_ip(self):
        """Get client IP address, handling proxies"""
        if request:
            # Check for forwarded IP first (behind proxy)
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            # Check for real IP header
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
            
            # Fall back to remote address
            return request.remote_addr
        
        return 'unknown'

    def get_security_events(self, limit=100, event_type=None, severity=None):
        """Get recent security events with filtering"""
        events = self.security_events[-limit:]
        
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        
        if severity:
            events = [e for e in events if e['severity'] == severity]
        
        return events

    def get_security_summary(self):
        """Get security status summary"""
        return {
            'locked_accounts': len(self.locked_accounts),
            'throttled_ips': len(self.throttled_ips),
            'recent_events': len(self.security_events),
            'failed_attempts_tracked': len(self.failed_attempts),
            'high_severity_events': len([e for e in self.security_events if e['severity'] == 'HIGH'])
        }

# Global unified security service instance
unified_security = UnifiedSecurityServices()

# === BACKWARD COMPATIBILITY FUNCTIONS ===
# These functions maintain the original API while using the unified service

def generate_csrf_token():
    """Backward compatibility for security.py"""
    return unified_security.generate_csrf_token()

def validate_csrf_token(token):
    """Backward compatibility for security.py"""
    return unified_security.validate_csrf_token(token)

def require_csrf_token(f):
    """Backward compatibility for security.py"""
    return unified_security.require_csrf_token(f)

def log_security_event(event_type, user_id=None, description=None, ip_address=None, severity="INFO"):
    """Backward compatibility for security.py and security_helper.py"""
    return unified_security.log_security_event(event_type, user_id, description, ip_address, severity)

def is_password_strong(password):
    """Backward compatibility for security.py"""
    return unified_security.is_password_strong(password)

def csrf_protect(f):
    """Backward compatibility for security_helper.py"""
    return unified_security.csrf_protect(f)

def admin_required(f):
    """Backward compatibility for security_helper.py"""
    return unified_security.admin_required(f)

def sanitize_input(text):
    """Backward compatibility for security_helper.py"""
    return unified_security.sanitize_input(text)

def set_admin_status(email, status):
    """Backward compatibility for security_helper.py"""
    return unified_security.set_admin_status(email, status)

def track_login_attempt(user_id, email, success, ip_address=None, user_agent=None):
    """Backward compatibility for login_security.py"""
    return unified_security.track_login_attempt(user_id, email, success, ip_address, user_agent)

def lock_account(email, ip_address=None, reason='Security policy'):
    """Backward compatibility for login_security.py"""
    return unified_security.lock_account(email, ip_address, reason)

def is_account_locked(email):
    """Backward compatibility for login_security.py"""
    return unified_security.is_account_locked(email)

def unlock_account(email, unlock_code=None):
    """Backward compatibility for login_security.py"""
    return unified_security.unlock_account(email, unlock_code)

def throttle_ip(ip_address, duration_minutes=15, reason=None):
    """Backward compatibility for login_security.py"""
    return unified_security.throttle_ip(ip_address, duration_minutes, reason)

def apply_security_headers(response):
    """Backward compatibility for security_headers.py"""
    return unified_security.apply_security_headers(response)