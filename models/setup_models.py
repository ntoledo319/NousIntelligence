"""
Setup Wizard Models

Database models for the initial user setup and onboarding process.
"""

from datetime import datetime
from database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class SetupProgress(db.Model):
    """Track user progress through setup wizard"""
    __tablename__ = 'setup_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Setup completion tracking
    is_completed = db.Column(db.Boolean, default=False)
    current_step = db.Column(db.String(50), default='welcome')
    completed_steps = db.Column(db.JSON, default=list)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('setup_progress', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_completed': self.is_completed,
            'current_step': self.current_step,
            'completed_steps': self.completed_steps or [],
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserPreferences(db.Model):
    """Comprehensive user preferences from setup wizard"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Language preferences
    primary_language = db.Column(db.String(10), default='en-US')
    secondary_languages = db.Column(db.JSON, default=list)  # Additional languages user speaks
    learning_languages = db.Column(db.JSON, default=list)  # Languages user wants to learn
    
    # Neurodivergent support
    is_neurodivergent = db.Column(db.Boolean, default=False)
    neurodivergent_conditions = db.Column(db.JSON, default=list)  # ADHD, Autism, etc.
    
    # Theme and aesthetics
    theme_preference = db.Column(db.String(20), default='auto')  # light, dark, auto
    color_scheme = db.Column(db.String(20), default='blue')
    font_size = db.Column(db.String(10), default='medium')
    high_contrast = db.Column(db.Boolean, default=False)
    
    # Mental health goals
    mental_health_goals = db.Column(db.JSON, default=list)
    therapeutic_approach = db.Column(db.String(20), default='integrated')  # dbt, cbt, integrated
    crisis_support_enabled = db.Column(db.Boolean, default=True)
    
    # AI Assistant preferences
    assistant_personality = db.Column(db.String(20), default='empathetic')
    assistant_tone = db.Column(db.String(20), default='compassionate')
    communication_style = db.Column(db.String(20), default='balanced')
    ai_assistance_level = db.Column(db.String(20), default='responsive')
    
    # Health and wellness
    health_tracking_interests = db.Column(db.JSON, default=list)
    wellness_goals = db.Column(db.JSON, default=list)
    reminder_preferences = db.Column(db.JSON, default=dict)
    
    # Notifications and privacy
    notification_frequency = db.Column(db.String(20), default='medium')
    data_privacy_level = db.Column(db.String(20), default='full')
    sharing_preferences = db.Column(db.JSON, default=dict)
    
    # Accessibility
    voice_interface_enabled = db.Column(db.Boolean, default=True)
    voice_interface_mode = db.Column(db.String(20), default='push-to-talk')
    motor_accessibility = db.Column(db.JSON, default=dict)
    cognitive_support_level = db.Column(db.String(20), default='standard')
    
    # Integration preferences
    google_services_integration = db.Column(db.JSON, default=dict)
    spotify_integration_enabled = db.Column(db.Boolean, default=True)
    external_integrations = db.Column(db.JSON, default=dict)
    
    # Emergency and safety
    emergency_contacts = db.Column(db.JSON, default=list)
    safety_planning_enabled = db.Column(db.Boolean, default=True)
    location_services_enabled = db.Column(db.Boolean, default=False)
    
    # Financial management
    budget_tracking_enabled = db.Column(db.Boolean, default=False)
    financial_privacy_level = db.Column(db.String(20), default='full')
    
    # Collaboration
    family_features_enabled = db.Column(db.Boolean, default=False)
    collaboration_level = db.Column(db.String(20), default='private')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', uselist=False))
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'primary_language': self.primary_language,
            'secondary_languages': self.secondary_languages or [],
            'learning_languages': self.learning_languages or [],
            'is_neurodivergent': self.is_neurodivergent,
            'neurodivergent_conditions': self.neurodivergent_conditions or [],
            'theme_preference': self.theme_preference,
            'color_scheme': self.color_scheme,
            'font_size': self.font_size,
            'high_contrast': self.high_contrast,
            'mental_health_goals': self.mental_health_goals or [],
            'therapeutic_approach': self.therapeutic_approach,
            'crisis_support_enabled': self.crisis_support_enabled,
            'assistant_personality': self.assistant_personality,
            'assistant_tone': self.assistant_tone,
            'communication_style': self.communication_style,
            'ai_assistance_level': self.ai_assistance_level,
            'health_tracking_interests': self.health_tracking_interests or [],
            'wellness_goals': self.wellness_goals or [],
            'reminder_preferences': self.reminder_preferences or {},
            'notification_frequency': self.notification_frequency,
            'data_privacy_level': self.data_privacy_level,
            'sharing_preferences': self.sharing_preferences or {},
            'voice_interface_enabled': self.voice_interface_enabled,
            'voice_interface_mode': self.voice_interface_mode,
            'motor_accessibility': self.motor_accessibility or {},
            'cognitive_support_level': self.cognitive_support_level,
            'google_services_integration': self.google_services_integration or {},
            'spotify_integration_enabled': self.spotify_integration_enabled,
            'external_integrations': self.external_integrations or {},
            'emergency_contacts': self.emergency_contacts or [],
            'safety_planning_enabled': self.safety_planning_enabled,
            'location_services_enabled': self.location_services_enabled,
            'budget_tracking_enabled': self.budget_tracking_enabled,
            'financial_privacy_level': self.financial_privacy_level,
            'family_features_enabled': self.family_features_enabled,
            'collaboration_level': self.collaboration_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }