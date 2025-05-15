"""
Caching utility to improve performance and reduce API/DB calls.
"""

import time
import logging
import threading
import functools
from datetime import datetime, timedelta

# Simple in-memory cache
_cache = {}
_cache_lock = threading.RLock()

def cache_result(ttl_seconds=3600):
    """
    Cache function results for a specified time period.
    
    Args:
        ttl_seconds (int): Time to live in seconds. Default is 1 hour.
        
    Returns:
        function: Decorated function with caching
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            with _cache_lock:
                # Check if result is in cache and not expired
                if cache_key in _cache:
                    result, timestamp = _cache[cache_key]
                    if timestamp + ttl_seconds > time.time():
                        return result
                
                # Call the function and cache the result
                result = func(*args, **kwargs)
                _cache[cache_key] = (result, time.time())
                
                # Clean up old cache entries (optional)
                if len(_cache) > 1000:  # Prevent unbounded growth
                    cleanup_cache()
                    
                return result
        return wrapper
    return decorator

def cleanup_cache(max_age_seconds=86400):
    """
    Remove old entries from cache.
    
    Args:
        max_age_seconds (int): Maximum age in seconds. Default is 24 hours.
    """
    now = time.time()
    with _cache_lock:
        expired_keys = [
            key for key, (_, timestamp) in _cache.items() 
            if timestamp + max_age_seconds < now
        ]
        for key in expired_keys:
            del _cache[key]
        
        logging.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries. Current size: {len(_cache)}")

def clear_cache():
    """Clear the entire cache."""
    with _cache_lock:
        _cache.clear()
        logging.debug("Cache cleared")

def get_cache_stats():
    """Get statistics about the cache."""
    with _cache_lock:
        total_entries = len(_cache)
        now = time.time()
        expired_entries = sum(1 for _, timestamp in _cache.values() if timestamp + 3600 < now)
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "cache_size_bytes": sum(len(str(item)) for item in _cache.values())
        }

# Specialized caching for embedding vectors
_embedding_cache = {}
_embedding_cache_lock = threading.RLock()

def cache_embedding(text, embedding, ttl_hours=24):
    """
    Cache an embedding vector for a text string.
    
    Args:
        text (str): The text that was embedded
        embedding (np.ndarray): The embedding vector
        ttl_hours (int): Time to live in hours
    """
    # Use a hash of the text as the key to save memory
    import hashlib
    key = hashlib.md5(text.encode()).hexdigest()
    
    with _embedding_cache_lock:
        _embedding_cache[key] = {
            'embedding': embedding,
            'expires': datetime.now() + timedelta(hours=ttl_hours)
        }

def get_cached_embedding(text):
    """
    Retrieve a cached embedding vector if available.
    
    Args:
        text (str): The text to check for cached embedding
        
    Returns:
        np.ndarray or None: The cached embedding or None if not found/expired
    """
    import hashlib
    key = hashlib.md5(text.encode()).hexdigest()
    
    with _embedding_cache_lock:
        if key in _embedding_cache:
            cache_item = _embedding_cache[key]
            if cache_item['expires'] > datetime.now():
                return cache_item['embedding']
            else:
                # Remove expired entry
                del _embedding_cache[key]
    
    return None

def cleanup_embedding_cache():
    """Remove expired embedding vectors from cache."""
    now = datetime.now()
    with _embedding_cache_lock:
        expired_keys = [
            key for key, item in _embedding_cache.items() 
            if item['expires'] < now
        ]
        for key in expired_keys:
            del _embedding_cache[key]
        
        logging.debug(f"Embedding cache cleanup: removed {len(expired_keys)} expired entries. Current size: {len(_embedding_cache)}")