"""
Security Models Module

This module defines the database models for security-related features
including account lockout, two-factor authentication, trusted devices,
security audit logs, and authentication tokens.

@module security_models
@description Security-related database models
"""

from datetime import datetime, timedelta
import secrets
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

# Import db from models.__init__
from models import db

class LoginAttempt(db.Model):
    """Model for tracking login attempts and detecting brute force attacks"""
    __tablename__ = 'login_attempts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(255), nullable=True)
    email = Column(String(120), nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # The User model side defines this relationship
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_login_attempts_user_id_timestamp', user_id, timestamp),
        Index('idx_login_attempts_ip_timestamp', ip_address, timestamp),
        Index('idx_login_attempts_success', success),
    )
    
    def __repr__(self):
        return f'<LoginAttempt {self.id}: {self.email} from {self.ip_address} at {self.timestamp}>'

class AccountLockout(db.Model):
    """Model for tracking account lockouts"""
    __tablename__ = 'account_lockouts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    ip_address = Column(String(45), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    locked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    unlock_at = Column(DateTime, nullable=True)
    unlocked_at = Column(DateTime, nullable=True)
    unlocked_by = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # User relationship defined in User model
    admin = relationship('User', foreign_keys=[unlocked_by])
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_account_lockouts_user_id_active', user_id, active),
        Index('idx_account_lockouts_ip_active', ip_address, active),
    )
    
    def __repr__(self):
        return f'<AccountLockout {self.id}: User {self.user_id} locked at {self.locked_at}>'
    
    @property
    def is_expired(self):
        """Check if the lockout has expired"""
        if not self.active:
            return True
        
        if self.unlock_at and self.unlock_at <= datetime.utcnow():
            return True
        
        return False
    
    def unlock(self, admin_id=None):
        """Unlock the account"""
        self.active = False
        self.unlocked_at = datetime.utcnow()
        self.unlocked_by = admin_id
        
        return self

class TwoFactorAuth(db.Model):
    """Model for two-factor authentication settings"""
    __tablename__ = 'two_factor_auth'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    secret_key = Column(String(64), nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # User relationship is defined on the User model side
    backup_codes = relationship('TwoFactorBackupCode', back_populates='two_factor', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TwoFactorAuth {self.id}: User {self.user_id} enabled={self.enabled}>'

class TwoFactorBackupCode(db.Model):
    """Model for two-factor authentication backup codes"""
    __tablename__ = 'two_factor_backup_codes'
    
    id = Column(Integer, primary_key=True)
    two_factor_id = Column(Integer, ForeignKey('two_factor_auth.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(16), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    two_factor = relationship('TwoFactorAuth', back_populates='backup_codes')
    user = relationship('User')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_backup_codes_user_id_used', user_id, used),
    )
    
    def __repr__(self):
        return f'<TwoFactorBackupCode {self.id}: User {self.user_id} used={self.used}>'

class TrustedDevice(db.Model):
    """Model for trusted devices (skip 2FA)"""
    __tablename__ = 'trusted_devices'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    device_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_trusted = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=90), nullable=True)
    
    # Relationships
    user = relationship('User')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_trusted_devices_user_device', user_id, device_id, unique=True),
        Index('idx_trusted_devices_user_trusted', user_id, is_trusted),
    )
    
    def __repr__(self):
        return f'<TrustedDevice {self.id}: User {self.user_id} device {self.name}>'
    
    @property
    def is_expired(self):
        """Check if the trusted device has expired"""
        if not self.is_trusted:
            return True
        
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return True
        
        return False
    
    def refresh(self):
        """Refresh the trusted device expiration"""
        self.last_used = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=90)
        
        return self

class SecurityAuditLog(db.Model):
    """Model for security audit logs"""
    __tablename__ = 'security_audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    event_type = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=True)
    resource_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    meta_data = Column(Text, nullable=True)  # Stored as JSON instead of 'metadata' which is reserved
    severity = Column(String(16), default='INFO', nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_audit_logs_user_timestamp', user_id, timestamp),
        Index('idx_audit_logs_event_type_timestamp', event_type, timestamp),
        Index('idx_audit_logs_severity', severity),
    )
    
    def __repr__(self):
        return f'<SecurityAuditLog {self.id}: {self.event_type} by User {self.user_id} at {self.timestamp}>'

# Add security-related fields to the User model
class AuthToken(db.Model):
    """Model for authentication tokens including API keys, access tokens, and refresh tokens"""
    __tablename__ = 'auth_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_type = Column(String(20), nullable=False)  # 'api', 'access', 'refresh', etc.
    token_value = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    scopes = Column(String(255), nullable=True)  # Comma-separated list of permissions
    
    # Relationships
    user = relationship('User')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_auth_tokens_user_id', user_id),
        Index('idx_auth_tokens_token_value', token_value),
        Index('idx_auth_tokens_expires_at', expires_at),
        Index('idx_auth_tokens_token_type_revoked', token_type, revoked),
    )
    
    def __repr__(self):
        return f'<AuthToken {self.id}: {self.token_type} for User {self.user_id}>'
    
    @property
    def is_expired(self):
        """Check if the token has expired"""
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return True
        return False
    
    @property
    def is_valid(self):
        """Check if the token is valid (not expired and not revoked)"""
        return not self.revoked and not self.is_expired
    
    def revoke(self, reason=None):
        """Revoke the token"""
        self.revoked = True
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason
        return self
    
    def record_usage(self, ip_address=None, user_agent=None):
        """Record token usage"""
        self.last_used_at = datetime.utcnow()
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
        return self
    
    @classmethod
    def generate_token(cls, user_id, token_type, description=None, expires_in=None, 
                      scopes=None, ip_address=None, user_agent=None):
        """Generate a new token
        
        Args:
            user_id: User ID
            token_type: Type of token ('api', 'access', 'refresh', etc.)
            description: Optional description of the token
            expires_in: Optional timedelta for token expiration
            scopes: Optional list of permission scopes
            ip_address: Optional IP address of the client
            user_agent: Optional user agent of the client
            
        Returns:
            Tuple of (token_obj, token_value)
        """
        # Generate a secure random token
        token_value = secrets.token_urlsafe(32)
        
        # Set expiration date if provided
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + expires_in
        
        # Convert scopes list to comma-separated string if provided
        scopes_str = None
        if scopes:
            scopes_str = ','.join(scopes)
        
        # Create token object
        token = cls(
            user_id=user_id,
            token_type=token_type,
            token_value=token_value,
            description=description,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            scopes=scopes_str
        )
        
        return token, token_value


class UserSecurityMixin:
    """Mixin to add security-related fields to the User model"""
    
    # Security fields
    password_last_changed = Column(DateTime, nullable=True)
    reset_token = Column(String(100), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    
    # Account status fields
    account_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime, nullable=True)
    
    # Multi-factor authentication
    requires_2fa = Column(Boolean, default=False, nullable=False)
    
    # Other security settings
    security_level = Column(String(20), default='standard', nullable=False)
    
    # Relationships
    @declared_attr
    def login_attempts(cls):
        return relationship('LoginAttempt', back_populates='user', cascade='all, delete-orphan')
    
    @declared_attr
    def lockouts(cls):
        return relationship('AccountLockout', foreign_keys='AccountLockout.user_id', 
                         back_populates='user', cascade='all, delete-orphan')
    
    @declared_attr
    def two_factor_auth(cls):
        return relationship('TwoFactorAuth', back_populates='user', uselist=False, 
                         cascade='all, delete-orphan')
    
    # Security methods
    def record_login_attempt(self, success, ip_address, user_agent=None):
        """Record a login attempt"""
        attempt = LoginAttempt(
            user_id=self.id,
            ip_address=ip_address,
            user_agent=user_agent,
            email=self.email,
            success=success
        )
        
        if not success:
            self.failed_login_attempts += 1
            self.last_failed_login = datetime.utcnow()
        else:
            # Reset failed login attempts on successful login
            self.failed_login_attempts = 0
            self.last_failed_login = None
        
        db.session.add(attempt)
        return attempt
    
    def lock_account(self, reason, ip_address, duration_hours=24):
        """Lock the user account"""
        self.account_locked = True
        
        # Create a lockout record
        lockout = AccountLockout(
            user_id=self.id,
            ip_address=ip_address,
            reason=reason,
            unlock_at=datetime.utcnow() + timedelta(hours=duration_hours)
        )
        
        db.session.add(lockout)
        return lockout
    
    def unlock_account(self, admin_id=None):
        """Unlock the user account"""
        self.account_locked = False
        self.failed_login_attempts = 0
        
        # Update any active lockouts
        active_lockouts = AccountLockout.query.filter_by(
            user_id=self.id,
            active=True
        ).all()
        
        for lockout in active_lockouts:
            lockout.unlock(admin_id)
        
        return True
    
    def is_locked(self):
        """Check if the account is locked"""
        if not self.account_locked:
            return False
        
        # Check if there are any active lockouts
        active_lockout = AccountLockout.query.filter_by(
            user_id=self.id,
            active=True
        ).first()
        
        if active_lockout and not active_lockout.is_expired:
            return True
        
        # If all lockouts are expired, unlock the account
        if active_lockout and active_lockout.is_expired:
            self.unlock_account()
            return False
        
        return self.account_locked
    
    def get_active_lockout(self):
        """Get the active lockout record if any"""
        return AccountLockout.query.filter_by(
            user_id=self.id,
            active=True
        ).first()
    
    def setup_2fa(self, secret_key):
        """Set up two-factor authentication"""
        if self.two_factor_auth:
            # Update existing 2FA
            self.two_factor_auth.secret_key = secret_key
            self.two_factor_auth.enabled = False  # Requires verification
            self.two_factor_auth.verified = False
        else:
            # Create new 2FA
            tfa = TwoFactorAuth(
                user_id=self.id,
                secret_key=secret_key,
                enabled=False,
                verified=False
            )
            db.session.add(tfa)
        
        return self.two_factor_auth
    
    def enable_2fa(self):
        """Enable two-factor authentication after verification"""
        if not self.two_factor_auth:
            return False
        
        self.two_factor_auth.enabled = True
        self.two_factor_auth.verified = True
        self.requires_2fa = True
        
        # Generate backup codes
        from utils.two_factor import generate_backup_codes
        self.generate_backup_codes()
        
        return True
    
    def disable_2fa(self):
        """Disable two-factor authentication"""
        if not self.two_factor_auth:
            return False
        
        self.two_factor_auth.enabled = False
        self.requires_2fa = False
        
        # Remove backup codes
        TwoFactorBackupCode.query.filter_by(user_id=self.id).delete()
        
        return True
    
    def has_2fa_enabled(self):
        """Check if 2FA is enabled"""
        return self.requires_2fa and self.two_factor_auth and self.two_factor_auth.enabled
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes for 2FA recovery"""
        if not self.two_factor_auth:
            return []
        
        # Clear existing unused backup codes
        TwoFactorBackupCode.query.filter_by(
            user_id=self.id,
            used=False
        ).delete()
        
        # Generate new backup codes
        from utils.two_factor import generate_backup_codes
        codes = generate_backup_codes(count)
        
        # Store the codes
        for code in codes:
            backup_code = TwoFactorBackupCode(
                two_factor_id=self.two_factor_auth.id,
                user_id=self.id,
                code=code.replace('-', '').upper()  # Store without dashes and uppercase
            )
            db.session.add(backup_code)
        
        return codes
    
    def log_security_event(self, event_type, description=None, ip_address=None, 
                          resource_type=None, resource_id=None, metadata=None, severity='INFO'):
        """Log a security event"""
        log = SecurityAuditLog(
            user_id=self.id,
            ip_address=ip_address,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            metadata=metadata,
            severity=severity
        )
        
        db.session.add(log)
        return log