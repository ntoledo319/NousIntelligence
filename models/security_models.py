"""
Security Models

This module contains security-related database models for the NOUS application.
"""

from datetime import datetime, timedelta
from app_factory import db

class SecurityLog(db.Model):
    """Security event log for auditing purposes"""
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45))  # IPv6 addresses can be up to 45 chars
    user_agent = db.Column(db.Text)
    details = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details
        }

class LoginAttempt(db.Model):
    """Record of login attempts for security monitoring"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    @classmethod
    def count_recent_failures(cls, email, minutes=15):
        """Count recent failed login attempts for an email within time window"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return cls.query.filter(
            cls.email == email,
            cls.success == False,
            cls.timestamp >= cutoff
        ).count()
    
    @classmethod
    def is_account_locked(cls, email, max_attempts=5, lockout_minutes=15):
        """Check if account should be locked based on recent failed attempts"""
        recent_failures = cls.count_recent_failures(email, minutes=lockout_minutes)
        return recent_failures >= max_attempts

class AuthToken(db.Model):
    """Authentication tokens for API access"""
    __tablename__ = 'auth_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    token_hash = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(255))
    expires_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    revoked = db.Column(db.Boolean, default=False)
    
    # Define relationship to User
    user = db.relationship('User', backref=db.backref('auth_tokens', lazy='dynamic'))