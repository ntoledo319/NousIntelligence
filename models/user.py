"""
User Models

This module defines user-related database models for the NOUS application,
including user account data, preferences, and authentication.
"""

from database import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User account model"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # OAuth token storage for secure API access
    google_access_token = db.Column(db.Text, nullable=True)
    google_refresh_token = db.Column(db.Text, nullable=True)
    google_token_expires_at = db.Column(db.DateTime, nullable=True)
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)
    
    def is_token_expired(self):
        """Check if Google access token is expired"""
        if not self.google_token_expires_at:
            return True
        return datetime.utcnow() > self.google_token_expires_at
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'