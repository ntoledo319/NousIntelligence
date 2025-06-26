"""
Unit tests for the cache_helper module

These tests verify the functionality of caching features including:
- In-memory LRU cache
- Cache key generation
- Cache TTL handling

@module: test_cache_helper
@author: NOUS Development Team
"""
import unittest
import sys
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cache_helper import (
    LRUCache,
    generate_cache_key,
    memory_cache
)

class TestLRUCache(unittest.TestCase):
    """Test cases for LRU Cache functionality"""
    
    def setUp(self):
        """Set up a fresh cache for each test"""
        self.cache = LRUCache(capacity=3)  # Small capacity for testing
    
    def test_put_and_get(self):
        """Test basic put and get operations"""
        self.cache.put("key1", "value1")
        result = self.cache.get("key1")
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "value1")
    
    def test_get_nonexistent(self):
        """Test get with non-existent key"""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)
    
    def test_capacity_limit(self):
        """Test that LRU eviction works when capacity is reached"""
        # Fill cache to capacity
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        self.cache.put("key3", "value3")
        
        # All keys should be present
        self.assertIsNotNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key3"))
        
        # Add one more item, should evict the least recently used (key1)
        self.cache.put("key4", "value4")
        
        # key1 should be evicted, others remain
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key3"))
        self.assertIsNotNone(self.cache.get("key4"))
    
    def test_lru_order_maintained(self):
        """Test that LRU order is maintained when items are accessed"""
        # Fill cache
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        self.cache.put("key3", "value3")
        
        # Access key1, making key2 the least recently used
        self.cache.get("key1")
        
        # Add new item, should evict key2
        self.cache.put("key4", "value4")
        
        # key2 should be evicted, others remain
        self.assertIsNotNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key3"))
        self.assertIsNotNone(self.cache.get("key4"))
    
    def test_expiration(self):
        """Test that expired items are not returned"""
        # Add item that expires in the past
        past_time = datetime.utcnow() - timedelta(seconds=10)
        self.cache.put("expired_key", "expired_value", past_time)
        
        # Add non-expiring item
        self.cache.put("valid_key", "valid_value")
        
        # Expired item should not be returned
        self.assertIsNone(self.cache.get("expired_key"))
        
        # Valid item should be returned
        self.assertIsNotNone(self.cache.get("valid_key"))
    
    def test_remove(self):
        """Test removal of items from cache"""
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        # Remove key1
        removed = self.cache.remove("key1")
        self.assertTrue(removed)
        
        # key1 should be gone, key2 remains
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
        
        # Attempt to remove non-existent key
        removed = self.cache.remove("nonexistent")
        self.assertFalse(removed)
    
    def test_clear(self):
        """Test clearing the entire cache"""
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        # Clear cache
        self.cache.clear()
        
        # All keys should be gone
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_keys(self):
        """Test getting all keys from cache"""
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        keys = self.cache.keys()
        self.assertEqual(len(keys), 2)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)

class TestCacheKeyGeneration(unittest.TestCase):
    """Test cases for cache key generation"""
    
    def test_simple_args(self):
        """Test key generation with simple arguments"""
        def test_func(a, b):
            pass
        
        key = generate_cache_key(test_func, None, "arg1", 42)
        self.assertIn("test_func", key)
        self.assertIn("arg1", key)
        self.assertIn("42", key)
    
    def test_with_prefix(self):
        """Test key generation with a prefix"""
        def test_func():
            pass
        
        key = generate_cache_key(test_func, "prefix")
        self.assertTrue(key.startswith("prefix"))
    
    def test_with_kwargs(self):
        """Test key generation with keyword arguments"""
        def test_func(a=1, b=2):
            pass
        
        key = generate_cache_key(test_func, None, a="value", b=123)
        self.assertIn("a=value", key)
        self.assertIn("b=123", key)
    
    def test_complex_objects(self):
        """Test key generation with complex objects"""
        def test_func(obj):
            pass
        
        class TestClass:
            pass
        
        obj = TestClass()
        key = generate_cache_key(test_func, None, obj)
        
        # Should include the type of the object, not the object itself
        self.assertIn("TestClass", key)

if __name__ == '__main__':
    unittest.main() 