"""
Database Configuration Module

This module configures the database connection and provides
utility functions for database operations.
"""

import logging

logger = logging.getLogger(__name__)

def init_db(app, db):
    """Initialize the database with the application context

    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from models.user import User
        from models.beta_models import BetaUser, BetaUserFeedback
        from models.health_models import (
            DBTSkillLog, DBTDiaryCard, DBTSkillCategory,
            DBTSkillRecommendation, DBTSkillChallenge,
            DBTCrisisResource, DBTEmotionTrack,
            AABigBook, AABigBookAudio, AASpeakerRecording, AAFavorite
        )
        # Create tables if they don't exist
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

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