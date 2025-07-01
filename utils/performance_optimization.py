"""
Performance Optimization Utilities
Provides caching, connection pooling, and performance monitoring
"""

import time
import logging
from functools import wraps
from typing import Any, Dict, Optional
from flask import g, request

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache for performance optimization"""
    
    def __init__(self, default_timeout: int = 300):
        self.cache = {}
        self.timeouts = {}
        self.default_timeout = default_timeout
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            if time.time() < self.timeouts.get(key, 0):
                return self.cache[key]
            else:
                # Expired
                self.delete(key)
        return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> None:
        """Set value in cache"""
        if timeout is None:
            timeout = self.default_timeout
        
        self.cache[key] = value
        self.timeouts[key] = time.time() + timeout
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.timeouts.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()
        self.timeouts.clear()

# Global cache instance
cache = SimpleCache()

def cached(timeout: int = 300, key_func: callable = None):
    """
    Caching decorator for expensive operations
    
    Args:
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key (default: use function name + args)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{f.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            execution_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"Performance: {f.__name__} took {execution_time:.3f}s, success: {success}")
            
            # Store in request context if available
            if hasattr(g, 'performance_metrics'):
                g.performance_metrics[f.__name__] = {
                    'execution_time': execution_time,
                    'success': success
                }
        
        return result
    
    wrapper.__name__ = f.__name__
    return wrapper

def optimize_database_queries():
    """Utility to optimize database query performance"""
    # This would integrate with SQLAlchemy to add query optimization
    pass
