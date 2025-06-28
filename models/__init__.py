"""
Models Package

This package contains all database models for the NOUS application.
"""

# Core models - always available
from datetime import datetime
from database import db
from models.user import User
from models.database import init_db, get_db_health

# Import all models directly - let individual files handle graceful degradation
import models.health_models
import models.analytics_models

# Re-export for convenience
from models.health_models import (
    DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
    DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
    DBTSkillCategory, AAAchievement, AABigBook, AABigBookAudio, 
    AASpeakerRecording, AAFavorite
)

from models.analytics_models import UserActivity, Goal, Insight

# Language learning models with fallback
try:
    from models.language_learning_models import (
        LanguageProfile, VocabularyItem, LearningSession, 
        ConversationTemplate, ConversationPrompt
    )
except ImportError:
    # Simple fallback classes
    LanguageProfile = type('LanguageProfile', (), {})
    VocabularyItem = type('VocabularyItem', (), {})
    LearningSession = type('LearningSession', (), {})
    ConversationTemplate = type('ConversationTemplate', (), {})
    ConversationPrompt = type('ConversationPrompt', (), {})

# Product model for Amazon/shopping functionality
class Product(db.Model):
    """Product model for shopping and price tracking"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    asin = db.Column(db.String(20), unique=True)  # Amazon ASIN
    price = db.Column(db.Float)
    original_price = db.Column(db.Float)
    discount_percentage = db.Column(db.Float)
    url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    rating = db.Column(db.Float)
    reviews_count = db.Column(db.Integer)
    availability = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Task model for task management
class Task(db.Model):
    """Task model for task management"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    category = db.Column(db.String(100))
    tags = db.Column(db.Text)  # JSON array of tags
    estimated_duration = db.Column(db.Integer)  # minutes
    actual_duration = db.Column(db.Integer)  # minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPreference(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text)
    preference_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemSettings(db.Model):
    """System-wide settings"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), nullable=False, unique=True)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(setting_key=key, is_active=True).first()
        if setting:
            if setting.setting_type == 'boolean':
                return setting.setting_value.lower() == 'true'
            elif setting.setting_type == 'integer':
                return int(setting.setting_value)
            elif setting.setting_type == 'json':
                import json
                return json.loads(setting.setting_value)
            return setting.setting_value
        return default
    
    @classmethod
    def set_setting(cls, key, value, description=None, setting_type='string'):
        """Set a setting value by key"""
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            setting.setting_type = setting_type
            if description:
                setting.description = description
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(
                setting_key=key,
                setting_value=str(value),
                setting_type=setting_type,
                description=description
            )
            db.session.add(setting)
        db.session.commit()
        return setting

class WeatherLocation(db.Model):
    """Weather location tracking"""
    __tablename__ = 'weather_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSettings(db.Model):
    """Individual user settings (alias for UserPreference for backward compatibility)"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    setting_name = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create a simple db placeholder for routes that expect it
class MockDB:
    """Mock database interface for backwards compatibility"""
    def __init__(self):
        self.session = None

# Mock database instance (only used as fallback)
# db is imported from database.py above

# Export models at the package level
__all__ = [
    'User', 'Task', 'UserPreference', 'SystemSettings', 'WeatherLocation', 'UserSettings', 'Product', 'db',
    'init_db', 'get_db_health',
    # Health models
    'DBTSkillRecommendation', 'DBTSkillLog', 'DBTDiaryCard', 'DBTSkillChallenge', 
    'DBTCrisisResource', 'DBTEmotionTrack', 'DBTSkillCategory', 'AAAchievement', 
    'AABigBook', 'AABigBookAudio', 'AASpeakerRecording', 'AAFavorite',
    # Analytics models
    'UserActivity', 'Goal', 'Insight',
    # Language learning models
    'LanguageProfile', 'VocabularyItem', 'LearningSession', 'ConversationTemplate', 'ConversationPrompt'
]