"""
Rate Limiting System
Implements rate limiting to prevent abuse and ensure API stability
"""

import time
from collections import defaultdict, deque
from functools import wraps
from typing import Dict, Any
from flask import request, jsonify, g

class RateLimiter:
    """Memory-based rate limiter for API endpoints"""
    
    def __init__(self):
        # Store request timestamps for each IP
        self.requests = defaultdict(deque)
        self.blocked_ips = {}  # IP -> block_until_timestamp
    
    def is_allowed(self, ip: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        # Check if IP is temporarily blocked
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                return False
            else:
                # Block expired, remove it
                del self.blocked_ips[ip]
        
        # Clean old requests outside the window
        while self.requests[ip] and self.requests[ip][0] < now - window:
            self.requests[ip].popleft()
        
        # Check if under limit
        if len(self.requests[ip]) < limit:
            self.requests[ip].append(now)
            return True
        
        # Rate limit exceeded - temporary block for repeat offenders
        if len(self.requests[ip]) > limit * 2:  # Aggressive behavior
            self.blocked_ips[ip] = now + 300  # 5-minute block
        
        return False
    
    def get_reset_time(self, ip: str, window: int) -> int:
        """Get time until rate limit resets"""
        if not self.requests[ip]:
            return 0
        
        oldest_request = self.requests[ip][0]
        return max(0, int(oldest_request + window - time.time()))

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(requests_per_minute: int = 60):
    """
    Rate limiting decorator
    
    Args:
        requests_per_minute: Maximum requests allowed per minute
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get client IP
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if ip:
                ip = ip.split(',')[0].strip()  # Handle proxy forwarded IPs
            else:
                ip = 'unknown'
            
            # Check rate limit
            if not rate_limiter.is_allowed(ip, requests_per_minute, 60):
                reset_time = rate_limiter.get_reset_time(ip, 60)
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': reset_time,
                    'limit': requests_per_minute
                }), 429
            
            # Store rate limit info for response headers
            g.rate_limit_remaining = requests_per_minute - len(rate_limiter.requests[ip])
            g.rate_limit_reset = int(time.time()) + 60
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
