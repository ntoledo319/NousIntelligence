"""
Beta Testing System Models
Database models for beta user management and feature flags
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from database import db

class BetaUser(db.Model):
    """Beta user registration and management"""
    __tablename__ = 'beta_users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    invite_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    flag_set = db.Column(db.JSON, default=dict)  # User-specific feature flags
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='TESTER')  # TESTER, ADMIN, OWNER
    notes = db.Column(db.Text)
    
    # Relationships
    feedback = relationship("BetaFeedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BetaUser {self.email}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invite_code': self.invite_code,
            'flag_set': self.flag_set if self.flag_set is not None else {},
            'joined_at': self.joined_at.isoformat() if self.joined_at is not None else None,
            'is_active': self.is_active,
            'role': self.role,
            'notes': self.notes
        }
    
    def has_flag(self, flag_name):
        """Check if user has specific feature flag enabled"""
        return self.flag_set.get(flag_name, False) if self.flag_set is not None else False
    
    def set_flag(self, flag_name, enabled=True):
        """Set feature flag for user"""
        if self.flag_set is None:
            self.flag_set = {}
        self.flag_set[flag_name] = enabled
    
    def is_owner(self):
        """Check if user is owner/super-admin"""
        return self.role == 'OWNER'
    
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.role in ['ADMIN', 'OWNER']

class BetaFeedback(db.Model):
    """Beta tester feedback storage"""
    __tablename__ = 'beta_feedback'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('beta_users.id'), nullable=False)
    feature_name = db.Column(db.String(100))
    rating = db.Column(db.Integer)  # 1-5 rating
    feedback_text = db.Column(db.Text)
    feedback_data = db.Column(db.JSON)  # Structured feedback data
    page_url = db.Column(db.String(500))
    user_agent = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='NEW')  # NEW, REVIEWED, RESOLVED, CLOSED
    admin_notes = db.Column(db.Text)
    
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
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at is not None else None,
            'status': self.status,
            'admin_notes': self.admin_notes
        }

class FeatureFlag(db.Model):
    """Global feature flags configuration"""
    __tablename__ = 'feature_flags'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_enabled = db.Column(db.Boolean, default=False)
    rollout_percentage = db.Column(db.Integer, default=0)  # 0-100
    target_users = db.Column(db.JSON)  # List of specific user IDs/emails
    conditions = db.Column(db.JSON)  # Conditions for flag activation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(120))  # Admin email who created it
    
    def __repr__(self):
        return f"<FeatureFlag {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'rollout_percentage': self.rollout_percentage,
            'target_users': self.target_users if self.target_users is not None else [],
            'conditions': self.conditions if self.conditions is not None else {},
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None,
            'created_by': self.created_by
        }
    
    def is_enabled_for_user(self, user_email, user_id=None):
        """Check if feature flag is enabled for specific user"""
        if self.is_enabled is False:
            return False
        
        # Check if user is specifically targeted
        if self.target_users is not None and self.target_users:
            if user_email in self.target_users or (user_id and user_id in self.target_users):
                return True
        
        # Check rollout percentage
        if self.rollout_percentage is not None and self.rollout_percentage > 0:
            # Simple hash-based rollout
            import hashlib
            hash_value = int(hashlib.md5(user_email.encode()).hexdigest()[:8], 16)
            return (hash_value % 100) < self.rollout_percentage
        
        return self.rollout_percentage == 100

class SystemMetrics(db.Model):
    """System performance metrics storage"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, db_query, response_time
    metric_value = db.Column(db.Integer)  # Value in appropriate units
    extra_data = db.Column(db.JSON)  # Additional context
    
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