"""
Services Package

This package provides service implementations for business logic operations.
Services coordinate operations and combine repository calls with business logic.

@module services
@author NOUS Development Team
"""

# Import and export service classes for easier imports
from services.settings import SettingsService

# Export specific services for convenient imports
__all__ = [
    'SettingsService'
] 