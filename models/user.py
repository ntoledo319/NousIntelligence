"""
User Models

This module defines user-related database models for the NOUS application,
including user account data, preferences, and authentication.
"""

from utils.auth_compat import login_required, current_user, get_current_user
from database import db
from datetime import datetime

class User(db.Model):
    """User account model"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'