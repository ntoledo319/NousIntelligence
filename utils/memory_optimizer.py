"""
Memory Optimizer
Provides memory optimization utilities and monitoring
"""

import gc
import sys
import psutil
import logging
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Memory optimization and monitoring utility"""
    
    def __init__(self):
        self.memory_stats = {}
        self.gc_threshold = 100 * 1024 * 1024  # 100MB threshold for GC
    
    def monitor_memory_usage(self, function_name: str):
        """Decorator to monitor memory usage"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get memory before
                memory_before = self.get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Get memory after
                    memory_after = self.get_memory_usage()
                    memory_diff = memory_after - memory_before
                    
                    # Log significant memory increases
                    if memory_diff > 10 * 1024 * 1024:  # 10MB
                        logger.warning(f"Function {function_name} increased memory by {memory_diff / 1024 / 1024:.1f}MB")
                    
                    # Store statistics
                    if function_name not in self.memory_stats:
                        self.memory_stats[function_name] = {
                            'calls': 0,
                            'total_memory_increase': 0,
                            'avg_memory_increase': 0
                        }
                    
                    stats = self.memory_stats[function_name]
                    stats['calls'] += 1
                    stats['total_memory_increase'] += memory_diff
                    stats['avg_memory_increase'] = stats['total_memory_increase'] / stats['calls']
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Memory monitoring error in {function_name}: {e}")
                    raise
                    
            return wrapper
        return decorator
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': memory_percent,
                'available': psutil.virtual_memory().available,
                'total': psutil.virtual_memory().total
            }
        except Exception as e:
            logger.error(f"Could not get memory info: {e}")
            return {}
    
    def optimize_memory(self):
        """Perform memory optimization"""
        # Force garbage collection
        collected = gc.collect()
        
        # Get memory after optimization
        memory_after = self.get_memory_usage()
        
        logger.info(f"Memory optimization: collected {collected} objects, current usage: {memory_after / 1024 / 1024:.1f}MB")
        
        return {
            'objects_collected': collected,
            'current_memory_mb': memory_after / 1024 / 1024
        }
    
    def auto_optimize_memory(self):
        """Automatically optimize memory if threshold exceeded"""
        current_memory = self.get_memory_usage()
        if current_memory > self.gc_threshold:
            return self.optimize_memory()
        return None
    
    def clear_cache(self, cache_dict: Dict):
        """Clear cache dictionary safely"""
        if len(cache_dict) > 1000:  # Clear if cache gets too large
            cache_dict.clear()
            logger.info("Cache cleared due to size limit")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        current_info = self.get_memory_info()
        
        return {
            'current_memory': current_info,
            'function_stats': self.memory_stats,
            'gc_threshold_mb': self.gc_threshold / 1024 / 1024,
            'optimization_suggestions': self.get_optimization_suggestions()
        }
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get memory optimization suggestions"""
        suggestions = []
        
        current_memory = self.get_memory_usage()
        if current_memory > 500 * 1024 * 1024:  # >500MB
            suggestions.append("Consider reducing memory usage - current usage is high")
        
        high_memory_functions = [
            name for name, stats in self.memory_stats.items()
            if stats['avg_memory_increase'] > 50 * 1024 * 1024  # 50MB average
        ]
        
        if high_memory_functions:
            suggestions.append(f"Consider optimizing high-memory functions: {high_memory_functions}")
        
        return suggestions

# Global memory optimizer
memory_optimizer = MemoryOptimizer()

# Convenience decorators and functions
def monitor_memory(function_name: str):
    """Monitor memory usage decorator"""
    return memory_optimizer.monitor_memory_usage(function_name)

def optimize_memory():
    """Optimize memory usage"""
    return memory_optimizer.optimize_memory()

def auto_memory_check():
    """Automatically check and optimize memory"""
    return memory_optimizer.auto_optimize_memory()
