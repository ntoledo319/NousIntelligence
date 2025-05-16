"""
@module enhanced_cache
@description Advanced caching system with longer TTLs and multi-tier strategies
@author AI Assistant
"""

import os
import json
import time
import hashlib
import logging
import zlib
import pickle
import threading
import redis
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Callable, Union, Set
from datetime import datetime, timedelta
from collections import OrderedDict

# Configure logger
logger = logging.getLogger(__name__)

# Constants for TTLs (in seconds)
TIER_1_TTL = 3600 * 24 * 30  # 30 days for Tier 1 (very stable data)
TIER_2_TTL = 3600 * 24 * 7   # 7 days for Tier 2 (relatively stable data)
TIER_3_TTL = 3600 * 24       # 24 hours for Tier 3 (daily changing data)
TIER_4_TTL = 3600 * 6        # 6 hours for Tier 4 (frequently changing data)
TIER_5_TTL = 3600            # 1 hour for Tier 5 (highly volatile data)
DEFAULT_TTL = TIER_3_TTL     # Default to Tier 3

# Cache eviction policies
class EvictionPolicy:
    """Cache eviction policy options"""
    LRU = "lru"      # Least Recently Used
    LFU = "lfu"      # Least Frequently Used
    FIFO = "fifo"    # First In First Out
    TTL = "ttl"      # Time To Live based only

# Cache backends
class CacheBackend:
    """Cache backend options"""
    MEMORY = "memory"      # In-memory cache
    REDIS = "redis"        # Redis cache
    FILESYSTEM = "file"    # Filesystem cache
    DATABASE = "db"        # Database cache
    MULTI = "multi"        # Multi-tier cache (memory + redis + file)

# Serialization methods
class SerializationMethod:
    """Serialization method options"""
    JSON = "json"          # JSON serialization (human-readable)
    PICKLE = "pickle"      # Pickle serialization (Python objects)
    COMPRESSED = "zlib"    # Compressed pickle (smaller size)

class CacheTier:
    """Cache tier definitions for different data types"""
    PERMANENT = "permanent"  # Tier 1: Almost permanent data (30 days)
    STABLE = "stable"        # Tier 2: Stable data (7 days)
    DAILY = "daily"          # Tier 3: Daily changing data (24 hours)
    FREQUENT = "frequent"    # Tier 4: Frequently changing data (6 hours)
    VOLATILE = "volatile"    # Tier 5: Highly volatile data (1 hour)

    @staticmethod
    def get_ttl(tier: str) -> int:
        """Get TTL for a specific tier"""
        ttl_map = {
            CacheTier.PERMANENT: TIER_1_TTL,
            CacheTier.STABLE: TIER_2_TTL,
            CacheTier.DAILY: TIER_3_TTL,
            CacheTier.FREQUENT: TIER_4_TTL,
            CacheTier.VOLATILE: TIER_5_TTL
        }
        return ttl_map.get(tier, DEFAULT_TTL)

class MemoryCache:
    """Thread-safe in-memory cache implementation with LRU/LFU eviction"""

    def __init__(self, max_size: int = 10000, eviction_policy: str = EvictionPolicy.LRU):
        """
        Initialize memory cache
        
        Args:
            max_size: Maximum number of items to store in cache
            eviction_policy: Eviction policy (LRU, LFU, FIFO, TTL)
        """
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.lock = threading.RLock()
        
        # Cache data structure depends on eviction policy
        if eviction_policy == EvictionPolicy.LRU:
            self.cache = OrderedDict()  # OrderedDict for LRU
        elif eviction_policy == EvictionPolicy.LFU:
            self.cache = {}  # Dict for data
            self.frequency = {}  # Dict for access frequency
        else:
            self.cache = OrderedDict()  # OrderedDict for FIFO and TTL
            
        # Stats
        self.hits = 0
        self.misses = 0
        self.insertions = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Tuple of (value, expiry_time) or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
                
            if self.eviction_policy == EvictionPolicy.LRU:
                # Get and move to end (most recently used)
                value, expiry = self.cache.pop(key)
                
                # Check if expired
                if expiry and time.time() > expiry:
                    self.misses += 1
                    return None
                    
                # Move to end (most recently used)
                self.cache[key] = (value, expiry)
                self.hits += 1
                return value, expiry
                
            elif self.eviction_policy == EvictionPolicy.LFU:
                # Get without changing order
                value, expiry = self.cache[key]
                
                # Check if expired
                if expiry and time.time() > expiry:
                    self.misses += 1
                    return None
                    
                # Increment frequency
                self.frequency[key] = self.frequency.get(key, 0) + 1
                self.hits += 1
                return value, expiry
                
            else:  # FIFO or TTL
                # Get without changing order
                value, expiry = self.cache[key]
                
                # Check if expired
                if expiry and time.time() > expiry:
                    self.misses += 1
                    return None
                    
                self.hits += 1
                return value, expiry
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds
        """
        with self.lock:
            # Calculate expiry time
            expiry = time.time() + ttl if ttl else None
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict()
                
            # Insert new item
            if self.eviction_policy == EvictionPolicy.LRU:
                # Remove if exists and add to end
                if key in self.cache:
                    self.cache.pop(key)
                self.cache[key] = (value, expiry)
                
            elif self.eviction_policy == EvictionPolicy.LFU:
                # Update value and reset frequency
                self.cache[key] = (value, expiry)
                self.frequency[key] = 1  # Reset frequency
                
            else:  # FIFO or TTL
                # Add to end
                if key in self.cache:
                    self.cache.pop(key)
                self.cache[key] = (value, expiry)
                
            self.insertions += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
                
                # Also remove from frequency dict if LFU
                if self.eviction_policy == EvictionPolicy.LFU and key in self.frequency:
                    self.frequency.pop(key)
                    
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache"""
        with self.lock:
            self.cache.clear()
            if self.eviction_policy == EvictionPolicy.LFU:
                self.frequency.clear()
    
    def _evict(self) -> None:
        """Evict items based on eviction policy"""
        if not self.cache:
            return
            
        if self.eviction_policy == EvictionPolicy.LRU:
            # Evict least recently used (first item)
            self.cache.popitem(last=False)
            
        elif self.eviction_policy == EvictionPolicy.LFU:
            # Evict least frequently used
            min_freq = min(self.frequency.values())
            min_keys = [k for k, v in self.frequency.items() if v == min_freq]
            key_to_evict = min_keys[0]  # Take the first one
            
            # Remove from cache and frequency
            self.cache.pop(key_to_evict)
            self.frequency.pop(key_to_evict)
            
        elif self.eviction_policy == EvictionPolicy.FIFO:
            # Evict first in (first item)
            self.cache.popitem(last=False)
            
        elif self.eviction_policy == EvictionPolicy.TTL:
            # Evict based on TTL - find expired or closest to expiry
            now = time.time()
            
            # First try to find expired items
            for key, (_, expiry) in list(self.cache.items()):
                if expiry and now > expiry:
                    self.cache.pop(key)
                    self.evictions += 1
                    return
                    
            # If no expired items, evict closest to expiry
            closest_key = None
            closest_expiry = float('inf')
            
            for key, (_, expiry) in self.cache.items():
                if expiry and expiry < closest_expiry:
                    closest_key = key
                    closest_expiry = expiry
                    
            if closest_key:
                self.cache.pop(closest_key)
            else:
                # If no expiry times, fall back to FIFO
                self.cache.popitem(last=False)
                
        self.evictions += 1
    
    def cleanup(self) -> int:
        """
        Remove expired items
        
        Returns:
            Number of items removed
        """
        with self.lock:
            now = time.time()
            expired_keys = []
            
            # Find expired keys
            for key, (_, expiry) in self.cache.items():
                if expiry and now > expiry:
                    expired_keys.append(key)
                    
            # Remove expired keys
            for key in expired_keys:
                self.cache.pop(key)
                
                # Also remove from frequency dict if LFU
                if self.eviction_policy == EvictionPolicy.LFU and key in self.frequency:
                    self.frequency.pop(key)
                    
            return len(expired_keys)
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "insertions": self.insertions,
                "evictions": self.evictions,
                "hit_ratio": (self.hits / (self.hits + self.misses)) if (self.hits + self.misses) > 0 else 0
            }

class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, redis_url: Optional[str] = None, prefix: str = "cache"):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis URL (default: environment variable REDIS_URL)
            prefix: Prefix for cache keys
        """
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.prefix = prefix
        self.client = None
        self.connect()
        
    def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.client = redis.from_url(self.redis_url)
            self.client.ping()  # Test connection
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            self.client = None
            
    def _get_prefixed_key(self, key: str) -> str:
        """Get key with prefix"""
        return f"{self.prefix}:{key}"
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.client:
            return None
            
        try:
            prefixed_key = self._get_prefixed_key(key)
            data = self.client.get(prefixed_key)
            
            if not data:
                return None
                
            # Deserialize
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {str(e)}")
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            prefixed_key = self._get_prefixed_key(key)
            
            # Serialize
            data = pickle.dumps(value)
            
            # Set with TTL
            if ttl:
                self.client.setex(prefixed_key, ttl, data)
            else:
                self.client.set(prefixed_key, data)
                
            return True
        except Exception as e:
            logger.error(f"Error setting in Redis cache: {str(e)}")
            return False
            
    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.client:
            return False
            
        try:
            prefixed_key = self._get_prefixed_key(key)
            return bool(self.client.delete(prefixed_key))
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {str(e)}")
            return False
            
    def clear(self) -> bool:
        """
        Clear all items with prefix
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            # Get all keys with prefix
            pattern = f"{self.prefix}:*"
            keys = self.client.keys(pattern)
            
            if keys:
                self.client.delete(*keys)
                
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {str(e)}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.client:
            return {"error": "Not connected to Redis"}
            
        try:
            # Get all keys with prefix
            pattern = f"{self.prefix}:*"
            keys = self.client.keys(pattern)
            
            # Get memory usage
            memory_usage = sum(self.client.memory_usage(key) or 0 for key in keys)
            
            return {
                "size": len(keys),
                "memory_usage_bytes": memory_usage,
                "prefix": self.prefix
            }
        except Exception as e:
            logger.error(f"Error getting Redis cache stats: {str(e)}")
            return {"error": str(e)}

class FileCache:
    """File-based cache implementation"""
    
    def __init__(self, cache_dir: Optional[str] = None, serialization: str = SerializationMethod.COMPRESSED):
        """
        Initialize file cache
        
        Args:
            cache_dir: Directory to store cache files
            serialization: Serialization method
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "cache", "enhanced")
        self.serialization = serialization
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for key"""
        # Create a safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'rb') as f:
                data = f.read()
                
            # Parse metadata and value
            metadata_size = int.from_bytes(data[:4], byteorder='big')
            metadata_bytes = data[4:4+metadata_size]
            value_bytes = data[4+metadata_size:]
            
            # Deserialize metadata
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            # Check expiry
            if 'expiry' in metadata and metadata['expiry'] and time.time() > metadata['expiry']:
                # Expired - delete file
                os.remove(cache_path)
                return None
                
            # Deserialize value based on method
            if metadata.get('serialization') == SerializationMethod.JSON:
                value = json.loads(value_bytes.decode('utf-8'))
            elif metadata.get('serialization') == SerializationMethod.COMPRESSED:
                value = pickle.loads(zlib.decompress(value_bytes))
            else:  # PICKLE
                value = pickle.loads(value_bytes)
                
            return value
        except Exception as e:
            logger.error(f"Error reading from file cache: {str(e)}")
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)
        
        try:
            # Prepare metadata
            metadata = {
                'key': key,
                'created_at': time.time(),
                'serialization': self.serialization
            }
            
            # Add expiry if TTL provided
            if ttl:
                metadata['expiry'] = time.time() + ttl
                
            # Serialize metadata
            metadata_bytes = json.dumps(metadata).encode('utf-8')
            metadata_size = len(metadata_bytes)
            
            # Serialize value based on method
            if self.serialization == SerializationMethod.JSON:
                value_bytes = json.dumps(value).encode('utf-8')
            elif self.serialization == SerializationMethod.COMPRESSED:
                value_bytes = zlib.compress(pickle.dumps(value))
            else:  # PICKLE
                value_bytes = pickle.dumps(value)
                
            # Write to file
            with open(cache_path, 'wb') as f:
                # Write metadata size (4 bytes)
                f.write(metadata_size.to_bytes(4, byteorder='big'))
                # Write metadata
                f.write(metadata_bytes)
                # Write value
                f.write(value_bytes)
                
            return True
        except Exception as e:
            logger.error(f"Error writing to file cache: {str(e)}")
            return False
            
    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return False
            
        try:
            os.remove(cache_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting from file cache: {str(e)}")
            return False
            
    def clear(self) -> bool:
        """
        Clear all items
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.cache'):
                    os.remove(file_path)
                    
            return True
        except Exception as e:
            logger.error(f"Error clearing file cache: {str(e)}")
            return False
            
    def cleanup(self) -> int:
        """
        Remove expired items
        
        Returns:
            Number of items removed
        """
        count = 0
        
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.cache'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        
                    # Parse metadata and check expiry
                    metadata_size = int.from_bytes(data[:4], byteorder='big')
                    metadata_bytes = data[4:4+metadata_size]
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                    
                    # Check expiry
                    if 'expiry' in metadata and metadata['expiry'] and time.time() > metadata['expiry']:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    # If can't read properly, remove the file
                    os.remove(file_path)
                    count += 1
                    
            return count
        except Exception as e:
            logger.error(f"Error cleaning up file cache: {str(e)}")
            return count
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # Count cache files
            count = 0
            size_bytes = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    count += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    size_bytes += os.path.getsize(file_path)
                    
            return {
                "size": count,
                "storage_bytes": size_bytes,
                "cache_dir": self.cache_dir
            }
        except Exception as e:
            logger.error(f"Error getting file cache stats: {str(e)}")
            return {"error": str(e)}

class MultiTierCache:
    """Multi-tier cache implementation combining memory, Redis, and file caches"""
    
    def __init__(self, 
                memory_size: int = 10000,
                redis_url: Optional[str] = None,
                cache_dir: Optional[str] = None,
                enable_memory: bool = True,
                enable_redis: bool = True,
                enable_file: bool = True):
        """
        Initialize multi-tier cache
        
        Args:
            memory_size: Maximum items in memory cache
            redis_url: Redis URL
            cache_dir: Directory for file cache
            enable_memory: Whether to enable memory cache
            enable_redis: Whether to enable Redis cache
            enable_file: Whether to enable file cache
        """
        # Initialize caches based on configuration
        self.memory_cache = MemoryCache(max_size=memory_size) if enable_memory else None
        self.redis_cache = RedisCache(redis_url=redis_url) if enable_redis else None
        self.file_cache = FileCache(cache_dir=cache_dir) if enable_file else None
        
        # Track enabled backends
        self.backends = []
        if self.memory_cache:
            self.backends.append(CacheBackend.MEMORY)
        if self.redis_cache:
            self.backends.append(CacheBackend.REDIS)
        if self.file_cache:
            self.backends.append(CacheBackend.FILESYSTEM)
            
        logger.info(f"Multi-tier cache initialized with backends: {', '.join(self.backends)}")
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache, trying each tier in order
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Try memory cache first (fastest)
        if self.memory_cache:
            result = self.memory_cache.get(key)
            if result:
                value, _ = result
                return value
                
        # Try Redis next
        if self.redis_cache:
            value = self.redis_cache.get(key)
            if value is not None:
                # Add to memory cache if available
                if self.memory_cache:
                    # No TTL for memory cache to simplify (will be handled by cleanup)
                    self.memory_cache.set(key, value)
                return value
                
        # Try file cache last
        if self.file_cache:
            value = self.file_cache.get(key)
            if value is not None:
                # Add to faster caches
                if self.memory_cache:
                    self.memory_cache.set(key, value)
                if self.redis_cache:
                    self.redis_cache.set(key, value)
                return value
                
        # Not found in any cache
        return None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None, backends: Optional[List[str]] = None) -> None:
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds
            backends: Specific backends to use (default: all)
        """
        # Determine which backends to use
        backends_to_use = backends or self.backends
        
        # Set in each enabled backend
        if CacheBackend.MEMORY in backends_to_use and self.memory_cache:
            self.memory_cache.set(key, value, ttl)
            
        if CacheBackend.REDIS in backends_to_use and self.redis_cache:
            self.redis_cache.set(key, value, ttl)
            
        if CacheBackend.FILESYSTEM in backends_to_use and self.file_cache:
            self.file_cache.set(key, value, ttl)
            
    def delete(self, key: str) -> bool:
        """
        Delete item from all cache tiers
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted from any tier, False if not found
        """
        result = False
        
        # Delete from each enabled backend
        if self.memory_cache:
            result = self.memory_cache.delete(key) or result
            
        if self.redis_cache:
            result = self.redis_cache.delete(key) or result
            
        if self.file_cache:
            result = self.file_cache.delete(key) or result
            
        return result
        
    def clear(self) -> None:
        """Clear all cache tiers"""
        if self.memory_cache:
            self.memory_cache.clear()
            
        if self.redis_cache:
            self.redis_cache.clear()
            
        if self.file_cache:
            self.file_cache.clear()
            
    def cleanup(self) -> Dict[str, int]:
        """
        Clean up expired items in all tiers
        
        Returns:
            Dictionary with cleanup counts by tier
        """
        result = {}
        
        if self.memory_cache:
            result['memory'] = self.memory_cache.cleanup()
            
        if self.file_cache:
            result['file'] = self.file_cache.cleanup()
            
        # Redis handles TTL automatically
        
        return result
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get stats from all cache tiers
        
        Returns:
            Dictionary with stats by tier
        """
        stats = {
            "enabled_backends": self.backends
        }
        
        if self.memory_cache:
            stats['memory'] = self.memory_cache.get_stats()
            
        if self.redis_cache:
            stats['redis'] = self.redis_cache.get_stats()
            
        if self.file_cache:
            stats['file'] = self.file_cache.get_stats()
            
        return stats

class EnhancedCache:
    """
    Enhanced caching system with longer TTLs and smart cache invalidation
    
    Features:
    - Multi-tier caching (memory, Redis, filesystem)
    - Extended TTLs for stable data
    - Automatic tier selection based on data type
    - Support for cache tags and bulk invalidation
    - Semantic caching for similar requests
    """
    
    def __init__(self):
        """Initialize the enhanced cache system"""
        # Create multi-tier cache
        self.cache = MultiTierCache()
        
        # Map of cache tags to keys
        self.tag_to_keys = {}
        
        # For scheduled cleanup
        self.cleanup_interval = 3600  # 1 hour
        self.cleanup_timer = None
        self._schedule_cleanup()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        return self.cache.get(key)
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tier: str = CacheTier.DAILY, tags: Optional[List[str]] = None) -> None:
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (overrides tier)
            tier: Cache tier (determines TTL if not explicitly provided)
            tags: Optional tags for grouping and invalidation
        """
        # Determine TTL based on tier if not explicitly provided
        actual_ttl = ttl if ttl is not None else CacheTier.get_ttl(tier)
        
        # Choose storage backends based on tier
        backends = self._get_backends_for_tier(tier)
        
        # Store the value
        self.cache.set(key, value, actual_ttl, backends)
        
        # Store tags mapping
        if tags:
            for tag in tags:
                if tag not in self.tag_to_keys:
                    self.tag_to_keys[tag] = set()
                self.tag_to_keys[tag].add(key)
                
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a specific cache key
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if invalidated, False if not found
        """
        return self.cache.delete(key)
        
    def invalidate_tags(self, tags: List[str]) -> int:
        """
        Invalidate all cache entries with specific tags
        
        Args:
            tags: List of tags to invalidate
            
        Returns:
            Number of invalidated cache entries
        """
        keys_to_invalidate = set()
        
        for tag in tags:
            if tag in self.tag_to_keys:
                keys_to_invalidate.update(self.tag_to_keys[tag])
                self.tag_to_keys[tag] = set()  # Clear the tag mapping
                
        # Invalidate all collected keys
        count = 0
        for key in keys_to_invalidate:
            if self.cache.delete(key):
                count += 1
                
        return count
        
    def clear_all(self) -> None:
        """Clear the entire cache"""
        self.cache.clear()
        self.tag_to_keys = {}
        
    def _get_backends_for_tier(self, tier: str) -> List[str]:
        """
        Determine which backends to use for a specific tier
        
        Args:
            tier: Cache tier
            
        Returns:
            List of backend identifiers
        """
        if tier == CacheTier.PERMANENT:
            # Store permanent data in all tiers for maximum durability
            return [CacheBackend.MEMORY, CacheBackend.REDIS, CacheBackend.FILESYSTEM]
            
        elif tier == CacheTier.STABLE:
            # Store stable data in Redis and file
            return [CacheBackend.MEMORY, CacheBackend.REDIS, CacheBackend.FILESYSTEM]
            
        elif tier == CacheTier.DAILY:
            # Store daily data in memory and Redis
            return [CacheBackend.MEMORY, CacheBackend.REDIS]
            
        else:  # FREQUENT or VOLATILE
            # Store frequent/volatile data only in memory
            return [CacheBackend.MEMORY]
            
    def _schedule_cleanup(self) -> None:
        """Schedule periodic cache cleanup"""
        def cleanup_job():
            try:
                # Run cleanup on the cache
                cleanup_result = self.cache.cleanup()
                logger.info(f"Cache cleanup completed: {cleanup_result}")
                
                # Reschedule
                self._schedule_cleanup()
            except Exception as e:
                logger.error(f"Error during cache cleanup: {str(e)}")
                
        # Schedule the cleanup
        self.cleanup_timer = threading.Timer(self.cleanup_interval, cleanup_job)
        self.cleanup_timer.daemon = True
        self.cleanup_timer.start()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        stats = self.cache.get_stats()
        
        # Add tag stats
        stats['tags'] = {
            'count': len(self.tag_to_keys),
            'tagged_keys': sum(len(keys) for keys in self.tag_to_keys.values())
        }
        
        return stats
        
    def find_similar(self, query: str, threshold: float = 0.8) -> Optional[Any]:
        """
        Find a similar cached query response
        
        Args:
            query: Query to find similar cached responses for
            threshold: Similarity threshold (0-1)
            
        Returns:
            Cached value for similar query or None if not found
        """
        # Get all keys from memory cache (fastest to check)
        memory_cache = getattr(self.cache, 'memory_cache', None)
        if not memory_cache:
            return None
            
        # This requires access to internals of the memory cache
        cache_data = getattr(memory_cache, 'cache', {})
        
        best_match = None
        best_similarity = 0
        
        for key in cache_data.keys():
            # Only consider query keys
            if not key.startswith('query:'):
                continue
                
            # Remove prefix to get the cached query
            cached_query = key[6:]
            
            # Calculate similarity (very basic)
            similarity = self._calculate_similarity(query, cached_query)
            
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = key
                
        # If found a good match, return its value
        if best_match:
            logger.info(f"Found similar cached query with similarity {best_similarity:.2f}")
            return self.get(best_match)
            
        return None
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # This is a very simple implementation
        # For production, consider using more sophisticated methods
        
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
            
        return intersection / union

def cache_with_ttl(tier: str = CacheTier.DAILY, tags: Optional[List[str]] = None):
    """
    Decorator for caching function results with enhanced TTL
    
    Args:
        tier: Cache tier (determines TTL)
        tags: Optional tags for grouping and invalidation
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize cache if needed
            if not hasattr(wrapper, 'cache'):
                wrapper.cache = EnhancedCache()
                
            # Generate a cache key based on function name and arguments
            key_parts = [func.__name__]
            
            # Add args and kwargs to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    key_parts.append(str(arg))
                else:
                    # For complex objects, use their string representation
                    key_parts.append(str(type(arg)))
            
            # Sort kwargs by key for consistent cache keys
            sorted_kwargs = sorted(kwargs.items())
            for key, value in sorted_kwargs:
                if isinstance(value, (str, int, float, bool, type(None))):
                    key_parts.append(f"{key}={value}")
                else:
                    # For complex objects, use their type
                    key_parts.append(f"{key}={str(type(value))}")
                    
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = wrapper.cache.get(cache_key)
            if cached_value is not None:
                return cached_value
                
            # Not in cache, call the function
            result = func(*args, **kwargs)
            
            # Store in cache
            wrapper.cache.set(cache_key, result, tier=tier, tags=tags)
            
            return result
        return wrapper
    return decorator

def query_cache(tier: str = CacheTier.DAILY, similarity_threshold: float = 0.8):
    """
    Specialized decorator for caching query results with semantic similarity matching
    
    Args:
        tier: Cache tier (determines TTL)
        similarity_threshold: Threshold for considering queries similar
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(query, *args, **kwargs):
            # Initialize cache if needed
            if not hasattr(wrapper, 'cache'):
                wrapper.cache = EnhancedCache()
                
            # Generate a cache key
            cache_key = f"query:{query}"
            
            # Try to get exact match from cache
            cached_value = wrapper.cache.get(cache_key)
            if cached_value is not None:
                return cached_value
                
            # Try to find similar query
            similar_value = wrapper.cache.find_similar(query, similarity_threshold)
            if similar_value is not None:
                return similar_value
                
            # Not found in cache, call the function
            result = func(query, *args, **kwargs)
            
            # Store in cache
            wrapper.cache.set(cache_key, result, tier=tier)
            
            return result
        return wrapper
    return decorator

# Example usage
def example_usage():
    """Example of using the enhanced cache"""
    # Create cache
    cache = EnhancedCache()
    
    # Store values in different tiers
    cache.set("user:1", {"name": "John", "email": "john@example.com"}, tier=CacheTier.STABLE, tags=["user"])
    cache.set("user:2", {"name": "Jane", "email": "jane@example.com"}, tier=CacheTier.STABLE, tags=["user"])
    cache.set("stats:daily", {"visits": 1000, "conversions": 50}, tier=CacheTier.DAILY, tags=["stats"])
    cache.set("config:app", {"theme": "dark", "features": ["a", "b", "c"]}, tier=CacheTier.PERMANENT)
    
    # Retrieve values
    user1 = cache.get("user:1")
    stats = cache.get("stats:daily")
    
    print(f"User 1: {user1}")
    print(f"Stats: {stats}")
    
    # Invalidate by tag
    invalidated = cache.invalidate_tags(["user"])
    print(f"Invalidated {invalidated} entries with 'user' tag")
    
    # Check if invalidated
    user1_after = cache.get("user:1")
    print(f"User 1 after invalidation: {user1_after}")
    
    # Get stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Example with decorator
    @cache_with_ttl(tier=CacheTier.DAILY, tags=["calculation"])
    def expensive_calculation(x, y):
        print("Performing expensive calculation...")
        time.sleep(1)  # Simulate expensive operation
        return x * y
    
    # First call should calculate
    result1 = expensive_calculation(5, 10)
    print(f"Result 1: {result1}")
    
    # Second call should use cache
    result2 = expensive_calculation(5, 10)
    print(f"Result 2: {result2}")
    
    # Different arguments should calculate again
    result3 = expensive_calculation(7, 10)
    print(f"Result 3: {result3}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage() 