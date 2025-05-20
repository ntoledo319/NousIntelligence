"""
Cache Helper Utility

This module provides caching functionality for the NOUS personal assistant.
It helps improve performance by caching expensive operations.

@module utils.cache_helper
@description Caching utilities for performance optimization
"""

import logging
import time
import os
import json
from typing import Dict, Any, Callable, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)

class CacheHelper:
    """
    Provides caching functionality for the application
    """
    
    def __init__(self, cache_dir: str = 'cache'):
        """
        Initialize the cache helper
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.logger = logging.getLogger(__name__)
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        self.logger.info(f"Cache initialized with directory: {cache_dir}")
        
        # In-memory cache
        self.memory_cache: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Check memory cache first
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            
            # Check if expired
            if expiry is None or expiry > time.time():
                return value
            
            # Remove from memory cache if expired
            del self.memory_cache[key]
        
        # Check file cache
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    
                # Check if expired
                if 'expiry' in cache_data and cache_data['expiry'] is not None:
                    if cache_data['expiry'] < time.time():
                        # Remove expired cache file
                        os.remove(cache_path)
                        return None
                
                # Add to memory cache
                self.memory_cache[key] = (
                    cache_data['value'],
                    cache_data.get('expiry')
                )
                
                return cache_data['value']
            except Exception as e:
                self.logger.error(f"Error reading cache file {cache_path}: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiry)
        """
        expiry = None
        if ttl is not None:
            expiry = time.time() + ttl
        
        # Store in memory cache
        self.memory_cache[key] = (value, expiry)
        
        # Store in file cache
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'value': value,
                    'expiry': expiry
                }, f)
        except Exception as e:
            self.logger.error(f"Error writing cache file {cache_path}: {str(e)}")
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache
        
        Args:
            key: Cache key
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from file cache
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except Exception as e:
                self.logger.error(f"Error deleting cache file {cache_path}: {str(e)}")
    
    def clear_all(self) -> None:
        """Clear all cached values"""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear file cache
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            self.logger.error(f"Error clearing cache directory: {str(e)}")
            
    def warmup(self) -> None:
        """Preload frequently used cached data into memory"""
        self.logger.info("Warming up cache for frequently accessed data")
        
        try:
            # Load cache files into memory
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            
            # Prioritize most common accessed data
            common_prefixes = ['user_settings_', 'system_settings_', 'dashboard_stats_']
            priority_files = []
            
            for prefix in common_prefixes:
                priority_files.extend([f for f in cache_files if f.startswith(prefix)])
                
            # Limit to first 10 to avoid excessive loading
            for filename in priority_files[:10]:
                key = filename.replace('.json', '')
                self.get(key)  # This will load into memory cache
                
            self.logger.info(f"Cache warmup completed with {len(priority_files[:10])} items")
        except Exception as e:
            self.logger.error(f"Error during cache warmup: {str(e)}")

# Create a singleton instance
cache_helper = CacheHelper()

def cached(ttl: Optional[int] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (None for no expiry)
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Check cache
            cached_result = cache_helper.get(key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_helper.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator

def get_cache_helper() -> CacheHelper:
    """Get the singleton instance of CacheHelper"""
    return cache_helper 