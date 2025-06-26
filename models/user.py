"""
User Models

This module defines user-related database models for the NOUS application,
including user account data, preferences, and authentication.
"""

from flask_login import UserMixin
from database import db

class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=True)  # Don't use is_active as it conflicts with UserMixin
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())

    # Override UserMixin property with our database column
    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return f'<User {self.username}>'