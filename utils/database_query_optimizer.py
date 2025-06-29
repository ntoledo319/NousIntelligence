"""
Database Query Optimizer
Provides optimized database query patterns and performance monitoring
"""

import logging
from functools import wraps
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DatabaseQueryOptimizer:
    """Optimizer for database queries"""
    
    def __init__(self):
        self.query_stats = {}
        self.slow_query_threshold = 1.0  # seconds
    
    def monitor_query_performance(self, query_name: str):
        """Decorator to monitor query performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # Track query statistics
                    if query_name not in self.query_stats:
                        self.query_stats[query_name] = {
                            'total_calls': 0,
                            'total_time': 0.0,
                            'avg_time': 0.0,
                            'slow_queries': 0
                        }
                    
                    stats = self.query_stats[query_name]
                    stats['total_calls'] += 1
                    stats['total_time'] += execution_time
                    stats['avg_time'] = stats['total_time'] / stats['total_calls']
                    
                    if execution_time > self.slow_query_threshold:
                        stats['slow_queries'] += 1
                        logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    logger.error(f"Query {query_name} failed after {execution_time:.2f}s: {e}")
                    raise
                    
            return wrapper
        return decorator
    
    def optimize_pagination_query(self, query, page: int, per_page: int = 20):
        """Optimize pagination queries"""
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page)
    
    def optimize_join_query(self, query, *join_tables):
        """Optimize join queries with eager loading"""
        for table in join_tables:
            query = query.options(joinedload(table))
        return query
    
    def prevent_n_plus_one(self, query, *relationships):
        """Prevent N+1 query problems"""
        for relationship in relationships:
            query = query.options(selectinload(relationship))
        return query
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            'total_monitored_queries': len(self.query_stats),
            'query_stats': self.query_stats,
            'slow_query_threshold': self.slow_query_threshold
        }
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get list of slow queries"""
        slow_queries = []
        for query_name, stats in self.query_stats.items():
            if stats['slow_queries'] > 0:
                slow_queries.append({
                    'query_name': query_name,
                    'avg_time': stats['avg_time'],
                    'slow_count': stats['slow_queries'],
                    'total_calls': stats['total_calls']
                })
        return sorted(slow_queries, key=lambda x: x['avg_time'], reverse=True)

# Global query optimizer
db_optimizer = DatabaseQueryOptimizer()

# Convenience decorators
def monitor_query(query_name: str):
    """Monitor query performance"""
    return db_optimizer.monitor_query_performance(query_name)

def optimize_pagination(query, page: int, per_page: int = 20):
    """Optimize pagination"""
    return db_optimizer.optimize_pagination_query(query, page, per_page)
