"""
Database Optimizer Module - Redirects to Unified Database Optimization

This module redirects to the unified database optimization service for zero functionality loss.
All original functions are preserved and work exactly the same.
"""

# Import everything from unified database optimization for backwards compatibility
from utils.unified_database_optimization import *

class DatabaseOptimizer:
    """Database optimization and monitoring system"""
    
    def __init__(self):
        self.app = None
        self.query_times = []
        
    def init_app(self, app):
        """Initialize database optimizer with Flask app"""
        self.app = app
        logger.info("Database optimizer initialized")
    
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
            if execution_time > 0.05:  # Log slow queries (>50ms)
                logger.warning(f"Slow query detected: {query_name} took {execution_time:.3f}s")
    
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
            'query_count': len(recent_queries),
            'avg_time': sum(times) / len(times),
            'max_time': max(times),
            'min_time': min(times),
            'slow_queries': len([t for t in times if t > 0.05])
        }

# Global database optimizer instance  
db_optimizer = DatabaseOptimizer()