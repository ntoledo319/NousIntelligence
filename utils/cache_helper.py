"""
Cache helper for storing and retrieving frequently accessed data.
Helps reduce API calls and database queries for better performance.
"""

import time
import functools
import logging
import threading
import hashlib
import json
import pickle
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

# Type variable for generic return type
T = TypeVar('T')

# Cache storage - using dictionaries for simplicity, could be replaced with Redis in production
_result_cache: Dict[str, Tuple[Any, float]] = {}
_embedding_cache: Dict[str, Tuple[Any, float]] = {}

# Lock for thread safety
_cache_lock = threading.RLock()

# Maximum cache sizes to prevent memory issues
MAX_RESULT_CACHE_SIZE = 1000  # Entries
MAX_EMBEDDING_CACHE_SIZE = 500  # Entries

def cache_result(ttl_seconds: int = 600):
    """
    Decorator to cache function results for a specified time.
    
    Args:
        ttl_seconds: Time to live in seconds for cache entries
        
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key based on function name and arguments
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            # Check if result is in cache and not expired
            cached_result = _get_from_cache(cache_key, _result_cache)
            if cached_result is not None:
                logging.debug(f"Cache hit for {func.__name__}")
                return cached_result
                
            # Execute function and cache result
            result = func(*args, **kwargs)
            _store_in_cache(cache_key, result, ttl_seconds, _result_cache, MAX_RESULT_CACHE_SIZE)
            
            return result
        return wrapper
    return decorator

def cache_embedding(text: str, embedding: Any, ttl_seconds: int = 86400):
    """
    Cache an embedding vector for a text string.
    
    Args:
        text: The original text
        embedding: The embedding vector to cache
        ttl_seconds: Time to live in seconds
    """
    cache_key = _hash_text(text)
    _store_in_cache(cache_key, embedding, ttl_seconds, _embedding_cache, MAX_EMBEDDING_CACHE_SIZE)
    
def get_cached_embedding(text: str) -> Optional[Any]:
    """
    Get a cached embedding for text if available.
    
    Args:
        text: The text to get embedding for
        
    Returns:
        The cached embedding or None if not found
    """
    cache_key = _hash_text(text)
    return _get_from_cache(cache_key, _embedding_cache)

def clear_caches():
    """Clear all caches."""
    with _cache_lock:
        _result_cache.clear()
        _embedding_cache.clear()
    logging.info("All caches cleared")

def _generate_cache_key(func_name: str, args: Tuple, kwargs: Dict) -> str:
    """Generate a deterministic cache key for function call."""
    try:
        # Convert args and kwargs to JSON-serializable format
        serializable_args = _make_serializable(args)
        serializable_kwargs = _make_serializable(kwargs)
        
        # Combine into a string
        key_parts = [func_name, str(serializable_args), str(serializable_kwargs)]
        combined = json.dumps(key_parts, sort_keys=True)
        
        # Hash the string to get a fixed-length key
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    except Exception as e:
        logging.warning(f"Error generating cache key: {e}. Using fallback method.")
        # Fallback: Use function name and object IDs
        return f"{func_name}_{hash(args)}_{hash(frozenset(kwargs.items() if kwargs else []))}"

def _hash_text(text: str) -> str:
    """Create a hash for text content."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def _make_serializable(obj: Any) -> Any:
    """Attempt to make an object JSON-serializable."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        # For custom objects, use a string representation or specific attributes
        return str(obj)
    else:
        # Just convert to string for non-serializable types
        return str(obj)

def _get_from_cache(key: str, cache: Dict[str, Tuple[Any, float]]) -> Optional[Any]:
    """Get an item from cache if it exists and is not expired."""
    with _cache_lock:
        if key in cache:
            value, expiry = cache[key]
            if expiry > time.time():
                return value
            else:
                # Remove expired entry
                del cache[key]
    return None

def _store_in_cache(key: str, value: Any, ttl_seconds: int, 
                   cache: Dict[str, Tuple[Any, float]], max_size: int):
    """Store an item in cache with expiry time."""
    with _cache_lock:
        # Check if cache is full and remove oldest entry if needed
        if len(cache) >= max_size:
            # Find and remove oldest entry (lowest expiry time)
            oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
            del cache[oldest_key]
            
        # Calculate expiry time and store
        expiry = time.time() + ttl_seconds
        
        # Use pickle to store more complex objects
        try:
            # Attempt to pickle to verify serializability
            pickle.dumps(value)
            cache[key] = (value, expiry)
        except (pickle.PickleError, TypeError) as e:
            logging.warning(f"Value not cache-able: {str(e)}")
            # For non-serializable objects, don't cache
            return