"""
API Response Caching
Implements caching for API responses to improve performance and reduce load
"""

import os
import json
import hashlib
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify

logger = logging.getLogger(__name__)


class CacheBackend:
    """Base class for cache backends."""

    def get(self, key):
        """Get value from cache."""
        raise NotImplementedError

    def set(self, key, value, ttl=300):
        """Set value in cache with TTL in seconds."""
        raise NotImplementedError

    def delete(self, key):
        """Delete value from cache."""
        raise NotImplementedError

    def clear(self):
        """Clear all cached values."""
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """In-memory cache backend (single instance only)."""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key):
        """Get value from memory cache."""
        # Check if expired
        if key in self._expiry:
            if datetime.utcnow() > self._expiry[key]:
                self.delete(key)
                return None

        return self._cache.get(key)

    def set(self, key, value, ttl=300):
        """Set value in memory cache."""
        self._cache[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)

    def delete(self, key):
        """Delete value from memory cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def clear(self):
        """Clear memory cache."""
        self._cache.clear()
        self._expiry.clear()

    def cleanup_expired(self):
        """Remove expired entries from cache."""
        now = datetime.utcnow()
        expired_keys = [k for k, exp in self._expiry.items() if now > exp]
        for key in expired_keys:
            self.delete(key)


class RedisCache(CacheBackend):
    """Redis cache backend (distributed, production-ready)."""

    def __init__(self, redis_url):
        """Initialize Redis cache."""
        try:
            import redis
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            logger.info(f"Redis cache initialized: {redis_url[:20]}...")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            raise

    def get(self, key):
        """Get value from Redis cache."""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key, value, ttl=300):
        """Set value in Redis cache."""
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key):
        """Delete value from Redis cache."""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear(self):
        """Clear Redis cache."""
        try:
            self.client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class APICache:
    """
    API response caching manager.

    Provides caching for API endpoints with automatic key generation
    and configurable TTL.
    """

    def __init__(self, backend=None):
        """
        Initialize API cache.

        Args:
            backend: Cache backend instance (MemoryCache or RedisCache)
        """
        if backend is None:
            # Try Redis first, fall back to memory
            redis_url = os.environ.get('REDIS_URL') or os.environ.get('REDISCLOUD_URL')
            if redis_url:
                try:
                    backend = RedisCache(redis_url)
                    logger.info("API cache using Redis backend")
                except Exception:
                    backend = MemoryCache()
                    logger.info("API cache using memory backend (fallback)")
            else:
                backend = MemoryCache()
                logger.info("API cache using memory backend")

        self.backend = backend
        self.enabled = os.environ.get('CACHE_ENABLED', 'true').lower() == 'true'

    def generate_key(self, prefix, *args, **kwargs):
        """
        Generate cache key from arguments.

        Args:
            prefix: Key prefix (e.g., 'api', 'user')
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key

        Returns:
            str: Generated cache key
        """
        key_parts = [prefix]

        # Add args
        for arg in args:
            key_parts.append(str(arg))

        # Add sorted kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")

        # Create hash for long keys
        key_string = ':'.join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return key_string

    def get(self, key):
        """Get value from cache."""
        if not self.enabled:
            return None
        return self.backend.get(key)

    def set(self, key, value, ttl=300):
        """Set value in cache."""
        if not self.enabled:
            return
        self.backend.set(key, value, ttl)

    def delete(self, key):
        """Delete value from cache."""
        self.backend.delete(key)

    def clear(self):
        """Clear all cached values."""
        self.backend.clear()


# Global cache instance
_api_cache = None


def init_api_cache(backend=None):
    """
    Initialize global API cache.

    Args:
        backend: Optional cache backend

    Returns:
        APICache: Initialized cache instance
    """
    global _api_cache
    _api_cache = APICache(backend)
    logger.info("API cache initialized")
    return _api_cache


def get_api_cache():
    """
    Get global API cache instance.

    Returns:
        APICache: Cache instance
    """
    global _api_cache
    if _api_cache is None:
        _api_cache = init_api_cache()
    return _api_cache


def cached(ttl=300, key_prefix='api'):
    """
    Decorator to cache API endpoint responses.

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Cache key prefix

    Example:
        @app.route('/api/data')
        @cached(ttl=600, key_prefix='data')
        def get_data():
            return jsonify({'data': expensive_operation()})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = get_api_cache()

            # Generate cache key from request
            cache_key_parts = [key_prefix, request.path]

            # Include query parameters
            if request.args:
                for k, v in sorted(request.args.items()):
                    cache_key_parts.append(f"{k}={v}")

            # Include user ID if authenticated
            try:
                from flask_login import current_user
                if current_user.is_authenticated:
                    cache_key_parts.append(f"user:{current_user.id}")
            except (ImportError, AttributeError):
                pass

            cache_key = ':'.join(cache_key_parts)

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit: {cache_key}")
                response = jsonify(cached_response)
                response.headers['X-Cache'] = 'HIT'
                return response

            # Call original function
            logger.debug(f"Cache miss: {cache_key}")
            response = f(*args, **kwargs)

            # Cache the response if successful
            if response.status_code == 200:
                try:
                    response_data = response.get_json()
                    cache.set(cache_key, response_data, ttl)
                except Exception as e:
                    logger.warning(f"Failed to cache response: {e}")

            response.headers['X-Cache'] = 'MISS'
            return response

        return decorated_function
    return decorator


def cache_invalidate(key_prefix):
    """
    Invalidate cache entries matching a prefix.

    Args:
        key_prefix: Prefix of keys to invalidate

    Note:
        This is a simple implementation that only works with specific keys.
        For pattern-based invalidation, use Redis SCAN in RedisCache backend.
    """
    cache = get_api_cache()
    cache.delete(key_prefix)
    logger.info(f"Cache invalidated: {key_prefix}")


def cache_clear_all():
    """Clear all cached data."""
    cache = get_api_cache()
    cache.clear()
    logger.info("All cache cleared")
