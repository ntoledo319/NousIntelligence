"""
Beta Testing System Models
Database models for beta user management and feature flags
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BetaUser(Base):
    """Beta user registration and management"""
    __tablename__ = 'beta_users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False, index=True)
    invite_code = Column(String(32), unique=True, nullable=False, index=True)
    flag_set = Column(JSON, default=dict)  # User-specific feature flags
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default='TESTER')  # TESTER, ADMIN, OWNER
    notes = Column(Text)
    
    # Relationships
    feedback = relationship("BetaFeedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BetaUser {self.email}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invite_code': self.invite_code,
            'flag_set': self.flag_set or {},
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_active': self.is_active,
            'role': self.role,
            'notes': self.notes
        }
    
    def has_flag(self, flag_name):
        """Check if user has specific feature flag enabled"""
        return self.flag_set.get(flag_name, False) if self.flag_set else False
    
    def set_flag(self, flag_name, enabled=True):
        """Set feature flag for user"""
        if not self.flag_set:
            self.flag_set = {}
        self.flag_set[flag_name] = enabled
    
    def is_owner(self):
        """Check if user is owner/super-admin"""
        return self.role == 'OWNER'
    
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.role in ['ADMIN', 'OWNER']

class BetaFeedback(Base):
    """Beta tester feedback storage"""
    __tablename__ = 'beta_feedback'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('beta_users.id'), nullable=False)
    feature_name = Column(String(100))
    rating = Column(Integer)  # 1-5 rating
    feedback_text = Column(Text)
    feedback_data = Column(JSON)  # Structured feedback data
    page_url = Column(String(500))
    user_agent = Column(String(500))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='NEW')  # NEW, REVIEWED, RESOLVED, CLOSED
    admin_notes = Column(Text)
    
    # Relationships
    user = relationship("BetaUser", back_populates="feedback")
    
    def __repr__(self):
        return f"<BetaFeedback {self.id} from {self.user.email if self.user else 'Unknown'}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'feature_name': self.feature_name,
            'rating': self.rating,
            'feedback_text': self.feedback_text,
            'feedback_data': self.feedback_data,
            'page_url': self.page_url,
            'user_agent': self.user_agent,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'status': self.status,
            'admin_notes': self.admin_notes
        }

class FeatureFlag(Base):
    """Global feature flags configuration"""
    __tablename__ = 'feature_flags'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)  # 0-100
    target_users = Column(JSON)  # List of specific user IDs/emails
    conditions = Column(JSON)  # Conditions for flag activation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(120))  # Admin email who created it
    
    def __repr__(self):
        return f"<FeatureFlag {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'rollout_percentage': self.rollout_percentage,
            'target_users': self.target_users or [],
            'conditions': self.conditions or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    def is_enabled_for_user(self, user_email, user_id=None):
        """Check if feature flag is enabled for specific user"""
        if not self.is_enabled:
            return False
        
        # Check if user is specifically targeted
        if self.target_users:
            if user_email in self.target_users or (user_id and user_id in self.target_users):
                return True
        
        # Check rollout percentage
        if self.rollout_percentage > 0:
            # Simple hash-based rollout
            import hashlib
            hash_value = int(hashlib.md5(user_email.encode()).hexdigest()[:8], 16)
            return (hash_value % 100) < self.rollout_percentage
        
        return self.rollout_percentage == 100

class SystemMetrics(Base):
    """System performance metrics storage"""
    __tablename__ = 'system_metrics'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, db_query, response_time
    metric_value = Column(Integer)  # Value in appropriate units
    extra_data = Column(JSON)  # Additional context
    
    def __repr__(self):
        return f"<SystemMetrics {self.metric_type}={self.metric_value}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'extra_data': self.extra_data or {}
        }