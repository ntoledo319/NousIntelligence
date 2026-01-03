"""
CBT (Cognitive Behavioral Therapy) Models
Database models for thought records and cognitive distortions
"""
from datetime import datetime
from models.database import db
from sqlalchemy.dialects.postgresql import JSON


class ThoughtRecord(db.Model):
    """CBT thought record for identifying and challenging cognitive distortions"""
    __tablename__ = 'thought_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    situation = db.Column(db.Text, nullable=False)
    automatic_thought = db.Column(db.Text, nullable=False)
    emotions = db.Column(JSON)  # {emotion: intensity (1-10)}
    cognitive_distortions = db.Column(JSON)  # List of identified distortions
    evidence_for = db.Column(db.Text)  # Evidence supporting the thought
    evidence_against = db.Column(db.Text)  # Evidence contradicting the thought
    balanced_thought = db.Column(db.Text)  # Reframed balanced perspective
    outcome_emotions = db.Column(JSON)  # Emotions after reframing
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('thought_records', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'situation': self.situation,
            'automatic_thought': self.automatic_thought,
            'emotions': self.emotions,
            'cognitive_distortions': self.cognitive_distortions,
            'evidence_for': self.evidence_for,
            'evidence_against': self.evidence_against,
            'balanced_thought': self.balanced_thought,
            'outcome_emotions': self.outcome_emotions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CognitiveDistortion(db.Model):
    """Reference table for cognitive distortion types"""
    __tablename__ = 'cognitive_distortions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    examples = db.Column(JSON)  # List of example thoughts
    counter_questions = db.Column(JSON)  # Questions to challenge the distortion
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'examples': self.examples,
            'counter_questions': self.counter_questions
        }


class MoodEntry(db.Model):
    """Daily mood tracking"""
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    mood_rating = db.Column(db.Integer, nullable=False)  # 1-10 scale
    emotions = db.Column(JSON)  # Detailed emotion breakdown
    note = db.Column(db.Text)
    activities = db.Column(JSON)  # What user was doing
    energy_level = db.Column(db.Integer)  # 1-10 scale
    sleep_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('mood_entries', lazy=True, cascade='all, delete-orphan'))
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('mood_rating >= 1 AND mood_rating <= 10', name='valid_mood_rating'),
        db.CheckConstraint('energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 10)', name='valid_energy_level'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood_rating': self.mood_rating,
            'emotions': self.emotions,
            'note': self.note,
            'activities': self.activities,
            'energy_level': self.energy_level,
            'sleep_hours': self.sleep_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
