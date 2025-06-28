"""
Models Package

This package contains all database models for the NOUS application.
"""

# Core models - always available
from models.user import User
from models.database import init_db, get_db_health

# Import all models directly - let individual files handle graceful degradation
import models.health_models
import models.analytics_models

# Re-export for convenience
from models.health_models import (
    DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
    DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
    DBTSkillCategory, AAAchievement
)

from models.analytics_models import UserActivity, Goal, Insight

# Language learning models with fallback
try:
    from models.language_learning_models import (
        LanguageLearningSession, Vocabulary, Grammar, 
        LearningProgress, LanguageGoal
    )
except ImportError:
    # Simple fallback classes
    LanguageLearningSession = type('LanguageLearningSession', (), {})
    Vocabulary = type('Vocabulary', (), {})
    Grammar = type('Grammar', (), {})
    LearningProgress = type('LearningProgress', (), {})
    LanguageGoal = type('LanguageGoal', (), {})

# Simple placeholder classes for models referenced in routes
class Task:
    """Placeholder Task model"""
    pass

class UserPreference:
    """Placeholder UserPreference model"""
    pass

class SystemSettings:
    """Placeholder SystemSettings model"""
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key - placeholder implementation"""
        return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a setting value by key - placeholder implementation"""
        pass

class WeatherLocation:
    """Placeholder WeatherLocation model"""
    pass

class UserSettings:
    """Placeholder UserSettings model"""
    pass

# Create a simple db placeholder for routes that expect it
class MockDB:
    """Mock database interface for backwards compatibility"""
    def __init__(self):
        self.session = None

# Mock database instance
db = MockDB()

# Export models at the package level
__all__ = [
    'User', 'Task', 'UserPreference', 'SystemSettings', 'WeatherLocation', 'UserSettings', 'db',
    'init_db', 'get_db_health',
    # Health models
    'DBTSkillRecommendation', 'DBTSkillLog', 'DBTDiaryCard', 'DBTSkillChallenge', 
    'DBTCrisisResource', 'DBTEmotionTrack', 'DBTSkillCategory', 'AAAchievement', 'AABigBook', 'AABigBookAudio',
    # Analytics models
    'UserActivity', 'Goal', 'Insight',
    # Language learning models
    'LanguageLearningSession', 'Vocabulary', 'Grammar', 'LearningProgress', 'LanguageGoal'
]