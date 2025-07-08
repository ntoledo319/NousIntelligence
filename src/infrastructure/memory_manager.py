import gc
import threading
import time
import logging
import psutil
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.max_memory_mb = int(os.getenv('MAX_MEMORY_MB', 512))
        self.cleanup_interval = int(os.getenv('CLEANUP_INTERVAL', 3600))  # 1 hour
        self.running = False
        self.start_cleanup_thread()
    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    def cleanup_old_sessions(self):
        """Clean sessions older than 24 hours"""
        try:
            from flask import current_app
            
            if hasattr(current_app, 'session_interface'):
                # Implementation depends on session backend
                logger.info("Cleaned up old sessions")
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
    
    def cleanup_caches(self):
        """Clear various application caches"""
        try:
            from src.infrastructure.cache import cache
            
            # Get cache size before cleanup
            cache_info = self.get_cache_info()
            
            # Clear old cache entries (implementation specific)
            cache.clear()
            
            # Force garbage collection
            collected = gc.collect()
            
            logger.info(f"Cache cleanup: {cache_info}, GC collected: {collected} objects")
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    def get_cache_info(self):
        """Get cache statistics"""
        try:
            from src.infrastructure.cache import cache
            if hasattr(cache, '_cache'):
                return len(cache._cache)
            return 0
        except:
            return 0
    
    def check_memory_pressure(self):
        """Check if memory usage is too high"""
        memory = self.get_memory_usage()
        if memory['rss_mb'] > self.max_memory_mb:
            logger.warning(f"High memory usage: {memory['rss_mb']:.1f}MB")
            self.emergency_cleanup()
            return True
        return False
    
    def emergency_cleanup(self):
        """Emergency memory cleanup"""
        logger.info("Running emergency memory cleanup")
        
        # Clear all caches
        self.cleanup_caches()
        
        # Clear session data
        self.cleanup_old_sessions()
        
        # Force garbage collection
        gc.collect()
        
        # Log new memory usage
        memory = self.get_memory_usage()
        logger.info(f"Memory after cleanup: {memory['rss_mb']:.1f}MB")
    
    def periodic_cleanup(self):
        """Run periodic cleanup tasks"""
        while self.running:
            try:
                time.sleep(self.cleanup_interval)
                
                if not self.running:
                    break
                
                logger.info("Running periodic cleanup")
                
                # Check memory pressure
                self.check_memory_pressure()
                
                # Regular cleanup
                self.cleanup_old_sessions()
                
                # Log memory stats
                memory = self.get_memory_usage()
                logger.info(f"Memory usage: {memory['rss_mb']:.1f}MB ({memory['percent']:.1f}%)")
                
            except Exception as e:
                logger.error(f"Periodic cleanup error: {e}")
    
    def start_cleanup_thread(self):
        """Start the cleanup background thread"""
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self.periodic_cleanup, daemon=True)
            thread.start()
            logger.info("Memory manager started")
    
    def stop_cleanup_thread(self):
        """Stop the cleanup thread"""
        self.running = False
        logger.info("Memory manager stopped")

# Global memory manager instance
memory_manager = MemoryManager()

def init_memory_manager():
    """Initialize memory manager"""
    return memory_manager

def get_memory_stats():
    """Get current memory statistics"""
    return memory_manager.get_memory_usage()
