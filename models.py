"""
NOUS Models - Main Models Module
Imports all model definitions for the NOUS application
"""

# Import all models to ensure they're available when this module is imported
from models.user import *
from models.analytics_models import *
from models.health_models import *
from models.financial_models import *
from models.collaboration_models import * 
from models.language_learning_models import *
from models.setup_models import *
from models.aa_content_models import *
from models.ai_models import *
from models.beta_models import *
from models.product_models import *
from models.enhanced_health_models import *

# Database instance
from models.database import db

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
    'Product',
    'EnhancedHealthModel'
]