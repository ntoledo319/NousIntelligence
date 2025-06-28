"""
Repository Pattern Implementation for NOUS Application

This module provides data access layer abstraction for the NOUS application,
implementing the repository pattern for clean separation of concerns.
"""

from .user_repository import UserRepository
from .health_repository import HealthRepository
from .analytics_repository import AnalyticsRepository
from .language_learning_repository import LanguageLearningRepository

__all__ = [
    'UserRepository',
    'HealthRepository', 
    'AnalyticsRepository',
    'LanguageLearningRepository'
]