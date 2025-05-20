"""
AI Models

This module contains AI-related database models for tracking usage,
costs, and optimizing service selection.
"""

from datetime import datetime
from app_factory import db

class UserAIUsage(db.Model):
    """Track user AI service usage for cost optimization"""
    __tablename__ = 'user_ai_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    service = db.Column(db.String(50))  # e.g., 'openai', 'openrouter'
    model = db.Column(db.String(100))   # e.g., 'gpt-4o', 'claude-3-sonnet'
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float, default=0.0)
    success = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('ai_usage', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'service': self.service,
            'model': self.model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'estimated_cost': self.estimated_cost,
            'success': self.success
        }

class AIServiceConfig(db.Model):
    """Configuration for AI services with usage limits and preferences"""
    __tablename__ = 'ai_service_config'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Lower value = higher priority
    daily_token_limit = db.Column(db.Integer, default=0)  # 0 = no limit
    cost_per_1k_input_tokens = db.Column(db.Float, default=0.0)
    cost_per_1k_output_tokens = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'service_name': self.service_name,
            'enabled': self.enabled,
            'priority': self.priority,
            'daily_token_limit': self.daily_token_limit,
            'cost_per_1k_input_tokens': self.cost_per_1k_input_tokens,
            'cost_per_1k_output_tokens': self.cost_per_1k_output_tokens,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AIModelConfig(db.Model):
    """Configuration for specific AI models with cost and capability settings"""
    __tablename__ = 'ai_model_config'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('ai_service_config.id'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    cost_per_1k_input_tokens = db.Column(db.Float, default=0.0)
    cost_per_1k_output_tokens = db.Column(db.Float, default=0.0)
    capability_level = db.Column(db.Integer, default=1)  # 1=basic, 2=standard, 3=complex
    max_context_length = db.Column(db.Integer, default=4096)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = db.relationship('AIServiceConfig', backref=db.backref('models', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'model_name': self.model_name,
            'enabled': self.enabled,
            'cost_per_1k_input_tokens': self.cost_per_1k_input_tokens,
            'cost_per_1k_output_tokens': self.cost_per_1k_output_tokens,
            'capability_level': self.capability_level,
            'max_context_length': self.max_context_length,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserAIPreferences(db.Model):
    """User preferences for AI services and models"""
    __tablename__ = 'user_ai_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    preferred_service = db.Column(db.String(50))
    preferred_model = db.Column(db.String(100))
    max_daily_cost = db.Column(db.Float, default=0.0)  # 0 = no limit
    enable_cost_optimization = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('ai_preferences', uselist=False, lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_service': self.preferred_service,
            'preferred_model': self.preferred_model,
            'max_daily_cost': self.max_daily_cost,
            'enable_cost_optimization': self.enable_cost_optimization,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }