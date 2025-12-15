"""
Rate Limiting Utility
Provides rate limiting functionality for Flask routes to prevent abuse
"""

import time
from functools import wraps
from collections import defaultdict, deque
from flask import request, jsonify, abort
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed based on rate limit
        
        Args:
            key: Unique identifier (usually IP address)
            limit: Maximum number of requests
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        
        # Clean old requests outside the window
        while self.requests[key] and self.requests[key][0] <= now - window:
            self.requests[key].popleft()
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def get_reset_time(self, key: str, window: int) -> int:
        """Get time until rate limit resets"""
        if not self.requests[key]:
            return 0
        
        oldest_request = self.requests[key][0]
        reset_time = oldest_request + window - time.time()
        return max(0, int(reset_time))

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: int = 60, window: int = 60, per: str = "ip"):
    """
    Rate limiting decorator for Flask routes
    
    Args:
        limit: Number of requests allowed
        window: Time window in seconds
        per: What to rate limit by ('ip', 'user', or custom function)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine the key for rate limiting
            if per == "ip":
                key = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            elif per == "user":
                from flask import session
                key = session.get('user', {}).get('id', request.remote_addr)
            elif callable(per):
                key = per()
            else:
                key = str(per)
            
            # Check rate limit
            if not rate_limiter.is_allowed(key, limit, window):
                reset_time = rate_limiter.get_reset_time(key, window)
                logger.warning(f"Rate limit exceeded for {key}. Reset in {reset_time}s")
                
                if request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests. Try again in {reset_time} seconds.',
                        'retry_after': reset_time
                    }), 429
                else:
                    # For web routes, return a user-friendly error page
                    abort(429)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_rate_limit_status(key: str = None, limit: int = 60, window: int = 60) -> dict:
    """Get current rate limit status for a key"""
    if key is None:
        key = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    now = time.time()
    
    # Clean old requests
    while rate_limiter.requests[key] and rate_limiter.requests[key][0] <= now - window:
        rate_limiter.requests[key].popleft()
    
    current_requests = len(rate_limiter.requests[key])
    remaining = max(0, limit - current_requests)
    reset_time = rate_limiter.get_reset_time(key, window)
    
    return {
        'limit': limit,
        'remaining': remaining,
        'reset_time': reset_time,
        'current_requests': current_requests
    }

# Preconfigured limits used by auth routes
login_rate_limit = rate_limit(limit=5, window=60)   # 5/min
oauth_rate_limit = rate_limit(limit=10, window=60)  # 10/min