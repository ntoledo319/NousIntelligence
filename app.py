"""
Application Module for Imports

This module exists to provide clean imports for other modules in the application.
Instead of importing directly from main.py, modules can import from here.
This helps avoid circular import issues.
"""

from app_factory import create_app, db

# Create an application instance for direct import
# This allows modules to import 'app' directly
app = create_app()

# Export key components for easy importing
__all__ = ['app', 'db']