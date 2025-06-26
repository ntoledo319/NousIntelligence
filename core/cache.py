"""
Consolidated Cache Management Core Module
Provides @cache(ttl=300) decorator for heavy operations
"""
import os
import time
import json
import logging
from functools import wraps
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache_store: Dict[str, Dict[str, Any]] = {}

def cache(ttl: int = 300):
    """
    Cache decorator with TTL (time-to-live) support
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if cached result exists and is still valid
            if cache_key in _cache_store:
                cached_item = _cache_store[cache_key]
                if time.time() - cached_item['timestamp'] < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_item['data']
                else:
                    # Cache expired
                    del _cache_store[cache_key]
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            
            _cache_store[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            return result
        return wrapper
    return decorator

def clear_cache():
    """Clear all cached data"""
    global _cache_store
    _cache_store.clear()
    logger.info("Cache cleared")

def cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        'total_entries': len(_cache_store),
        'entries': list(_cache_store.keys()),
        'memory_usage_estimate': sum(len(str(v)) for v in _cache_store.values())
    }