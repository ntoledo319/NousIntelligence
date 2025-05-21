"""
Models Package

This package contains all database models for the NOUS application,
organized into related modules for better maintainability.

@package models
"""

# Import memory models to make them available through the models package
from models.memory_models import UserMemoryEntry, UserTopicInterest, UserEntityMemory

# Export memory models at the package level
__all__ = ['UserMemoryEntry', 'UserTopicInterest', 'UserEntityMemory']