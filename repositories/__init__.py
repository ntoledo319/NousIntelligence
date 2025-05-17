"""
Repositories Package

This package provides repository implementations for database operations.
Repositories provide an abstraction layer for database access and implement
common patterns for data access.

@module repositories
@author NOUS Development Team
"""

# Import and export repository classes for easier imports
from repositories.base import Repository
from repositories.user import UserRepository
from repositories.user_settings import UserSettingsRepository

# Export specific repositories for convenient imports
__all__ = [
    'Repository',
    'UserRepository',
    'UserSettingsRepository'
] 