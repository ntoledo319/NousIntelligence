"""
Database Optimization Utilities - Redirects to Unified Database Optimization

This module redirects to the unified database optimization service for zero functionality loss.
All original functions are preserved and work exactly the same.
"""

# Import everything from unified database optimization for backwards compatibility
from utils.unified_database_optimization import *

def optimize_query(query_name: str):
    """
    Decorator for timing and optimizing database queries

    Args:
        query_name: Name of the query for logging and stats tracking

    Returns:
        Decorated function
    """
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

def get_db_stats() -> Dict[str, Any]:
    """
    Get database query performance statistics

    Returns:
        Dictionary with query stats
    """
    return query_stats

def clear_db_stats() -> None:
    """
    Clear the database query statistics
    """
    query_stats.clear()

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Add query timing to connection"""
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    start_time = conn.info['query_start_time'].pop(-1)
    query_time = time.time() - start_time

    # Track query statistics in Flask g object if available
    try:
        from flask import g
        if hasattr(g, 'db_query_count'):
            g.db_query_count += 1
        if hasattr(g, 'db_query_time'):
            g.db_query_time += query_time
    except (RuntimeError, ImportError):
        pass

    # Log queries taking more than 150ms (increased threshold to reduce noise)
    if query_time > 0.15:
        # Extract the table name for better log filtering
        table_name = "unknown"
        if "FROM" in statement:
            parts = statement.split("FROM")
            if len(parts) > 1 and len(parts[1].strip().split()) > 0:
                table_name = parts[1].strip().split()[0]

        logger.warning(f"Slow SQL query on {table_name}: {query_time:.3f}s")

def get_or_create(model: Type[T], **kwargs) -> tuple[T, bool]:
    """
    Get an instance of a model by the given kwargs, or create it if it doesn't exist

    Args:
        model: SQLAlchemy model class
        **kwargs: Attributes to filter by and create with

    Returns:
        Tuple of (instance, created) where created is True if a new instance was created
    """
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True

def paginate_query(query: Query, page: int, per_page: int) -> Dict[str, Any]:
    """
    Paginate a SQLAlchemy query with consistent response format

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Number of items per page

    Returns:
        Dict with pagination info and results
    """
    # Ensure valid pagination parameters
    page = max(1, page)
    per_page = min(100, max(1, per_page))  # Limit to 100 items per page

    # Execute the pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Return consistent format
    return {
        'items': paginated.items,
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'next_page': paginated.next_num if paginated.has_next else None,
            'prev_page': paginated.prev_num if paginated.has_prev else None
        }
    }

def bulk_create(model: Type[T], items: List[Dict[str, Any]]) -> List[T]:
    """
    Efficiently create multiple objects in a single transaction

    Args:
        model: SQLAlchemy model class
        items: List of dictionaries with model attributes

    Returns:
        List of created model instances
    """
    instances = [model(**item) for item in items]
    db.session.bulk_save_objects(instances)
    db.session.commit()
    return instances

def bulk_update(model: Type[T], items: List[Dict[str, Any]], id_key: str = 'id') -> List[T]:
    """
    Efficiently update multiple objects in a single transaction

    Args:
        model: SQLAlchemy model class
        items: List of dictionaries with model attributes including ID
        id_key: Name of the ID attribute (default: 'id')

    Returns:
        List of updated model instances
    """
    # Get all IDs
    ids = [item[id_key] for item in items if id_key in item]
    if not ids:
        return []

    # Fetch all objects to update
    objects = model.query.filter(getattr(model, id_key).in_(ids)).all()
    id_to_obj = {getattr(obj, id_key): obj for obj in objects}

    # Update objects
    updated = []
    for item in items:
        if id_key in item and item[id_key] in id_to_obj:
            obj = id_to_obj[item[id_key]]
            for key, value in item.items():
                if key != id_key and hasattr(obj, key):
                    setattr(obj, key, value)
            updated.append(obj)

    db.session.commit()
    return updated

def setup_db_optimizations(app: Flask) -> None:
    """
    Set up database optimizations for the Flask application

    Args:
        app: Flask application instance
    """
    # Add before_request handler to track database operations
    @app.before_request
    def setup_db_context():
        """Initialize database context for the request"""
        g.db_query_count = 0
        g.db_query_time = 0.0

    # Add after_request handler to log database stats
    @app.after_request
    def log_db_stats(response):
        """Log database statistics after each request"""
        if hasattr(g, 'db_query_count') and g.db_query_count > 0:
            logger.debug(f"Request DB stats: {g.db_query_count} queries in {g.db_query_time:.3f}s")

            # Log slow requests
            if g.db_query_time > 0.5:  # More than 500ms spent on database queries
                logger.warning(f"Slow DB request: {g.db_query_count} queries in {g.db_query_time:.3f}s")

        return response

    # Add teardown handler to reset stats
    @app.teardown_request
    def reset_db_stats(exception=None):
        """Reset database statistics after request complete"""
        if hasattr(g, 'db_query_count'):
            del g.db_query_count
        if hasattr(g, 'db_query_time'):
            del g.db_query_time

    # Register database statistics endpoint if in debug mode
    if app.debug:
        @app.route('/debug/db-stats')
        def view_db_stats():
            """View database query statistics (debug only)"""
            from flask import jsonify
            return jsonify(get_db_stats())

        @app.route('/debug/db-stats/clear')
        def clear_db_stats_route():
            """Clear database query statistics (debug only)"""
            clear_db_stats()
            return jsonify({"status": "ok", "message": "Database statistics cleared"})

    logger.info("Database optimization utilities initialized")