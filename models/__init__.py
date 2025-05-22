"""
Models Package

This package contains all database models for the NOUS application,
organized into related modules for better maintainability.
"""

# Import user models
from models.user import User

# Export models at the package level for easy importing
__all__ = ['User']