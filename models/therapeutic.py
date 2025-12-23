"""
Therapeutic Models

This module defines models for persistent state tracking in therapeutic contexts,
including session state, mood logs, crisis plans, and clinical profiles.
"""

from models.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class TherapySession(db.Model):
    """Tracks the state of an active therapeutic interaction (e.g. CBT Thought Record)"""
    __tablename__ = 'therapy_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Session Context
    module_id = db.Column(db.String(50), nullable=False)  # e.g., 'cbt_thought_record', 'dbt_tipp'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # State Machine Data
    current_step = db.Column(db.String(50))  # e.g., 'identify_emotion'
    variables = db.Column(db.JSON, default={})  # Store answers, partial thoughts

    # Relationships
    user = db.relationship('User', backref='therapy_sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'current_step': self.current_step,
            'variables': self.variables,
            'is_active': self.is_active,
            'started_at': self.started_at.isoformat()
        }

class MoodLog(db.Model):
    """Stores user mood entries for tracking over time"""
    __tablename__ = 'mood_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood_label = db.Column(db.String(50), nullable=False)  # e.g., 'Anxious', 'Happy'
    intensity = db.Column(db.Integer)  # 1-10 scale
    note = db.Column(db.Text)
    tags = db.Column(db.JSON, default=[])  # e.g., ['work', 'morning']

    # Relationships
    user = db.relationship('User', backref='mood_logs')

class CrisisPlan(db.Model):
    """User-specific safety plan for crisis management"""
    __tablename__ = 'crisis_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Safety Plan Components
    warning_signs = db.Column(db.JSON, default=[])
    coping_strategies = db.Column(db.JSON, default=[])  # Internal coping
    social_distractions = db.Column(db.JSON, default=[])  # People/Places to distract
    support_contacts = db.Column(db.JSON, default=[])  # Friends/Family names & numbers
    professional_contacts = db.Column(db.JSON, default=[])  # Doctors/Therapists
    environment_safety = db.Column(db.Text)  # How to make environment safe
    reasons_to_live = db.Column(db.JSON, default=[])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('crisis_plan', uselist=False))

class TherapyProfile(db.Model):
    """Clinical profile: preferences, history, and goals"""
    __tablename__ = 'therapy_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Preferences
    communication_style = db.Column(db.String(50), default='warm')  # 'direct', 'warm', 'humorous'
    preferred_modalities = db.Column(db.JSON, default=[])  # ['cbt', 'dbt']
    disliked_exercises = db.Column(db.JSON, default=[])

    # Goals (SMART)
    goals = db.Column(db.JSON, default=[])  # List of objects {text, target_date, progress}

    # History/Context
    challenges = db.Column(db.JSON, default=[])  # ['anxiety', 'sleep']
    strengths = db.Column(db.JSON, default=[])  # User strengths for positive psych

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('therapy_profile', uselist=False))
