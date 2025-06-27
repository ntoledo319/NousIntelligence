"""
Database Optimization and Query Analysis
Automatically analyzes queries, suggests indexes, and optimizes performance
"""
import os
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database performance optimization and monitoring"""
    
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self.slow_query_threshold = 100  # ms
        self.query_log = []
        self.performance_metrics = {}
        
        if self.db_url:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
    
    def execute_with_timing(self, query, params=None):
        """Execute query with performance timing"""
        if not self.db_url:
            raise Exception("Database URL not configured")
        
        session = self.Session()
        start_time = time.time()
        
        try:
            result = session.execute(text(query), params or {})
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Log slow queries
            if execution_time_ms > self.slow_query_threshold:
                self._log_slow_query(query, execution_time_ms, params)
            
            # Record metrics
            self._record_query_metric(query, execution_time_ms)
            
            return result, execution_time_ms
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Query failed in {execution_time_ms:.2f}ms: {str(e)}")
            raise
            
        finally:
            session.close()
    
    def analyze_query_performance(self, query, params=None):
        """Analyze query performance with EXPLAIN"""
        if not self.db_url:
            return {"error": "Database not configured"}
        
        session = self.Session()
        
        try:
            # Run EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = session.execute(text(explain_query), params or {})
            explain_data = result.fetchone()[0]
            
            analysis = self._parse_explain_output(explain_data)
            suggestions = self._generate_optimization_suggestions(query, explain_data)
            
            return {
                "query": query,
                "execution_plan": explain_data,
                "analysis": analysis,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Query analysis failed: {str(e)}")
            return {"error": str(e)}
            
        finally:
            session.close()
    
    def suggest_indexes(self):
        """Analyze slow queries and suggest indexes"""
        suggestions = []
        
        # Analyze query patterns from slow query log
        for query_log in self.query_log:
            if query_log['execution_time_ms'] > self.slow_query_threshold:
                index_suggestions = self._analyze_query_for_indexes(query_log['query'])
                suggestions.extend(index_suggestions)
        
        # Remove duplicates
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            if suggestion['index_sql'] not in seen:
                unique_suggestions.append(suggestion)
                seen.add(suggestion['index_sql'])
        
        return unique_suggestions
    
    def optimize_connection_pool(self):
        """Optimize database connection pool settings"""
        if not self.db_url:
            return {"error": "Database not configured"}
        
        recommendations = {
            "current_settings": {},
            "recommendations": [],
            "optimized_config": {}
        }
        
        try:
            # Get current pool settings
            engine_info = {
                "pool_size": getattr(self.engine.pool, 'size', lambda: 'unknown')(),
                "max_overflow": getattr(self.engine.pool, 'overflow', 'unknown'),
                "pool_timeout": getattr(self.engine.pool, 'timeout', 'unknown'),
                "pool_recycle": getattr(self.engine, 'pool_recycle', 'unknown')
            }
            
            recommendations["current_settings"] = engine_info
            
            # Generate recommendations
            recommendations["recommendations"] = [
                "Set pool_size to min(2, max_connections/4) for optimal resource usage",
                "Set max_overflow to pool_size for connection bursts",
                "Set pool_recycle to 3600 seconds to prevent stale connections",
                "Set pool_pre_ping=True to validate connections before use",
                "Monitor connection pool metrics regularly"
            ]
            
            # Optimized configuration
            recommendations["optimized_config"] = {
                "pool_size": 2,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "pool_pre_ping": True
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Pool optimization analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def create_performance_report(self):
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "database_health": self._get_database_health(),
            "query_performance": self._get_query_performance_summary(),
            "slow_queries": self._get_slow_queries_summary(),
            "index_suggestions": self.suggest_indexes(),
            "connection_pool": self.optimize_connection_pool(),
            "recommendations": self._get_performance_recommendations()
        }
        
        return report
    
    def _log_slow_query(self, query, execution_time_ms, params):
        """Log slow query for analysis"""
        self.query_log.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "execution_time_ms": execution_time_ms,
            "params": params
        })
        
        # Keep only last 100 slow queries
        if len(self.query_log) > 100:
            self.query_log = self.query_log[-100:]
    
    def _record_query_metric(self, query, execution_time_ms):
        """Record query performance metrics"""
        query_type = self._get_query_type(query)
        
        if query_type not in self.performance_metrics:
            self.performance_metrics[query_type] = {
                "count": 0,
                "total_time_ms": 0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0,
                "avg_time_ms": 0
            }
        
        metrics = self.performance_metrics[query_type]
        metrics["count"] += 1
        metrics["total_time_ms"] += execution_time_ms
        metrics["min_time_ms"] = min(metrics["min_time_ms"], execution_time_ms)
        metrics["max_time_ms"] = max(metrics["max_time_ms"], execution_time_ms)
        metrics["avg_time_ms"] = metrics["total_time_ms"] / metrics["count"]
    
    def _parse_explain_output(self, explain_data):
        """Parse EXPLAIN output for key insights"""
        if not explain_data or not isinstance(explain_data, list):
            return {}
        
        plan = explain_data[0].get("Plan", {})
        
        analysis = {
            "total_cost": plan.get("Total Cost", 0),
            "actual_time": plan.get("Actual Total Time", 0),
            "rows_returned": plan.get("Actual Rows", 0),
            "node_type": plan.get("Node Type", ""),
            "scan_type": "sequential" if "Seq Scan" in plan.get("Node Type", "") else "indexed",
            "uses_index": "Index" in plan.get("Node Type", ""),
            "expensive_operations": []
        }
        
        # Check for expensive operations
        if plan.get("Total Cost", 0) > 1000:
            analysis["expensive_operations"].append("High cost query")
        
        if plan.get("Actual Total Time", 0) > 100:
            analysis["expensive_operations"].append("Slow execution")
        
        if "Seq Scan" in plan.get("Node Type", ""):
            analysis["expensive_operations"].append("Sequential scan")
        
        return analysis
    
    def _generate_optimization_suggestions(self, query, explain_data):
        """Generate optimization suggestions based on EXPLAIN output"""
        suggestions = []
        
        if not explain_data or not isinstance(explain_data, list):
            return suggestions
        
        plan = explain_data[0].get("Plan", {})
        
        # Sequential scan suggestions
        if "Seq Scan" in plan.get("Node Type", ""):
            suggestions.append({
                "type": "index",
                "priority": "high",
                "description": "Consider adding an index to avoid sequential scan",
                "action": "Analyze WHERE clauses and add appropriate indexes"
            })
        
        # High cost suggestions
        if plan.get("Total Cost", 0) > 1000:
            suggestions.append({
                "type": "optimization",
                "priority": "medium",
                "description": "Query has high cost, consider optimization",
                "action": "Review query logic and consider breaking into smaller queries"
            })
        
        # Slow execution suggestions
        if plan.get("Actual Total Time", 0) > 100:
            suggestions.append({
                "type": "performance",
                "priority": "high",
                "description": "Query execution is slow",
                "action": "Add indexes, optimize WHERE clauses, or consider query rewrite"
            })
        
        return suggestions
    
    def _analyze_query_for_indexes(self, query):
        """Analyze query and suggest specific indexes"""
        suggestions = []
        query_lower = query.lower()
        
        # Simple pattern matching for common cases
        # This is a basic implementation - could be enhanced with proper SQL parsing
        
        # Look for WHERE clauses
        if "where" in query_lower:
            # Extract table name (basic implementation)
            tables = self._extract_table_names(query)
            for table in tables:
                suggestions.append({
                    "table": table,
                    "type": "WHERE clause optimization",
                    "index_sql": f"CREATE INDEX IF NOT EXISTS idx_{table}_optimized ON {table} (/* columns from WHERE clause */)",
                    "description": f"Add index on {table} for WHERE clause optimization"
                })
        
        # Look for JOIN operations
        if "join" in query_lower:
            suggestions.append({
                "type": "JOIN optimization",
                "index_sql": "-- Add indexes on JOIN columns",
                "description": "Consider indexes on columns used in JOIN conditions"
            })
        
        # Look for ORDER BY
        if "order by" in query_lower:
            suggestions.append({
                "type": "ORDER BY optimization",
                "index_sql": "-- Add index on ORDER BY columns",
                "description": "Consider composite index including ORDER BY columns"
            })
        
        return suggestions
    
    def _extract_table_names(self, query):
        """Extract table names from query (basic implementation)"""
        # This is a simplified implementation
        # In production, use a proper SQL parser
        tables = []
        query_lower = query.lower()
        
        # Look for FROM clause
        if "from" in query_lower:
            words = query_lower.split()
            try:
                from_index = words.index("from")
                if from_index + 1 < len(words):
                    table_name = words[from_index + 1].strip("(),;")
                    tables.append(table_name)
            except (ValueError, IndexError):
                pass
        
        return tables
    
    def _get_query_type(self, query):
        """Determine query type (SELECT, INSERT, UPDATE, DELETE)"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith("select"):
            return "SELECT"
        elif query_lower.startswith("insert"):
            return "INSERT"
        elif query_lower.startswith("update"):
            return "UPDATE"
        elif query_lower.startswith("delete"):
            return "DELETE"
        else:
            return "OTHER"
    
    def _get_database_health(self):
        """Get database health metrics"""
        if not self.db_url:
            return {"status": "unknown", "error": "Database not configured"}
        
        session = self.Session()
        
        try:
            # Test connectivity
            start_time = time.time()
            session.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "connection_successful": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_successful": False
            }
            
        finally:
            session.close()
    
    def _get_query_performance_summary(self):
        """Get summary of query performance metrics"""
        summary = {}
        
        for query_type, metrics in self.performance_metrics.items():
            summary[query_type] = {
                "total_queries": metrics["count"],
                "average_time_ms": round(metrics["avg_time_ms"], 2),
                "min_time_ms": round(metrics["min_time_ms"], 2),
                "max_time_ms": round(metrics["max_time_ms"], 2)
            }
        
        return summary
    
    def _get_slow_queries_summary(self):
        """Get summary of slow queries"""
        recent_slow_queries = [
            q for q in self.query_log 
            if datetime.fromisoformat(q["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]
        
        return {
            "total_slow_queries": len(self.query_log),
            "recent_slow_queries": len(recent_slow_queries),
            "slowest_query_ms": max([q["execution_time_ms"] for q in self.query_log], default=0)
        }
    
    def _get_performance_recommendations(self):
        """Get general performance recommendations"""
        recommendations = [
            "Monitor query execution times regularly",
            "Add indexes for frequently used WHERE clauses",
            "Optimize connection pool settings based on usage patterns",
            "Consider query result caching for expensive operations",
            "Review and optimize slow queries (>100ms)",
            "Use connection pooling with appropriate pool size",
            "Implement query timeout limits",
            "Monitor database connection health"
        ]
        
        # Add specific recommendations based on metrics
        if len(self.query_log) > 10:
            recommendations.append("High number of slow queries detected - review query optimization")
        
        return recommendations

# Global optimizer instance
db_optimizer = DatabaseOptimizer()