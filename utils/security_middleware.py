"""
Security Middleware
Implements comprehensive security headers and protections
"""

from flask import Flask, request, make_response, g
from functools import wraps
from datetime import datetime, timedelta
import logging
import hmac
import hashlib
import time
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


def init_security_headers(app: Flask) -> None:
    """Initialize security headers and middleware for all responses"""
    
    @app.after_request
    def add_security_headers(response):
        """Add comprehensive security headers to all responses"""
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Enable XSS protection in older browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Control referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HSTS for HTTPS enforcement (only on secure connections)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy - comprehensive ruleset
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://apis.google.com https://accounts.google.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://oauth2.googleapis.com https://www.googleapis.com wss:",
            "frame-src https://accounts.google.com",
            "frame-ancestors 'none'",
            "form-action 'self' https://accounts.google.com",
            "base-uri 'self'",
            "object-src 'none'",
            "media-src 'self'",
            "worker-src 'self' blob:",
            "manifest-src 'self'",
            "upgrade-insecure-requests"
        ]
        response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Permissions Policy (formerly Feature Policy)
        permissions = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()"
        ]
        response.headers['Permissions-Policy'] = ", ".join(permissions)
        
        # Remove server header to avoid information disclosure
        response.headers.pop('Server', None)
        
        # Add cache control for security
        if request.endpoint and 'static' not in request.endpoint:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Add X-Request-ID for tracing
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    @app.before_request
    def security_checks():
        """Perform security checks before processing requests"""
        
        # Generate request ID for tracing
        g.request_id = generate_request_id()
        
        # Check for suspicious patterns
        if is_suspicious_request(request):
            logger.warning(f"Suspicious request blocked: {request.url} from {request.remote_addr}")
            return make_response("Forbidden", 403)
        
        # Validate content length
        if request.content_length and request.content_length > app.config.get('MAX_CONTENT_LENGTH', 10485760):
            return make_response("Payload too large", 413)
        
        # Check for common attack patterns in headers
        for header, value in request.headers:
            if contains_attack_pattern(value):
                logger.warning(f"Attack pattern in header {header}: {value[:50]}")
                return make_response("Bad Request", 400)
    
    logger.info("Security middleware initialized with comprehensive protections")


def generate_request_id() -> str:
    """Generate unique request ID for tracing"""
    timestamp = str(int(time.time() * 1000))
    random_part = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
    return f"{timestamp}-{random_part}"


def is_suspicious_request(request) -> bool:
    """Check if request shows suspicious patterns"""
    suspicious_patterns = [
        '../',  # Path traversal
        '..\\',  # Windows path traversal
        '%2e%2e',  # Encoded path traversal
        'eval(',  # Code injection
        'exec(',  # Code injection
        '<script',  # XSS attempt
        'javascript:',  # XSS attempt
        'vbscript:',  # XSS attempt
        'onload=',  # XSS attempt
        'onerror=',  # XSS attempt
        '; DROP TABLE',  # SQL injection
        'UNION SELECT',  # SQL injection
        '/*',  # SQL comment injection
        '--',  # SQL comment injection
    ]
    
    # Check URL
    url_lower = request.url.lower()
    for pattern in suspicious_patterns:
        if pattern.lower() in url_lower:
            return True
    
    # Check form data
    if request.form:
        for value in request.form.values():
            if isinstance(value, str):
                for pattern in suspicious_patterns:
                    if pattern.lower() in value.lower():
                        return True
    
    return False


def contains_attack_pattern(value: str) -> bool:
    """Check if a value contains common attack patterns"""
    if not isinstance(value, str):
        return False
    
    attack_patterns = [
        r'<script[^>]*>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'\.\./|\.\.\\'  # Path traversal
    ]
    
    import re
    for pattern in attack_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    
    return False


def require_https(f):
    """Decorator to require HTTPS for sensitive endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and app.config.get('FLASK_ENV') == 'production':
            return make_response("HTTPS required", 403)
        return f(*args, **kwargs)
    return decorated_function


def validate_origin(allowed_origins: list):
    """Decorator to validate request origin"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            origin = request.headers.get('Origin')
            if origin and origin not in allowed_origins:
                logger.warning(f"Invalid origin: {origin}")
                return make_response("Forbidden", 403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sign_response(response_data: Dict[str, Any], secret: str) -> Dict[str, Any]:
    """Sign API response for integrity verification"""
    # Create signature
    message = json.dumps(response_data, sort_keys=True)
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'data': response_data,
        'signature': signature,
        'timestamp': datetime.utcnow().isoformat()
    }


def verify_signature(signed_data: Dict[str, Any], secret: str) -> bool:
    """Verify signed data integrity"""
    try:
        data = signed_data.get('data')
        signature = signed_data.get('signature')
        
        if not data or not signature:
            return False
        
        # Recreate signature
        message = json.dumps(data, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False


# Additional security utilities
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    import os
    # Remove path separators and null bytes
    filename = filename.replace('/', '').replace('\\', '').replace('\x00', '')
    # Remove leading dots
    while filename.startswith('.'):
        filename = filename[1:]
    # Limit length
    return filename[:255]


def is_safe_url(target: str, host: str) -> bool:
    """Check if URL is safe for redirection"""
    from urllib.parse import urlparse, urljoin
    
    if not target:
        return False
    
    # Parse target URL
    parsed = urlparse(urljoin(host, target))
    
    # Check if it's a relative URL or same host
    return not parsed.netloc or parsed.netloc == urlparse(host).netloc 