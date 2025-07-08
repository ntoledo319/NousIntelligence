import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_optimized_engine():
    """Create database engine with optimized connection pooling"""
    
    database_url = os.getenv('DATABASE_URL', 'sqlite:///nous.db')
    
    # Connection pool settings
    pool_size = int(os.getenv('DB_POOL_SIZE', 10))
    max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 20))
    pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
    pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))  # 1 hour
    
    engine_kwargs = {
        'poolclass': QueuePool,
        'pool_size': pool_size,
        'max_overflow': max_overflow,
        'pool_timeout': pool_timeout,
        'pool_recycle': pool_recycle,
        'pool_pre_ping': True,  # Verify connections before use
        'echo': os.getenv('DB_ECHO', 'False').lower() == 'true'
    }
    
    # PostgreSQL specific optimizations
    if database_url.startswith('postgresql'):
        engine_kwargs.update({
            'connect_args': {
                'options': '-c default_transaction_isolation=read_committed'
            }
        })
    
    # SQLite specific optimizations
    elif database_url.startswith('sqlite'):
        engine_kwargs.update({
            'connect_args': {
                'check_same_thread': False,
                'timeout': 20
            }
        })
    
    engine = create_engine(database_url, **engine_kwargs)
    
    return engine

def get_connection_stats(engine):
    """Get connection pool statistics"""
    if hasattr(engine.pool, 'size'):
        return {
            'pool_size': engine.pool.size(),
            'checked_in': engine.pool.checkedin(),
            'checked_out': engine.pool.checkedout(),
            'overflow': engine.pool.overflow(),
            'invalidated': engine.pool.invalidated()
        }
    return {}
