"""
Models Package

This package contains all database models for the NOUS application,
organized into related modules for better maintainability.
"""

# Import all models from the flat models.py file for now
# This ensures backward compatibility while we transition to a modular structure
from models.user import User
from models.user_models import UserPreference, UserSetting
from models.task_models import Task
from models.health_models import HealthMetric
from models.system_models import WeatherData, SystemSetting

# Export models at the package level for easy importing
__all__ = [
    'User', 'UserPreference', 'UserSetting', 
    'Task', 'HealthMetric', 
    'WeatherData', 'SystemSetting'
]