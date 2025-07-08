import json
import time
import logging
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self._cache = {}  # In-memory fallback
        self.use_redis = False
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.use_redis = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_redis:
                value = self.redis.get(key)
                return json.loads(value) if value else None
            return self._cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache"""
        try:
            if self.use_redis:
                self.redis.set(key, json.dumps(value, default=str), ex=ttl)
            else:
                self._cache[key] = {
                    'value': value,
                    'expires': time.time() + ttl
                }
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.use_redis:
                self.redis.delete(key)
            else:
                self._cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear(self):
        """Clear all cache"""
        try:
            if self.use_redis:
                self.redis.flushdb()
            else:
                self._cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Global cache instance
cache = CacheManager()
