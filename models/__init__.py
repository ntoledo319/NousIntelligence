"""
Models Package

This package contains all database models for the NOUS application.
"""

# Import available models
from models.user import User
from models.database import init_db, get_db_health

# Import health models
try:
    from models.health_models import (
        DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
        DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
        AAAchievement, AABigBook, AABigBookAudio
    )
except ImportError:
    # Create placeholder classes if models aren't available
    class DBTSkillLog:
        pass
    class DBTSkillRecommendation:
        pass
    class DBTDiaryCard:
        pass
    class DBTSkillChallenge:
        pass
    class DBTCrisisResource:
        pass
    class DBTEmotionTrack:
        pass
    class AAAchievement:
        pass
    class AABigBook:
        pass
    class AABigBookAudio:
        pass

# Import other model categories with fallbacks
try:
    from models.analytics_models import UserActivity, Goal, Insight
except ImportError:
    class UserActivity:
        pass
    class Goal:
        pass
    class Insight:
        pass

try:
    from models.language_learning_models import (
        LanguageLearningSession, Vocabulary, Grammar, 
        LearningProgress, LanguageGoal
    )
except ImportError:
    class LanguageLearningSession:
        pass
    class Vocabulary:
        pass
    class Grammar:
        pass
    class LearningProgress:
        pass
    class LanguageGoal:
        pass

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
    'DBTCrisisResource', 'DBTEmotionTrack', 'AAAchievement', 'AABigBook', 'AABigBookAudio',
    # Analytics models
    'UserActivity', 'Goal', 'Insight',
    # Language learning models
    'LanguageLearningSession', 'Vocabulary', 'Grammar', 'LearningProgress', 'LanguageGoal'
]