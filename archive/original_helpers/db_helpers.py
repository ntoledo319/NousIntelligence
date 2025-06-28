"""
Database Helper Utilities

This module provides helper functions for database operations
"""

from flask import current_app
from models import User

def get_user_by_id(user_id):
    """
    Get a user by their ID

    Args:
        user_id: The user's ID

    Returns:
        User object or None if not found
    """
    try:
        return User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"Error retrieving user: {str(e)}")
        return None