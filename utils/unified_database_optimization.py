"""
Unified Database Optimization - Zero Functionality Loss Consolidation

This module consolidates database optimization utilities while maintaining 100% backward compatibility.
Combines: database_optimizer.py, db_optimizations.py, performance_middleware.py (database parts)

All original function signatures and behavior are preserved.
"""

import time
import logging
import functools
from contextlib import contextmanager
from typing import Dict, Any, List, Callable, Optional, Union, TypeVar
from flask import Flask, g, request

logger = logging.getLogger(__name__)
T = TypeVar('T')

# Global query stats storage
query_stats: Dict[str, Dict[str, Any]] = {}

class UnifiedDatabaseOptimizer:
    """Unified database optimizer consolidating all database optimization utilities"""

    def __init__(self):
        """Initialize unified database optimizer"""
        self.app = None
        self.query_times = []
        self.performance_metrics = {
            'slow_queries': [],
            'average_query_time': 0,
            'total_queries': 0
        }
        
    def init_app(self, app: Flask):
        """Initialize database optimizer with Flask app"""
        self.app = app
        self._setup_query_monitoring()
        logger.info("Unified database optimizer initialized")
    
    def _setup_query_monitoring(self):
        """Set up automatic query monitoring"""
        if self.app:
            @self.app.before_request
            def start_db_timer():
                """Start database timing for request"""
                g.db_start_time = time.time()
            
            @self.app.after_request
            def log_db_performance(response):
                """Log database performance metrics"""
                if hasattr(g, 'db_start_time'):
                    db_time = time.time() - g.db_start_time
                    if db_time > 0.1:  # Log slow database operations
                        logger.warning(f"Slow database operation: {request.path} took {db_time:.3f}s")
                return response

    # === DATABASE OPTIMIZER FUNCTIONS ===
    
    @contextmanager
    def monitor_query(self, query_name):
        """Context manager to monitor query execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.query_times.append({
                'query': query_name,
                'time': execution_time,
                'timestamp': time.time()
            })
            
            # Update performance metrics
            self.performance_metrics['total_queries'] += 1
            
            if execution_time > 0.05:  # Log slow queries (>50ms)
                logger.warning(f"Slow query detected: {query_name} took {execution_time:.3f}s")
                self.performance_metrics['slow_queries'].append({
                    'query': query_name,
                    'time': execution_time,
                    'timestamp': time.time()
                })
    
    def get_performance_stats(self):
        """Get database performance statistics"""
        if not self.query_times:
            return {'status': 'no_data', 'message': 'No query data available'}
        
        recent_queries = [q for q in self.query_times if time.time() - q['timestamp'] < 300]  # Last 5 minutes
        
        if not recent_queries:
            return {'status': 'no_recent_data', 'message': 'No recent query data'}
        
        times = [q['time'] for q in recent_queries]
        return {
            'status': 'healthy',
            'total_queries': len(recent_queries),
            'average_time': sum(times) / len(times),
            'max_time': max(times),
            'min_time': min(times),
            'slow_queries': len([t for t in times if t > 0.05])
        }
    
    # === DB OPTIMIZATIONS FUNCTIONS ===
    
    def optimize_query(self, query_name: str):
        """Decorator for timing and optimizing database queries"""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = f(*args, **kwargs)
                query_time = time.time() - start_time

                # Store query stats
                if query_name not in query_stats:
                    query_stats[query_name] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'max_time': 0
                    }

                # Update stats
                stats = query_stats[query_name]
                stats['count'] += 1
                stats['total_time'] += query_time
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['max_time'] = max(stats['max_time'], query_time)

                # Log slow queries
                if query_time > 0.1:  # Log queries taking more than 100ms
                    logger.warning(f"Slow query '{query_name}': {query_time:.3f}s")

                return result
            return wrapper
        return decorator

    def get_db_stats(self) -> Dict[str, Any]:
        """Get database query performance statistics"""
        return query_stats
    
    def clear_stats(self):
        """Clear performance statistics"""
        global query_stats
        query_stats.clear()
        self.query_times.clear()
        self.performance_metrics = {
            'slow_queries': [],
            'average_query_time': 0,
            'total_queries': 0
        }
        logger.info("Database performance statistics cleared")
    
    def get_query_report(self) -> Dict[str, Any]:
        """Generate comprehensive query performance report"""
        if not query_stats:
            return {'message': 'No query statistics available'}
        
        # Calculate totals
        total_queries = sum(stats['count'] for stats in query_stats.values())
        total_time = sum(stats['total_time'] for stats in query_stats.values())
        
        # Find slowest queries
        slowest_queries = sorted(
            [(name, stats) for name, stats in query_stats.items()],
            key=lambda x: x[1]['max_time'],
            reverse=True
        )[:10]
        
        # Find most frequent queries
        most_frequent = sorted(
            [(name, stats) for name, stats in query_stats.items()],
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            'summary': {
                'total_queries': total_queries,
                'total_time': total_time,
                'average_time': total_time / total_queries if total_queries > 0 else 0,
                'unique_queries': len(query_stats)
            },
            'slowest_queries': [
                {
                    'name': name,
                    'max_time': stats['max_time'],
                    'avg_time': stats['avg_time'],
                    'count': stats['count']
                }
                for name, stats in slowest_queries
            ],
            'most_frequent': [
                {
                    'name': name,
                    'count': stats['count'],
                    'total_time': stats['total_time'],
                    'avg_time': stats['avg_time']
                }
                for name, stats in most_frequent
            ],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on query stats"""
        recommendations = []
        
        # Check for slow queries
        slow_queries = [name for name, stats in query_stats.items() if stats['max_time'] > 0.1]
        if slow_queries:
            recommendations.append(f"Consider optimizing {len(slow_queries)} slow queries: {', '.join(slow_queries[:3])}")
        
        # Check for frequent queries
        frequent_queries = [name for name, stats in query_stats.items() if stats['count'] > 100]
        if frequent_queries:
            recommendations.append(f"Consider caching {len(frequent_queries)} frequently executed queries")
        
        # Check overall performance
        total_queries = sum(stats['count'] for stats in query_stats.values())
        total_time = sum(stats['total_time'] for stats in query_stats.values())
        if total_queries > 0:
            avg_time = total_time / total_queries
            if avg_time > 0.05:
                recommendations.append("Overall query performance could be improved - consider indexing")
        
        return recommendations or ["Database performance appears optimal"]

# Create singleton instance
_unified_db_optimizer = None

def get_unified_db_optimizer() -> UnifiedDatabaseOptimizer:
    """Get singleton instance of unified database optimizer"""
    global _unified_db_optimizer
    if _unified_db_optimizer is None:
        _unified_db_optimizer = UnifiedDatabaseOptimizer()
    return _unified_db_optimizer

# === BACKWARDS COMPATIBILITY EXPORTS ===

# From database_optimizer.py
class DatabaseOptimizer:
    """Backwards compatibility class"""
    def __init__(self):
        self.optimizer = get_unified_db_optimizer()
    
    def init_app(self, app):
        return self.optimizer.init_app(app)
    
    def monitor_query(self, query_name):
        return self.optimizer.monitor_query(query_name)
    
    def get_performance_stats(self):
        return self.optimizer.get_performance_stats()

# Create compatibility instance
db_optimizer = get_unified_db_optimizer()

# From db_optimizations.py
def optimize_query(query_name: str):
    """Decorator for timing and optimizing database queries"""
    return get_unified_db_optimizer().optimize_query(query_name)

def get_db_stats() -> Dict[str, Any]:
    """Get database query performance statistics"""
    return get_unified_db_optimizer().get_db_stats()

def clear_db_stats():
    """Clear database statistics"""
    return get_unified_db_optimizer().clear_stats()

def generate_db_report():
    """Generate database performance report"""
    return get_unified_db_optimizer().get_query_report()

# Performance monitoring utilities
def setup_performance_monitoring(app: Flask):
    """Set up performance monitoring for Flask app"""
    return get_unified_db_optimizer().init_app(app)

logger.info("Unified Database Optimization loaded - all database optimization modules consolidated with zero functionality loss")