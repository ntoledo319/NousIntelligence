"""
Models Package

This package contains all database models for the NOUS application.
"""

# Import available models
from models.user import User
from models.database import init_db, get_db_health

# Simple placeholder classes for models referenced in routes
class Task:
    """Placeholder Task model"""
    pass

class UserPreference:
    """Placeholder UserPreference model"""
    pass

class SystemSetting:
    """Placeholder SystemSetting model"""
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
    'User', 'Task', 'UserPreference', 'SystemSetting', 'WeatherLocation', 'UserSettings', 'db',
    'init_db', 'get_db_health'
]