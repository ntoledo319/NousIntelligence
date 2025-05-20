"""
Database Models Package

This package contains all database models for the NOUS application organized by feature area.
"""

# Re-export db from app_factory to maintain compatibility with existing code
from app_factory import db

# Import models here
from models.user_models import User, UserSettings, BetaTester
from models.task_models import Task
from models.system_models import SystemSettings
from models.health_models import (
    DBTSkillRecommendation, DBTSkillLog, DBTCrisisResource, DBTSkillCategory, 
    DBTDiaryCard, DBTSkillChallenge, DBTEmotionTrack, AAAchievement
)
from models.deal_models import Deal, Product

# Import AI and AA content models
from models.ai_models import UserAIUsage, AIServiceConfig, AIModelConfig, UserAIPreferences
from models.aa_content_models import (
    AABigBook, AABigBookAudio, AASpeakerRecording, AADailyReflection, AAFavorite
)

# Export all models
__all__ = [
    'db',
    'User', 'UserSettings', 'BetaTester',
    'Task',
    'SystemSettings',
    'DBTSkillRecommendation', 'DBTSkillLog', 'DBTCrisisResource', 'DBTSkillCategory',
    'DBTDiaryCard', 'DBTSkillChallenge', 'DBTEmotionTrack', 'AAAchievement',
    'Deal', 'Product',
    'UserAIUsage', 'AIServiceConfig', 'AIModelConfig', 'UserAIPreferences',
    'AABigBook', 'AABigBookAudio', 'AASpeakerRecording', 'AADailyReflection', 'AAFavorite'
]