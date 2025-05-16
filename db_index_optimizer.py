"""
@module db_index_optimizer
@description Database index optimization for improved query performance
@author AI Assistant
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Configure logger
logger = logging.getLogger(__name__)

class IndexOptimizer:
    """Database index optimizer for performance tuning"""
    
    def __init__(self, engine: Engine):
        """
        Initialize the index optimizer
        
        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
        self.inspector = inspect(engine)
    
    def analyze_query_performance(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN
        
        Args:
            query: SQL query to analyze
            params: Query parameters
            
        Returns:
            Dictionary with query analysis results
        """
        if params is None:
            params = {}
            
        try:
            # Start with EXPLAIN ANALYZE (PostgreSQL) or EXPLAIN (MySQL/SQLite)
            if self.engine.name == 'postgresql':
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                result = self.engine.execute(text(explain_query), params).scalar()
                return result[0]
            elif self.engine.name == 'mysql':
                explain_query = f"EXPLAIN FORMAT=JSON {query}"
                result = self.engine.execute(text(explain_query), params).scalar()
                return result
            elif self.engine.name == 'sqlite':
                explain_query = f"EXPLAIN QUERY PLAN {query}"
                result = self.engine.execute(text(explain_query), params).fetchall()
                return {"query_plan": [dict(row) for row in result]}
            else:
                return {"error": f"Unsupported database engine: {self.engine.name}"}
        except SQLAlchemyError as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {"error": str(e)}
    
    def get_existing_indexes(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get existing indexes for a table
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of existing indexes
        """
        try:
            indexes = self.inspector.get_indexes(table_name, schema)
            return indexes
        except SQLAlchemyError as e:
            logger.error(f"Error getting indexes for {table_name}: {str(e)}")
            return []
    
    def get_all_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        Get all tables in the database
        
        Args:
            schema: Schema name (optional)
            
        Returns:
            List of table names
        """
        try:
            return self.inspector.get_table_names(schema)
        except SQLAlchemyError as e:
            logger.error(f"Error getting tables: {str(e)}")
            return []
    
    def get_table_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get column information for a table
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of column information dictionaries
        """
        try:
            return self.inspector.get_columns(table_name, schema)
        except SQLAlchemyError as e:
            logger.error(f"Error getting columns for {table_name}: {str(e)}")
            return []
    
    def get_table_primary_key(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        """
        Get primary key column names for a table
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of primary key column names
        """
        try:
            pk_constraint = self.inspector.get_pk_constraint(table_name, schema)
            return pk_constraint.get('constrained_columns', [])
        except SQLAlchemyError as e:
            logger.error(f"Error getting primary key for {table_name}: {str(e)}")
            return []
    
    def create_index(self, table_name: str, columns: List[str], index_name: Optional[str] = None, 
                   unique: bool = False, schema: Optional[str] = None) -> bool:
        """
        Create an index on the specified columns
        
        Args:
            table_name: Name of the table
            columns: List of column names to index
            index_name: Name for the index (optional)
            unique: Whether the index should enforce uniqueness
            schema: Schema name (optional)
            
        Returns:
            True if index was created successfully, False otherwise
        """
        if not columns:
            logger.error("No columns specified for index")
            return False
            
        # Generate index name if not provided
        if not index_name:
            index_name = f"ix_{table_name}_{'_'.join(columns)}"
            
        # Check if index already exists
        existing_indexes = self.get_existing_indexes(table_name, schema)
        for idx in existing_indexes:
            if set(idx['column_names']) == set(columns):
                logger.info(f"Index on {', '.join(columns)} already exists for table {table_name}")
                return True
                
        # Create the index
        try:
            schema_prefix = f"{schema}." if schema else ""
            unique_str = "UNIQUE " if unique else ""
            column_str = ", ".join(columns)
            
            sql = f"CREATE {unique_str}INDEX {index_name} ON {schema_prefix}{table_name} ({column_str})"
            
            # Execute the SQL
            with self.engine.begin() as conn:
                conn.execute(text(sql))
                
            logger.info(f"Created index {index_name} on {table_name} ({', '.join(columns)})")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating index: {str(e)}")
            return False
    
    def drop_index(self, index_name: str, table_name: str, schema: Optional[str] = None) -> bool:
        """
        Drop an index
        
        Args:
            index_name: Name of the index to drop
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            True if index was dropped successfully, False otherwise
        """
        try:
            schema_prefix = f"{schema}." if schema else ""
            
            # Syntax varies by database engine
            if self.engine.name == 'postgresql':
                sql = f"DROP INDEX {schema_prefix}{index_name}"
            elif self.engine.name == 'mysql':
                sql = f"ALTER TABLE {schema_prefix}{table_name} DROP INDEX {index_name}"
            elif self.engine.name == 'sqlite':
                sql = f"DROP INDEX {schema_prefix}{index_name}"
            else:
                logger.error(f"Unsupported database engine: {self.engine.name}")
                return False
                
            # Execute the SQL
            with self.engine.begin() as conn:
                conn.execute(text(sql))
                
            logger.info(f"Dropped index {index_name} from {table_name}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error dropping index: {str(e)}")
            return False
    
    def find_missing_indexes(self, slow_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze slow queries and suggest missing indexes
        
        Args:
            slow_queries: List of slow SQL queries
            
        Returns:
            List of suggested indexes
        """
        suggested_indexes = []
        
        for query in slow_queries:
            try:
                # Analyze the query
                analysis = self.analyze_query_performance(query)
                
                # Check for full table scans (varies by database)
                if self.engine.name == 'postgresql':
                    for node in analysis.get('Plan', {}).get('Plans', []):
                        if node.get('Node Type') == 'Seq Scan':
                            table_name = node.get('Relation Name')
                            filter_conds = node.get('Filter', '')
                            
                            # Extract potential columns for indexing from filter conditions
                            columns = self._extract_columns_from_filter(filter_conds)
                            
                            if columns and table_name:
                                suggested_indexes.append({
                                    'table': table_name,
                                    'columns': columns,
                                    'reason': f"Sequential scan on {table_name} with filter on {', '.join(columns)}"
                                })
                elif self.engine.name == 'mysql':
                    # MySQL-specific analysis
                    for row in analysis.get('query_block', {}).get('table', []):
                        if row.get('access_type') == 'ALL':  # Full table scan
                            table_name = row.get('table_name')
                            used_columns = self._extract_columns_from_mysql_where(row.get('attached_condition', ''))
                            
                            if used_columns and table_name:
                                suggested_indexes.append({
                                    'table': table_name,
                                    'columns': used_columns,
                                    'reason': f"Full table scan on {table_name} with filter on {', '.join(used_columns)}"
                                })
                elif self.engine.name == 'sqlite':
                    # SQLite-specific analysis
                    for row in analysis.get('query_plan', []):
                        if 'SCAN TABLE' in row.get('detail', ''):
                            parts = row.get('detail', '').split()
                            table_idx = parts.index('TABLE') + 1 if 'TABLE' in parts else -1
                            
                            if table_idx > 0 and table_idx < len(parts):
                                table_name = parts[table_idx]
                                
                                # Look for WHERE clause columns
                                used_columns = self._extract_columns_from_filter(query)
                                
                                if used_columns:
                                    suggested_indexes.append({
                                        'table': table_name,
                                        'columns': used_columns,
                                        'reason': f"Table scan on {table_name} with filter on {', '.join(used_columns)}"
                                    })
            except Exception as e:
                logger.error(f"Error analyzing query for missing indexes: {str(e)}")
                
        return suggested_indexes
    
    def _extract_columns_from_filter(self, filter_str: str) -> List[str]:
        """
        Extract column names from a filter condition string
        
        Args:
            filter_str: Filter condition string
            
        Returns:
            List of column names
        """
        if not filter_str:
            return []
            
        # Simple regex-based extraction - could be improved
        import re
        # Look for patterns like "column_name = value" or "column_name > value"
        matches = re.findall(r'(\w+)\s*[=><!\s]', filter_str)
        
        # Remove SQL keywords and numbers
        keywords = ['AND', 'OR', 'IN', 'NOT', 'NULL', 'IS', 'LIKE', 'BETWEEN']
        return [m for m in matches if m.upper() not in keywords and not m.isdigit()]
    
    def _extract_columns_from_mysql_where(self, where_str: str) -> List[str]:
        """
        Extract column names from MySQL WHERE clause
        
        Args:
            where_str: WHERE clause string
            
        Returns:
            List of column names
        """
        # For MySQL EXPLAIN JSON format
        import re
        columns = []
        
        # Look for column references like `table`.`column`
        matches = re.findall(r'`([^`]+)`\.`([^`]+)`', where_str)
        for table, column in matches:
            columns.append(column)
            
        # Also look for simpler references
        simple_matches = re.findall(r'(\w+)\s*[=><!\s]', where_str)
        columns.extend([m for m in simple_matches if m.upper() not in ['AND', 'OR', 'NOT', 'NULL']])
        
        return list(set(columns))
    
    def benchmark_query(self, query: str, params: Optional[Dict[str, Any]] = None, iterations: int = 3) -> Dict[str, Any]:
        """
        Benchmark a query's performance
        
        Args:
            query: SQL query to benchmark
            params: Query parameters
            iterations: Number of times to run the query
            
        Returns:
            Dictionary with benchmark results
        """
        if params is None:
            params = {}
            
        results = {
            'query': query,
            'iterations': iterations,
            'execution_times': [],
            'average_time': 0,
            'min_time': 0,
            'max_time': 0
        }
        
        try:
            for i in range(iterations):
                start_time = time.time()
                
                with self.engine.connect() as conn:
                    conn.execute(text(query), params)
                    
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                results['execution_times'].append(execution_time)
                
            # Calculate statistics
            times = results['execution_times']
            results['average_time'] = sum(times) / len(times)
            results['min_time'] = min(times)
            results['max_time'] = max(times)
            
            return results
        except SQLAlchemyError as e:
            logger.error(f"Error benchmarking query: {str(e)}")
            return {'error': str(e)}
    
    def analyze_all_tables(self) -> None:
        """
        Run ANALYZE on all tables to update statistics
        
        This helps the query planner make better decisions
        """
        try:
            tables = self.get_all_tables()
            
            for table in tables:
                with self.engine.begin() as conn:
                    if self.engine.name == 'postgresql':
                        conn.execute(text(f"ANALYZE {table}"))
                    elif self.engine.name == 'mysql':
                        conn.execute(text(f"ANALYZE TABLE {table}"))
                    elif self.engine.name == 'sqlite':
                        conn.execute(text(f"ANALYZE {table}"))
                        
                logger.info(f"Analyzed table {table}")
        except SQLAlchemyError as e:
            logger.error(f"Error analyzing tables: {str(e)}")

def optimize_db_indexes(engine: Engine, queries_log_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Optimize database indexes based on slow queries
    
    Args:
        engine: SQLAlchemy engine
        queries_log_path: Path to slow queries log file (optional)
        
    Returns:
        List of created indexes
    """
    optimizer = IndexOptimizer(engine)
    slow_queries = []
    created_indexes = []
    
    # Load slow queries from log if provided
    if queries_log_path:
        try:
            with open(queries_log_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('SELECT'):
                        slow_queries.append(line.strip())
        except Exception as e:
            logger.error(f"Error reading queries log: {str(e)}")
    
    # If no log file, use some common patterns to identify potentially slow queries
    if not slow_queries:
        # Get tables to analyze
        tables = optimizer.get_all_tables()
        for table in tables:
            # Get columns for this table
            columns = optimizer.get_table_columns(table)
            column_names = [col['name'] for col in columns]
            
            # Look for timestamp/date columns that are often used for filtering
            date_columns = [col['name'] for col in columns 
                          if any(dt_type in col['type'].__str__().lower() 
                                for dt_type in ['timestamp', 'date', 'datetime'])]
            
            # Look for columns that might be used in WHERE clauses
            potential_filter_columns = [col['name'] for col in columns
                                      if any(name in col['name'].lower()
                                            for name in ['status', 'type', 'category', 'state', 'is_', 'has_'])]
            
            # Create sample slow queries based on common patterns
            if date_columns:
                slow_queries.append(f"SELECT * FROM {table} WHERE {date_columns[0]} > '2023-01-01'")
            
            if potential_filter_columns:
                slow_queries.append(f"SELECT * FROM {table} WHERE {potential_filter_columns[0]} = 'value'")
                
            # Foreign key columns often need indexes
            foreign_key_columns = [col['name'] for col in columns if col['name'].endswith('_id')]
            for fk_col in foreign_key_columns:
                slow_queries.append(f"SELECT * FROM {table} WHERE {fk_col} = 123")
    
    # Analyze queries and find missing indexes
    logger.info(f"Analyzing {len(slow_queries)} slow queries for missing indexes")
    suggested_indexes = optimizer.find_missing_indexes(slow_queries)
    
    # Create suggested indexes
    for idx in suggested_indexes:
        table_name = idx['table']
        columns = idx['columns']
        
        # Skip if no columns identified
        if not columns:
            continue
            
        # Create an index name
        index_name = f"ix_{table_name}_{'_'.join(columns)}"
        
        # Create the index
        success = optimizer.create_index(table_name, columns, index_name)
        if success:
            created_indexes.append({
                'table': table_name,
                'columns': columns,
                'index_name': index_name
            })
    
    # Run ANALYZE to update statistics
    optimizer.analyze_all_tables()
    
    logger.info(f"Created {len(created_indexes)} new indexes")
    return created_indexes

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from app import db
    created_indexes = optimize_db_indexes(db.engine)
    print(f"Created {len(created_indexes)} indexes:") 