"""
Database Configuration Module

This module configures the database connection and provides
utility functions for database operations.
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Single database instance used throughout the app
db = SQLAlchemy(model_class=Base)

def init_db(app):
    """Initialize the database with the application context

    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        try:
            from models.user import User
            from models.beta_models import BetaUser, BetaFeedback
            from models.health_models import (
                DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
                DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
                AAAchievement
            )
        except ImportError as e:
            logger.error(f"Error: Could not import some models: {e}")
            # Don't raise - allow app to continue
        
        # Note: Database tables are now managed through Flask-Migrate
        # Use 'flask db upgrade' to create/update database schema
        
        return db

def get_db_health():
    """Check database connection health with actual connection test
    
    Returns:
        dict: Health status information including connection test results
    """
    from flask import current_app
    from sqlalchemy import text
    import time
    
    result = {
        'status': 'unknown',
        'type': 'unknown',
        'connection': 'unknown',
        'latency_ms': None,
        'error': None
    }
    
    try:
        # Determine database type from URI
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri or 'postgres' in db_uri:
            result['type'] = 'postgresql'
        elif 'sqlite' in db_uri:
            result['type'] = 'sqlite'
        elif 'mysql' in db_uri:
            result['type'] = 'mysql'
        else:
            result['type'] = 'unknown'
        
        # Actual connection test with latency measurement
        start_time = time.time()
        db.session.execute(text('SELECT 1'))
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        result['status'] = 'healthy'
        result['connection'] = 'active'
        result['latency_ms'] = round(latency, 2)
        
        # Check connection pool stats if available
        engine = db.engine
        if hasattr(engine.pool, 'size'):
            result['pool_size'] = engine.pool.size()
        if hasattr(engine.pool, 'checkedin'):
            result['pool_available'] = engine.pool.checkedin()
        if hasattr(engine.pool, 'checkedout'):
            result['pool_in_use'] = engine.pool.checkedout()
            
    except Exception as e:
        result['status'] = 'unhealthy'
        result['connection'] = 'failed'
        result['error'] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return result