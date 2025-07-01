"""
NOUS Models - Main Models Module
Imports all model definitions for the NOUS application
"""

# Import specific models instead of using wildcard imports
from models.user import User
from models.analytics_models import (
    Activity, Insight, HealthMetric, AnalyticsData
)
from models.health_models import (
    DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
    DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
    AAAchievement
)
from models.financial_models import (
    FinancialAccount, Transaction, Budget, FinancialGoal
)
from models.collaboration_models import (
    Family, SharedTask, SharedNote, Collaboration
)
from models.language_learning_models import (
    LanguageLearning, LanguageProgress, LanguageExercise
)
from models.setup_models import (
    SetupProgress, Goal, UserSettings
)
from models.aa_content_models import (
    AABigBookAudio, AADailyReflection, AAContent
)
from models.ai_models import (
    AIService, AIConversation, AIModel
)
from models.beta_models import (
    BetaUser, BetaFeedback, BetaFeature
)
from models.product_models import (
    Product, ProductCategory, ProductReview
)

# Database instance
try:
    from models.database import db
except ImportError:
    from database import db

# Make sure all models are properly registered
__all__ = [
    'db',
    'User',
    'UserSettings', 
    'SetupProgress',
    'Goal',
    'Activity',
    'Insight',
    'HealthMetric',
    'FinancialAccount',
    'Transaction',
    'Family',
    'SharedTask',
    'LanguageLearning',
    'AABigBookAudio',
    'AIService',
    'BetaFeature',
    'BetaUser',
    'BetaFeedback',
    'Product',
    'DBTSkillRecommendation',
    'DBTSkillLog',
    'DBTDiaryCard',
    'DBTSkillChallenge',
    'DBTCrisisResource',
    'DBTEmotionTrack',
    'AAAchievement'
]