"""
Health Models

This module contains health-related database models for the NOUS application,
including DBT (Dialectical Behavior Therapy) and AA (Alcoholics Anonymous) models.
"""

from datetime import datetime
from app_factory import db
from sqlalchemy.ext.hybrid import hybrid_property

class DBTSkillRecommendation(db.Model):
    """Recommended DBT skills for specific situations"""
    __tablename__ = 'dbt_skill_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    situation_type = db.Column(db.String(100))
    skill_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    effectiveness_score = db.Column(db.Float, default=0.0)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_recommendations', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'situation_type': self.situation_type,
            'skill_name': self.skill_name,
            'description': self.description,
            'effectiveness_score': self.effectiveness_score,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillLog(db.Model):
    """Log of DBT skills used"""
    __tablename__ = 'dbt_skill_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    situation = db.Column(db.Text)
    effectiveness = db.Column(db.Integer)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_logs', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'situation': self.situation,
            'effectiveness': self.effectiveness,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class DBTCrisisResource(db.Model):
    """Crisis resources for DBT users"""
    __tablename__ = 'dbt_crisis_resources'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100))
    contact_info = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_crisis_resources', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'contact_info': self.contact_info,
            'resource_type': self.resource_type,
            'notes': self.notes,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillCategory(db.Model):
    """Categories for DBT skills"""
    __tablename__ = 'dbt_skill_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class AAAchievement(db.Model):
    """Achievement badges for AA recovery progress"""
    __tablename__ = 'aa_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.String(50))
    badge_name = db.Column(db.String(100))
    badge_description = db.Column(db.Text)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('aa_achievements', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None
        }

class DBTDiaryCard(db.Model):
    """Diary card model for DBT tracking"""
    __tablename__ = 'dbt_diary_cards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    mood_rating = db.Column(db.Integer)  # 1-10
    triggers = db.Column(db.Text)
    urges = db.Column(db.Text)
    skills_used = db.Column(db.Text)
    reflection = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_diary_cards', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'mood_rating': self.mood_rating,
            'triggers': self.triggers,
            'urges': self.urges,
            'skills_used': self.skills_used,
            'reflection': self.reflection,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillChallenge(db.Model):
    """Skill challenge model for DBT practice"""
    __tablename__ = 'dbt_skill_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    progress = db.Column(db.Integer, default=0)  # 0-100
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_challenges', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @hybrid_property
    def is_custom(self):
        """Check if challenge is user-created vs system"""
        return self.user_id is not None

class DBTEmotionTrack(db.Model):
    """Emotion tracking model for DBT"""
    __tablename__ = 'dbt_emotion_tracks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    emotion = db.Column(db.String(50))
    intensity = db.Column(db.Integer)  # 1-10
    trigger = db.Column(db.Text)
    thoughts = db.Column(db.Text)
    behaviors = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_emotion_tracks', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion': self.emotion,
            'intensity': self.intensity,
            'trigger': self.trigger,
            'thoughts': self.thoughts,
            'behaviors': self.behaviors,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }