import logging
logger = logging.getLogger(__name__)
"""
Centralized Database Configuration
Eliminates circular imports by providing a clean database setup
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Single database instance used throughout the app
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Import essential models here to register them
        try:
            from models.user import User
            from models.beta_models import BetaUser, BetaFeedback
            from models.health_models import (
                DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
                DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
                AAAchievement
            )
        except ImportError as e:
            logger.error(Error: Could not import some models: {e})
            raise e
        
        # Note: Database tables are now managed through Flask-Migrate
        # Use 'flask db upgrade' to create/update database schema
        
        return db