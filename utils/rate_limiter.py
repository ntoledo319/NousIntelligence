"""
Rate Limiting Utility for Authentication Endpoints
Provides protection against brute force attacks
"""

import time
import logging
from flask import request, jsonify, session
from functools import wraps
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store request timestamps per IP
        self.requests = defaultdict(deque)
        # Store blocked IPs with expiry time
        self.blocked_ips = {}
        
    def is_rate_limited(self, ip, max_requests=5, window_minutes=15, block_minutes=30):
        """Check if IP is rate limited"""
        now = datetime.utcnow()
        
        # Check if IP is currently blocked
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[ip]
        
        # Clean old requests outside the window
        window_start = now - timedelta(minutes=window_minutes)
        while self.requests[ip] and self.requests[ip][0] < window_start:
            self.requests[ip].popleft()
        
        # Check if over the limit
        if len(self.requests[ip]) >= max_requests:
            # Block the IP
            self.blocked_ips[ip] = now + timedelta(minutes=block_minutes)
            logger.warning(f"Rate limit exceeded for IP {ip}, blocked for {block_minutes} minutes")
            return True
        
        # Add current request
        self.requests[ip].append(now)
        return False
    
    def get_client_ip(self):
        """Get client IP address, considering proxy headers"""
        # Check for forwarded IP first (for proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or '127.0.0.1'

# Global rate limiter instance
auth_rate_limiter = RateLimiter()

def auth_rate_limit(max_requests=5, window_minutes=15, block_minutes=30):
    """
    Decorator to apply rate limiting to authentication endpoints
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_minutes: Time window in minutes
        block_minutes: How long to block after limit exceeded
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = auth_rate_limiter.get_client_ip()
            
            if auth_rate_limiter.is_rate_limited(ip, max_requests, window_minutes, block_minutes):
                logger.warning(f"Rate limit exceeded for {request.endpoint} from IP {ip}")
                return jsonify({
                    'error': 'Too many requests',
                    'message': f'Rate limit exceeded. Try again in {block_minutes} minutes.',
                    'retry_after': block_minutes * 60
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_rate_limit(f):
    """Specific rate limiter for login attempts - stricter limits"""
    return auth_rate_limit(max_requests=3, window_minutes=10, block_minutes=60)(f)

def oauth_rate_limit(f):
    """Rate limiter for OAuth endpoints - more permissive for development"""
    return auth_rate_limit(max_requests=50, window_minutes=15, block_minutes=5)(f)