"""
Cache Service - Phase 4.3 Performance Optimization
Redis-based caching with fallback to in-memory cache
"""
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import hashlib

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")

class CacheService:
    """Unified caching service with Redis backend and in-memory fallback"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_cache = {}
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 5 minutes)
        """
        try:
            if self.redis_client:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.memory_cache[key] = value
                # In-memory cache doesn't expire, but we limit size
                if len(self.memory_cache) > 1000:
                    # Remove oldest 100 items
                    keys_to_remove = list(self.memory_cache.keys())[:100]
                    for k in keys_to_remove:
                        del self.memory_cache[k]
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

# Global cache instance
_cache_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """Get or create global cache service"""
    global _cache_service
    if _cache_service is None:
        import os
        redis_url = os.getenv('REDIS_URL')
        _cache_service = CacheService(redis_url)
    return _cache_service

def cached(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=600, key_prefix="user_data")
        def get_user_data(user_id):
            return expensive_query(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()
            
            # Generate cache key
            cache_key = cache.cache_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(key_pattern: str):
    """Invalidate cache keys matching pattern"""
    cache = get_cache_service()
    if cache.redis_client:
        try:
            keys = cache.redis_client.keys(f"{key_pattern}*")
            if keys:
                cache.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching {key_pattern}")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
