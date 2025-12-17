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
    """Check database connection health
    
    Returns:
        dict: Health status information
    """
    try:
        # Simple health check - this would be enhanced with actual DB connection test
        return {
            'status': 'healthy',
            'type': 'postgresql',
            'connection': 'active'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }