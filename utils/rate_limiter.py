"""
Rate Limiting Implementation
Protects authentication endpoints from abuse
"""

import os
import json
import logging
from functools import wraps
from flask import request, jsonify, session
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """In-memory rate limiter with fallback storage"""
    
    def __init__(self):
        self.memory_store = {}  # Fallback storage
        
    def _get_identifier(self, identifier_type='ip'):
        """Get identifier for rate limiting"""
        if identifier_type == 'ip':
            forwarded_for = request.headers.get('X-Forwarded-For', request.remote_addr)
            return forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr
        elif identifier_type == 'session':
            return session.get('session_id', request.remote_addr)
        elif identifier_type == 'user':
            user = session.get('user', {})
            return user.get('id', request.remote_addr)
        else:
            return request.remote_addr
    
    def _get_key(self, endpoint, identifier):
        """Generate rate limit key"""
        return f"rate_limit:{endpoint}:{identifier}"
    
    def is_allowed(self, endpoint, max_requests, window_seconds, identifier_type='ip'):
        """Check if request is allowed under rate limit"""
        identifier = self._get_identifier(identifier_type)
        key = self._get_key(endpoint, identifier)
        now = datetime.utcnow()
        
        # Memory-based rate limiting
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old entries
        cutoff_time = now - timedelta(seconds=window_seconds)
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if timestamp > cutoff_time
        ]
        
        # Check limit
        if len(self.memory_store[key]) >= max_requests:
            return False
        
        # Add current request
        self.memory_store[key].append(now)
        return True
    
    def get_reset_time(self, endpoint, window_seconds, identifier_type='ip'):
        """Get time when rate limit resets"""
        identifier = self._get_identifier(identifier_type)
        key = self._get_key(endpoint, identifier)
        
        # For memory store, return window from first request
        if key in self.memory_store and self.memory_store[key]:
            first_request = min(self.memory_store[key])
            return first_request + timedelta(seconds=window_seconds)
        
        return datetime.utcnow() + timedelta(seconds=window_seconds)

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests=60, window=60, identifier_type='ip'):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint or 'unknown'
            
            if not rate_limiter.is_allowed(endpoint, max_requests, window, identifier_type):
                reset_time = rate_limiter.get_reset_time(endpoint, window, identifier_type)
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again after {reset_time.strftime("%Y-%m-%d %H:%M:%S")} UTC'
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
                
                return response
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Specific rate limiters for auth endpoints
login_rate_limit = rate_limit(max_requests=5, window=300, identifier_type='ip')  # 5 per 5 minutes
oauth_rate_limit = rate_limit(max_requests=10, window=600, identifier_type='ip')  # 10 per 10 minutes