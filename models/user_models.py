"""
User Models

This module contains user-related database models for the NOUS application.
"""

import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app_factory import db

class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Two-factor authentication fields
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    # Login attempt tracking
    failed_login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    
    # Security relationships
    login_attempts = db.relationship('LoginAttempt', backref='user_account', cascade='all, delete-orphan')
    lockouts = db.relationship('AccountLockout', foreign_keys='AccountLockout.user_id', backref='user_account', cascade='all, delete-orphan')
    two_factor_auth = db.relationship('TwoFactorAuth', backref='user_account', uselist=False, cascade='all, delete-orphan')
    auth_tokens = db.relationship('AuthToken', backref='user_account', cascade='all, delete-orphan')
    security_logs = db.relationship('SecurityAuditLog', backref='user_account', cascade='all, delete-orphan')
    
    @property
    def is_active(self):
        """Return whether the user is active (required by Flask-Login)"""
        return self.active
        
    @is_active.setter
    def is_active(self, value):
        self.active = value
    
    # OAuth fields
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    spotify_id = db.Column(db.String(128), unique=True, nullable=True)
    
    def set_password(self, password):
        """Set password hash from plain text password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'has_google': bool(self.google_id),
            'has_spotify': bool(self.spotify_id)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserSettings(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(32), default='light')
    notifications_enabled = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='en-US')
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('settings', uselist=False, lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'notifications_enabled': self.notifications_enabled,
            'language': self.language,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BetaTester(db.Model):
    """Beta tester registration model"""
    __tablename__ = 'beta_testers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    access_code = db.Column(db.String(20), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    activation_date = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('beta_tester', uselist=False, lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'is_approved': self.is_approved,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'activation_date': self.activation_date.isoformat() if self.activation_date else None
        }