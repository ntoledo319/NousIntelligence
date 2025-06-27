"""
User Models

This module defines user-related database models for the NOUS application,
including user account data, preferences, and authentication.
"""

from flask_login import UserMixin

# Simple User model for authentication
class User(UserMixin):
    """User account model"""
    
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
        self.active = True
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'