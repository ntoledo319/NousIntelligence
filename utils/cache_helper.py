"""
Cache Helper module for improved cost efficiency
Provides caching mechanisms to reduce redundant AI API calls
"""

import os
import json
import time
import logging
import hashlib
import functools
from datetime import datetime, timedelta

# Try to use SQLAlchemy to get the database
try:
    from app import db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logging.warning("Cache helper couldn't import database, will use local file cache")

# Define paths for file-based cache
CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Cache models
if DB_AVAILABLE:
    from models import CacheEntry

    class CacheManager:
        """Database-backed cache manager"""
        
        @staticmethod
        def get(cache_key):
            """Get a value from the cache"""
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
                logging.error(f"Error reading from cache: {str(e)}")
                return None
        
        @staticmethod
        def set(cache_key, value, ttl_seconds=3600):
            """Set a value in the cache"""
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
                logging.error(f"Error writing to cache: {str(e)}")
                db.session.rollback()
                return False
                
        @staticmethod
        def delete(cache_key):
            """Delete a value from the cache"""
            try:
                entry = CacheEntry.query.filter_by(key=cache_key).first()
                if entry:
                    db.session.delete(entry)
                    db.session.commit()
                return True
            except Exception as e:
                logging.error(f"Error deleting from cache: {str(e)}")
                db.session.rollback()
                return False
                
        @staticmethod
        def clear_expired():
            """Clear all expired cache entries"""
            try:
                expired = CacheEntry.query.filter(
                    CacheEntry.expires_at < datetime.utcnow()
                ).all()
                
                if expired:
                    for entry in expired:
                        db.session.delete(entry)
                    db.session.commit()
                    logging.info(f"Cleared {len(expired)} expired cache entries")
                return True
            except Exception as e:
                logging.error(f"Error clearing expired cache: {str(e)}")
                db.session.rollback()
                return False

else:
    class FileCacheManager:
        """File-based cache manager as fallback"""
        
        @staticmethod
        def get(cache_key):
            """Get a value from the file cache"""
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
                logging.error(f"Error reading from file cache: {str(e)}")
                return None
        
        @staticmethod
        def set(cache_key, value, ttl_seconds=3600):
            """Set a value in the file cache"""
            try:
                # Generate a file path from the key
                file_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
                
                # Prepare data
                data = {
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
                logging.error(f"Error writing to file cache: {str(e)}")
                return False
                
        @staticmethod
        def delete(cache_key):
            """Delete a value from the file cache"""
            try:
                # Generate a file path from the key
                file_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
                
                # Delete file if it exists
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                return True
            except Exception as e:
                logging.error(f"Error deleting from file cache: {str(e)}")
                return False
                
        @staticmethod
        def clear_expired():
            """Clear all expired cache entries"""
            try:
                cleared = 0
                current_time = time.time()
                
                # Check all cache files
                for filename in os.listdir(CACHE_DIR):
                    if filename.endswith(".json"):
                        file_path = os.path.join(CACHE_DIR, filename)
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                
                            # Check expiration
                            if 'expires_at' in data and data['expires_at'] < current_time:
                                os.remove(file_path)
                                cleared += 1
                        except Exception:
                            # If file is corrupted, delete it
                            os.remove(file_path)
                            cleared += 1
                            
                if cleared > 0:
                    logging.info(f"Cleared {cleared} expired file cache entries")
                return True
            except Exception as e:
                logging.error(f"Error clearing expired file cache: {str(e)}")
                return False

    # Use the file-based cache manager
    CacheManager = FileCacheManager


def cache_result(ttl_seconds=3600, prefix=None):
    """
    Decorator to cache function results to reduce redundant API calls
    
    Args:
        ttl_seconds (int): Time-to-live in seconds
        prefix (str, optional): Custom prefix for cache key
        
    Returns:
        function: Decorated function with caching
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a cache key from function name, args, and kwargs
            key_parts = [func.__name__]
            
            # Add custom prefix if provided
            if prefix:
                key_parts.insert(0, prefix)
                
            # Add args and kwargs to key
            for arg in args:
                key_parts.append(str(arg))
            
            for key, value in sorted(kwargs.items()):
                key_parts.append(f"{key}={value}")
                
            # Create an MD5 hash of the key
            key_string = ":".join(key_parts)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                logging.info(f"Cache hit for {func.__name__}")
                return cached_result
                
            # If not in cache, call the function
            logging.info(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            
            # Store in cache if result is not None
            if result is not None:
                CacheManager.set(cache_key, result, ttl_seconds)
                
            return result
        return wrapper
    return decorator

# Periodically clear expired cache entries
def schedule_cache_cleanup():
    """Schedule periodic cleanup of expired cache entries"""
    import threading
    
    def cleanup_job():
        while True:
            try:
                CacheManager.clear_expired()
            except Exception as e:
                logging.error(f"Error in cache cleanup job: {str(e)}")
            
            # Sleep for 1 hour before next cleanup
            time.sleep(3600)
    
    # Start cleanup thread
    threading.Thread(target=cleanup_job, daemon=True).start()
    logging.info("Scheduled cache cleanup job")

# Initialize cache cleanup on module import
schedule_cache_cleanup()