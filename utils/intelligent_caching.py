"""
Intelligent Caching System
Multi-layer caching with AI response optimization and automatic invalidation
"""
import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Callable, List
from functools import wraps
import threading

logger = logging.getLogger(__name__)

class IntelligentCache:
    """Multi-layer intelligent caching system"""
    
    def __init__(self, max_memory_size: int = 1000, default_ttl: int = 3600):
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        self.max_memory_size = max_memory_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        
        # AI-specific caching rules
        self.ai_cache_rules = {
            "chat": {"ttl": 1800, "max_size": 500},  # 30 minutes
            "translation": {"ttl": 86400, "max_size": 1000},  # 24 hours
            "analysis": {"ttl": 3600, "max_size": 200},  # 1 hour
            "generation": {"ttl": 7200, "max_size": 300}  # 2 hours
        }
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        key_hash = hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item is expired"""
        return time.time() > item["expires_at"]
    
    def _evict_oldest(self):
        """Evict oldest items when cache is full"""
        with self.lock:
            if len(self.memory_cache) >= self.max_memory_size:
                # Sort by access time and remove oldest
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1]["accessed_at"]
                )
                
                # Remove oldest 20% of items
                evict_count = max(1, len(sorted_items) // 5)
                for i in range(evict_count):
                    key = sorted_items[i][0]
                    del self.memory_cache[key]
                    self.cache_stats["evictions"] += 1
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.memory_cache:
                item = self.memory_cache[key]
                
                if self._is_expired(item):
                    del self.memory_cache[key]
                    self.cache_stats["misses"] += 1
                    return None
                
                # Update access time
                item["accessed_at"] = time.time()
                self.cache_stats["hits"] += 1
                return item["data"]
            
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set item in cache"""
        try:
            with self.lock:
                # Evict if necessary
                self._evict_oldest()
                
                ttl = ttl or self.default_ttl
                expires_at = time.time() + ttl
                
                self.memory_cache[key] = {
                    "data": data,
                    "created_at": time.time(),
                    "accessed_at": time.time(),
                    "expires_at": expires_at,
                    "ttl": ttl
                }
                
                self.cache_stats["size"] = len(self.memory_cache)
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.cache_stats["size"] = len(self.memory_cache)
                return True
            return False
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.memory_cache.clear()
            self.cache_stats["size"] = 0
            self.cache_stats["evictions"] += len(self.memory_cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate_percent": round(hit_rate, 2),
            "memory_usage_percent": round(len(self.memory_cache) / self.max_memory_size * 100, 2)
        }

# Global cache instance
cache = IntelligentCache()

# AI Response caching decorators
def cache_ai_response(response_type: str = "chat", ttl: Optional[int] = None):
    """Decorator to cache AI responses"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            cache_key = cache._generate_key(f"ai:{response_type}", cache_data)
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for AI {response_type}: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                
                # Determine TTL based on response type
                if ttl is not None:
                    cache_ttl = ttl
                elif response_type in cache.ai_cache_rules:
                    cache_ttl = cache.ai_cache_rules[response_type]["ttl"]
                else:
                    cache_ttl = cache.default_ttl
                
                cache.set(cache_key, result, cache_ttl)
                logger.debug(f"Cached AI {response_type}: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

def cache_database_query(ttl: int = 300):
    """Decorator to cache database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            cache_key = cache._generate_key("db", cache_data)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def cache_api_response(ttl: int = 600):
    """Decorator to cache external API responses"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            cache_key = cache._generate_key("api", cache_data)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Cache invalidation helpers
def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a specific user"""
    with cache.lock:
        keys_to_delete = []
        for key in cache.memory_cache.keys():
            if f"user:{user_id}" in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cache.delete(key)

def invalidate_pattern(pattern: str):
    """Invalidate cache entries matching a pattern"""
    with cache.lock:
        keys_to_delete = []
        for key in cache.memory_cache.keys():
            if pattern in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cache.delete(key)

# Cache warming functions
def warm_ai_cache():
    """Pre-warm cache with common AI responses"""
    common_prompts = [
        "Hello, how can I help you today?",
        "What would you like to know?",
        "Please let me know how I can assist you."
    ]
    
    # This would typically call your AI service
    # For now, just log the warming attempt
    logger.info(f"Warming AI cache with {len(common_prompts)} common prompts")

def warm_database_cache():
    """Pre-warm cache with common database queries"""
    # This would typically execute common queries
    logger.info("Warming database cache with common queries")

# Cache monitoring
def get_cache_health() -> Dict[str, Any]:
    """Get cache health metrics"""
    stats = cache.get_stats()
    
    health_status = "healthy"
    if stats["hit_rate_percent"] < 30:
        health_status = "degraded"
    elif stats["memory_usage_percent"] > 90:
        health_status = "critical"
    
    return {
        "status": health_status,
        "statistics": stats,
        "recommendations": _get_cache_recommendations(stats)
    }

def _get_cache_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Get cache optimization recommendations"""
    recommendations = []
    
    if stats["hit_rate_percent"] < 30:
        recommendations.append("Low cache hit rate - consider increasing TTL or cache size")
    
    if stats["memory_usage_percent"] > 90:
        recommendations.append("High memory usage - consider increasing max_memory_size")
    
    if stats["evictions"] > stats["hits"]:
        recommendations.append("High eviction rate - cache size may be too small")
    
    return recommendations

# Context manager for cache operations
class CacheContext:
    """Context manager for cache operations with automatic cleanup"""
    
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.keys_created = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Clean up on error
            for key in self.keys_created:
                cache.delete(key)
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """Set with automatic cleanup tracking"""
        full_key = f"{self.prefix}:{key}"
        if cache.set(full_key, data, ttl):
            self.keys_created.append(full_key)
        return full_key