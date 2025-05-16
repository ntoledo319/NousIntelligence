"""
Cache Helper Module for Improved Performance and Cost Efficiency

This module provides advanced caching mechanisms to reduce redundant AI API calls
and improve application performance. It supports multiple cache backends:
1. Redis (preferred for production)
2. Database (SQLAlchemy)
3. Local file system (fallback)

It implements intelligent caching strategies including:
- TTL-based expiration
- LRU (Least Recently Used) cache eviction
- Semantic similarity search for similar cached results
- Batch operation support for embeddings
- Automatic cache cleanup

@module: cache_helper
@author: NOUS Development Team
"""

import os
import json
import time
import logging
import hashlib
import pickle
import functools
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from collections import OrderedDict

# Configure module logger
logger = logging.getLogger(__name__)

# Attempt to load Redis (preferred caching method)
REDIS_AVAILABLE = False
try:
    import redis
    from redis.exceptions import RedisError
    
    # Try to connect to Redis if URL is available
    REDIS_URL = os.environ.get("REDIS_URL")
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()  # Test connection
        REDIS_AVAILABLE = True
        logger.info("Redis cache backend initialized successfully")
except (ImportError, RedisError) as e:
    logger.warning(f"Redis cache unavailable: {str(e)}")
    redis_client = None

# Try to use SQLAlchemy to get the database
DB_AVAILABLE = False
try:
    from app import db
    from sqlalchemy.exc import SQLAlchemyError
    DB_AVAILABLE = True
    logger.info("Database cache backend initialized successfully")
except ImportError:
    logger.warning("Cache helper couldn't import database, will try Redis or file cache")

# Define paths for file-based cache
CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Constants
DEFAULT_TTL = 7200  # Default TTL in seconds (2 hours, was 1 hour)
EMBEDDING_TTL = 604800  # Embedding cache TTL (7 days, was 24 hours)
CLEANUP_INTERVAL = 3600  # Cache cleanup interval (1 hour)
SIMILARITY_THRESHOLD = 0.90  # Threshold for semantic similarity cache hits (was 0.92)
MAX_CACHE_ENTRIES = 10000  # Maximum number of entries in memory cache

# In-memory LRU cache
class LRUCache:
    """Thread-safe LRU cache implementation"""
    def __init__(self, capacity: int = MAX_CACHE_ENTRIES):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Tuple[Any, datetime]]:
        """Get item from cache and move to end (most recently used)"""
        with self.lock:
            if key not in self.cache:
                return None
            value, expires_at = self.cache.pop(key)
            # Check if expired
            if expires_at and expires_at < datetime.utcnow():
                return None
            # Move to end (most recently used)
            self.cache[key] = (value, expires_at)
            return value, expires_at
            
    def put(self, key: str, value: Any, expires_at: Optional[datetime] = None) -> None:
        """Add item to cache, evicting least recently used if at capacity"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Evict least recently used item
                self.cache.popitem(last=False)
            self.cache[key] = (value, expires_at)
            
    def remove(self, key: str) -> bool:
        """Remove item from cache"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
                return True
            return False
            
    def clear(self) -> None:
        """Clear all items from cache"""
        with self.lock:
            self.cache.clear()
            
    def keys(self) -> List[str]:
        """Return all keys in cache"""
        with self.lock:
            return list(self.cache.keys())

# Initialize in-memory LRU cache
memory_cache = LRUCache(MAX_CACHE_ENTRIES)

def generate_cache_key(func, prefix: Optional[str] = None, *args, **kwargs) -> str:
    """
    Generate a cache key from function and arguments
    
    Args:
        func: The function being cached
        prefix: Optional prefix for the cache key
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function
        
    Returns:
        A string cache key
    """
    cache_key_parts = [func.__name__]
    
    # Add prefix if provided
    if prefix:
        cache_key_parts.insert(0, prefix)
    
    # Add args and kwargs to key
    for arg in args:
        if isinstance(arg, (str, int, float, bool, type(None))):
            cache_key_parts.append(str(arg))
        else:
            # For complex objects, use their string representation
            cache_key_parts.append(str(type(arg)))
    
    # Sort kwargs by key for consistent cache keys
    sorted_kwargs = sorted(kwargs.items())
    for key, value in sorted_kwargs:
        if isinstance(value, (str, int, float, bool, type(None))):
            cache_key_parts.append(f"{key}={value}")
        else:
            # For complex objects, use their type
            cache_key_parts.append(f"{key}={str(type(value))}")
            
    # Create the final cache key
    return ":".join(cache_key_parts)

# Import CacheEntry model if database is available
if DB_AVAILABLE:
    try:
        from models import CacheEntry
    except ImportError:
        # Create the model directly if it doesn't exist
        from sqlalchemy import Column, String, Text, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        
        Base = declarative_base()
        
        class CacheEntry(Base):
            """Model for storing cache entries in the database"""
            __tablename__ = 'cache_entries'
            
            key = Column(String(255), primary_key=True)
            value = Column(Text, nullable=False)
            expires_at = Column(DateTime, nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RedisCacheManager:
    """Redis-based cache manager for optimal performance"""
    
    @staticmethod
    def get(cache_key: str) -> Optional[Any]:
        """
        Get a value from the Redis cache
        
        Args:
            cache_key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        try:
            # Get the value from Redis
            data = redis_client.get(cache_key)
            if not data:
                return None
                
            # Deserialize using pickle for complex objects
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Error reading from Redis cache: {str(e)}")
            return None
    
    @staticmethod
    def set(cache_key: str, value: Any, ttl_seconds: int = DEFAULT_TTL) -> bool:
        """
        Set a value in the Redis cache
        
        Args:
            cache_key: The cache key to set
            value: The value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize using pickle for complex objects
            data = pickle.dumps(value)
            
            # Set in Redis with expiration
            redis_client.setex(cache_key, ttl_seconds, data)
            return True
        except Exception as e:
            logger.error(f"Error writing to Redis cache: {str(e)}")
            return False
    
    @staticmethod
    def delete(cache_key: str) -> bool:
        """
        Delete a value from the Redis cache
        
        Args:
            cache_key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {str(e)}")
            return False
    
    @staticmethod
    def clear_expired() -> bool:
        """
        Clear expired cache entries - Redis handles this automatically
        
        Returns:
            True always (Redis handles expiration automatically)
        """
        # Redis automatically expires keys, no need to do anything
        return True
    
    @staticmethod
    def get_keys_by_pattern(pattern: str) -> List[str]:
        """
        Get all Redis keys matching a pattern
        
        Args:
            pattern: Redis key pattern (e.g., "embedding:*")
            
        Returns:
            List of matching keys
        """
        try:
            # Get all matching keys
            keys = redis_client.keys(pattern)
            return [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            logger.error(f"Error getting Redis keys by pattern: {str(e)}")
            return []

class DatabaseCacheManager:
    """Database-backed cache manager"""
    
    @staticmethod
    def get(cache_key: str) -> Optional[Any]:
        """
        Get a value from the database cache
        
        Args:
            cache_key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        try:
            entry = CacheEntry.query.filter_by(key=cache_key).first()
            if not entry:
                return None
                
            # Check expiration
            if entry.expires_at and entry.expires_at < datetime.utcnow():
                # Delete expired entry
                db.session.delete(entry)
                db.session.commit()
                return None
                
            return json.loads(entry.value)
        except Exception as e:
            logger.error(f"Error reading from database cache: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def set(cache_key: str, value: Any, ttl_seconds: int = DEFAULT_TTL) -> bool:
        """
        Set a value in the database cache
        
        Args:
            cache_key: The cache key to set
            value: The value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value to JSON
            json_value = json.dumps(value)
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            # Check if entry exists
            entry = CacheEntry.query.filter_by(key=cache_key).first()
            if entry:
                # Update existing entry
                entry.value = json_value
                entry.expires_at = expires_at
                entry.updated_at = datetime.utcnow()
            else:
                # Create new entry
                entry = CacheEntry(
                    key=cache_key,
                    value=json_value,
                    expires_at=expires_at,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(entry)
                
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error writing to database cache: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def delete(cache_key: str) -> bool:
        """
        Delete a value from the database cache
        
        Args:
            cache_key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            entry = CacheEntry.query.filter_by(key=cache_key).first()
            if entry:
                db.session.delete(entry)
                db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting from database cache: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def clear_expired() -> bool:
        """
        Clear all expired cache entries
        
        Returns:
            True if successful, False otherwise
        """
        try:
            expired = CacheEntry.query.filter(
                CacheEntry.expires_at < datetime.utcnow()
            ).all()
            
            if expired:
                for entry in expired:
                    db.session.delete(entry)
                db.session.commit()
                logger.info(f"Cleared {len(expired)} expired database cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing expired database cache: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_keys_by_pattern(pattern: str) -> List[str]:
        """
        Get all database cache keys matching a pattern
        
        Args:
            pattern: SQL LIKE pattern (e.g., "embedding:%")
            
        Returns:
            List of matching keys
        """
        try:
            # Convert Redis-style pattern to SQL LIKE pattern
            sql_pattern = pattern.replace('*', '%')
            
            # Query database for matching keys
            entries = CacheEntry.query.filter(
                CacheEntry.key.like(sql_pattern)
            ).all()
            
            return [entry.key for entry in entries]
        except Exception as e:
            logger.error(f"Error getting database cache keys by pattern: {str(e)}")
            return []

class FileCacheManager:
    """File-based cache manager as fallback"""
    
    @staticmethod
    def get(cache_key: str) -> Optional[Any]:
        """
        Get a value from the file cache
        
        Args:
            cache_key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        try:
            # Generate a file path from the key
            file_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return None
                
            # Read the file
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Check expiration
            if 'expires_at' in data and data['expires_at'] < time.time():
                # Delete expired entry
                os.remove(file_path)
                return None
                
            return data['value']
        except Exception as e:
            logger.error(f"Error reading from file cache: {str(e)}")
            return None
    
    @staticmethod
    def set(cache_key: str, value: Any, ttl_seconds: int = DEFAULT_TTL) -> bool:
        """
        Set a value in the file cache
        
        Args:
            cache_key: The cache key to set
            value: The value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create safe filename from cache key
            safe_key = hashlib.md5(cache_key.encode()).hexdigest()
            file_path = os.path.join(CACHE_DIR, f"{safe_key}.json")
            
            # Prepare data
            data = {
                'key': cache_key,
                'value': value,
                'expires_at': time.time() + ttl_seconds,
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(data, f)
                
            return True
        except Exception as e:
            logger.error(f"Error writing to file cache: {str(e)}")
            return False
    
    @staticmethod
    def delete(cache_key: str) -> bool:
        """
        Delete a value from the file cache
        
        Args:
            cache_key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create safe filename from cache key
            safe_key = hashlib.md5(cache_key.encode()).hexdigest()
            file_path = os.path.join(CACHE_DIR, f"{safe_key}.json")
            
            # Delete file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return True
        except Exception as e:
            logger.error(f"Error deleting from file cache: {str(e)}")
            return False
    
    @staticmethod
    def clear_expired() -> bool:
        """
        Clear all expired cache entries
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cleared = 0
            current_time = time.time()
            
            # Check all cache files
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith(".json"):
                    file_path = os.path.join(CACHE_DIR, filename)
                    
                    # Read expiration time
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            
                        # Check if expired
                        if 'expires_at' in data and data['expires_at'] < current_time:
                            os.remove(file_path)
                            cleared += 1
                    except (json.JSONDecodeError, OSError) as e:
                        # Remove corrupt files
                        os.remove(file_path)
                        cleared += 1
            
            if cleared > 0:
                logger.info(f"Cleared {cleared} expired file cache entries")
            
            return True
        except Exception as e:
            logger.error(f"Error clearing expired file cache: {str(e)}")
            return False
    
    @staticmethod
    def get_keys_by_pattern(pattern: str) -> List[str]:
        """
        Get all file cache keys matching a pattern
        
        Args:
            pattern: Glob-style pattern (e.g., "embedding:*")
            
        Returns:
            List of matching keys
        """
        try:
            # List all cache files
            keys = []
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith(".json"):
                    file_path = os.path.join(CACHE_DIR, filename)
                    
                    # Read key from file
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            
                        # Check if key matches pattern
                        key = data.get('key', '')
                        if key.startswith(pattern.replace('*', '')):
                            keys.append(key)
                    except (json.JSONDecodeError, OSError):
                        pass
            
            return keys
        except Exception as e:
            logger.error(f"Error getting file cache keys by pattern: {str(e)}")
            return []

# Select the appropriate cache manager
if REDIS_AVAILABLE:
    CacheManager = RedisCacheManager
    logger.info("Using Redis cache manager")
elif DB_AVAILABLE:
    CacheManager = DatabaseCacheManager
    logger.info("Using database cache manager")
else:
    CacheManager = FileCacheManager
    logger.info("Using file-based cache manager")

def cache_result(ttl_seconds: int = DEFAULT_TTL, prefix: Optional[str] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl_seconds: Time to live in seconds
        prefix: Optional prefix for cache key
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a cache key from function name, args, and kwargs
            cache_key = generate_cache_key(func, prefix, *args, **kwargs)
            
            # Try memory cache first (fastest)
            mem_result = memory_cache.get(cache_key)
            if mem_result:
                value, _ = mem_result
                return value
                
            # Try Redis cache next
            if REDIS_AVAILABLE:
                redis_result = RedisCacheManager.get(cache_key)
                if redis_result is not None:
                    # Also store in memory cache for faster access next time
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
                    memory_cache.put(cache_key, redis_result, expires_at)
                    return redis_result
            
            # Try database cache
            if DB_AVAILABLE:
                db_result = DatabaseCacheManager.get(cache_key)
                if db_result is not None:
                    # Also store in memory cache for faster access next time
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
                    memory_cache.put(cache_key, db_result, expires_at)
                    
                    # Update Redis cache if available
                    if REDIS_AVAILABLE:
                        RedisCacheManager.set(cache_key, db_result, ttl_seconds)
                        
                    return db_result
            
            # Try file cache
            file_result = FileCacheManager.get(cache_key)
            if file_result is not None:
                # Also store in memory and other caches for faster access next time
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
                memory_cache.put(cache_key, file_result, expires_at)
                
                # Update Redis/DB cache if available
                if REDIS_AVAILABLE:
                    RedisCacheManager.set(cache_key, file_result, ttl_seconds)
                elif DB_AVAILABLE:
                    DatabaseCacheManager.set(cache_key, file_result, ttl_seconds)
                    
                return file_result
            
            # If not found in any cache, call function and cache result
            result = func(*args, **kwargs)
            
            # Skip caching None results
            if result is None:
                return None
                
            # Cache in memory
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            memory_cache.put(cache_key, result, expires_at)
            
            # Cache in persistent storage
            if REDIS_AVAILABLE:
                RedisCacheManager.set(cache_key, result, ttl_seconds)
            elif DB_AVAILABLE:
                DatabaseCacheManager.set(cache_key, result, ttl_seconds)
            else:
                FileCacheManager.set(cache_key, result, ttl_seconds)
                
            return result
        return wrapper
    return decorator

def get_cached_embedding(text: str, model: str = "BAAI/bge-small-en-v1.5") -> Optional[List[float]]:
    """
    Get cached embedding for text if available
    
    Args:
        text: The text to get embedding for
        model: The model name used for embedding
        
    Returns:
        The embedding as a list of floats, or None if not cached
    """
    # Normalize text to ensure consistent caching
    normalized_text = text.strip().lower()
    
    # Generate a cache key
    cache_key = f"embedding:{model}:{hashlib.md5(normalized_text.encode()).hexdigest()}"
    
    # Try memory cache first (fastest)
    mem_result = memory_cache.get(cache_key)
    if mem_result:
        value, _ = mem_result
        logger.debug(f"Memory cache hit for embedding")
        return value
    
    # Try backend caches
    # If Redis is available, try it first
    if REDIS_AVAILABLE:
        embedding = RedisCacheManager.get(cache_key)
        if embedding is not None:
            # Also store in memory cache
            expires_at = datetime.utcnow() + timedelta(seconds=EMBEDDING_TTL)
            memory_cache.put(cache_key, embedding, expires_at)
            return embedding
            
    # Try database cache
    if DB_AVAILABLE:
        embedding = DatabaseCacheManager.get(cache_key)
        if embedding is not None:
            # Store in memory cache
            expires_at = datetime.utcnow() + timedelta(seconds=EMBEDDING_TTL)
            memory_cache.put(cache_key, embedding, expires_at)
            # Also update Redis if available
            if REDIS_AVAILABLE:
                RedisCacheManager.set(cache_key, embedding, EMBEDDING_TTL)
            return embedding
            
    # Try file cache
    embedding = FileCacheManager.get(cache_key)
    if embedding is not None:
        # Store in memory cache
        expires_at = datetime.utcnow() + timedelta(seconds=EMBEDDING_TTL)
        memory_cache.put(cache_key, embedding, expires_at)
        # Also update Redis/DB if available
        if REDIS_AVAILABLE:
            RedisCacheManager.set(cache_key, embedding, EMBEDDING_TTL)
        elif DB_AVAILABLE:
            DatabaseCacheManager.set(cache_key, embedding, EMBEDDING_TTL)
        return embedding
            
    # If not in any cache, try to find a similar embedding
    return find_similar_embedding(normalized_text, model)

def store_cached_embedding(text: str, embedding: List[float], model: str = "BAAI/bge-small-en-v1.5", ttl_seconds: int = EMBEDDING_TTL) -> bool:
    """
    Store embedding in cache
    
    Args:
        text: The text the embedding is for
        embedding: The embedding as a list of floats
        model: The model name used for embedding
        ttl_seconds: Time to live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    # Normalize text to ensure consistent caching
    normalized_text = text.strip().lower()
    
    # Generate a cache key
    cache_key = f"embedding:{model}:{hashlib.md5(normalized_text.encode()).hexdigest()}"
    
    # Store in memory cache
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    memory_cache.put(cache_key, embedding, expires_at)
    
    # Store in Redis if available
    if REDIS_AVAILABLE:
        return RedisCacheManager.set(cache_key, embedding, ttl_seconds)
    # Otherwise store in database if available
    elif DB_AVAILABLE:
        return DatabaseCacheManager.set(cache_key, embedding, ttl_seconds)
    # Otherwise store in file cache
    else:
        return FileCacheManager.set(cache_key, embedding, ttl_seconds)

def vector_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (0-1, higher is more similar)
    """
    import numpy as np
    # Convert to numpy arrays if not already
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    # Return cosine similarity
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

def find_similar_embedding(text: str, model: str) -> Optional[List[float]]:
    """
    Find a similar cached embedding using semantic similarity
    
    Args:
        text: The text to find similar embedding for
        model: The model name used for embedding
        
    Returns:
        The most similar embedding as a list of floats, or None if no similar embedding found
    """
    import numpy as np
    
    # We need the huggingface_helper to compute an embedding for comparison
    try:
        from utils.huggingface_helper import compute_embedding
    except ImportError:
        logger.warning("huggingface_helper not available, cannot find similar embeddings")
        return None
        
    try:
        # Compute embedding for the input text (temporary, not stored)
        current_embedding = compute_embedding(text, model)
        
        if not current_embedding:
            return None
            
        # Get all embedding keys to check for similarity
        pattern = f"embedding:{model}:*"
        
        # Try to get keys from each cache
        embedding_keys = []
        
        if REDIS_AVAILABLE:
            embedding_keys = RedisCacheManager.get_keys_by_pattern(pattern)
        elif DB_AVAILABLE:
            embedding_keys = DatabaseCacheManager.get_keys_by_pattern(pattern)
        else:
            embedding_keys = FileCacheManager.get_keys_by_pattern(pattern)
            
        if not embedding_keys:
            return None
            
        # Track the best match
        best_similarity = 0.0
        best_embedding = None
        
        # Batch process embeddings for efficiency (up to 50 at a time)
        batch_size = 50
        
        for i in range(0, len(embedding_keys), batch_size):
            batch_keys = embedding_keys[i:i+batch_size]
            batch_embeddings = []
            
            # Retrieve embeddings for this batch
            for key in batch_keys:
                if REDIS_AVAILABLE:
                    emb = RedisCacheManager.get(key)
                elif DB_AVAILABLE:
                    emb = DatabaseCacheManager.get(key)
                else:
                    emb = FileCacheManager.get(key)
                    
                if emb is not None:
                    batch_embeddings.append((key, emb))
            
            # Calculate similarities for this batch
            for key, cached_emb in batch_embeddings:
                similarity = vector_similarity(current_embedding, cached_emb)
                
                if similarity > best_similarity and similarity >= SIMILARITY_THRESHOLD:
                    best_similarity = similarity
                    best_embedding = cached_emb
                    
        if best_embedding is not None:
            logger.info(f"Found similar embedding with similarity: {best_similarity:.4f}")
            return best_embedding
            
        return None
    except Exception as e:
        logger.error(f"Error finding similar embedding: {str(e)}")
        return None

def batch_cache_operations(operation: str, items: List[Tuple[str, Any, int]]) -> Dict[str, bool]:
    """
    Perform batch cache operations
    
    Args:
        operation: The operation to perform ('set' or 'delete')
        items: List of (key, value, ttl) tuples for 'set' or list of keys for 'delete'
        
    Returns:
        Dictionary of {key: success} results
    """
    results = {}
    
    if operation == 'set':
        for key, value, ttl in items:
            results[key] = CacheManager.set(key, value, ttl)
    elif operation == 'delete':
        for key in items:
            results[key] = CacheManager.delete(key)
    
    return results

def schedule_cache_cleanup() -> None:
    """Schedule periodic cache cleanup in a background thread"""
    
    def cleanup_job() -> None:
        """Cleanup job to run periodically"""
        while True:
            try:
                logger.info("Running scheduled cache cleanup")
                CacheManager.clear_expired()
                
                # Sleep for the cleanup interval
                time.sleep(CLEANUP_INTERVAL)
            except Exception as e:
                logger.error(f"Error in cache cleanup job: {str(e)}")
                # Sleep and try again
                time.sleep(60)
    
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_job, daemon=True)
    cleanup_thread.start()
    logger.info("Cache cleanup thread started")

def clear_caches() -> bool:
    """
    Clear all caches
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if REDIS_AVAILABLE:
            # For Redis, clear all keys with a pattern
            keys = redis_client.keys("*")
            if keys:
                redis_client.delete(*keys)
        elif DB_AVAILABLE:
            # For database, delete all entries
            CacheEntry.query.delete()
            db.session.commit()
        else:
            # For file cache, delete all files
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith(".json"):
                    os.remove(os.path.join(CACHE_DIR, filename))
        
        logger.info("All caches cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing caches: {str(e)}")
        if DB_AVAILABLE:
            db.session.rollback()
        return False

# Start the cache cleanup scheduler
if not os.environ.get("DISABLE_CACHE_CLEANUP"):
    schedule_cache_cleanup()