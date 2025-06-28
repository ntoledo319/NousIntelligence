"""
Language Learning Models

This module contains database models for language learning features including
vocabulary, phrases, grammar rules, and user progress tracking.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import db


class LanguageProfile(db.Model):
    """User's language learning profile and preferences"""
    __tablename__ = 'language_profiles'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    native_language = db.Column(String(10), nullable=False, default='en-US')  # User's native language
    learning_language = db.Column(String(10), nullable=False)  # Language being learned
    proficiency_level = db.Column(String(20), nullable=False, default='beginner')  # beginner, intermediate, advanced
    daily_goal_minutes = db.Column(Integer, default=15)  # Minutes per day goal
    weekly_goal_days = db.Column(Integer, default=5)  # Days per week goal
    focus_areas = db.Column(String(255), default='vocabulary,pronunciation,conversation')  # Comma-separated focus areas
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('language_profiles', lazy=True, cascade='all, delete-orphan'))
    vocabulary_items = db.relationship('VocabularyItem', back_populates='language_profile', cascade='all, delete-orphan')
    learning_sessions = db.relationship('LearningSession', back_populates='language_profile', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LanguageProfile {self.id}: {self.native_language} → {self.learning_language}>'


class VocabularyItem(db.Model):
    """Words or phrases for vocabulary learning"""
    __tablename__ = 'vocabulary_items'

    id = db.Column(Integer, primary_key=True)
    profile_id = db.Column(Integer, db.ForeignKey('language_profiles.id', ondelete='CASCADE'), nullable=False)
    word = db.Column(String(100), nullable=False)  # Word in target language
    translation = db.Column(String(100), nullable=False)  # Translation in native language
    pronunciation = db.Column(String(100))  # Pronunciation guide
    example_sentence = db.Column(Text)  # Example sentence using the word
    notes = db.Column(Text)  # User notes
    part_of_speech = db.Column(String(50))  # Noun, verb, etc.
    difficulty = db.Column(Integer, default=1)  # 1-5 scale
    mastery_level = db.Column(Float, default=0.0)  # 0.0-1.0 scale of mastery
    times_reviewed = db.Column(Integer, default=0)  # Number of review sessions
    last_reviewed = db.Column(DateTime)  # When it was last reviewed
    next_review = db.Column(DateTime)  # When it should be reviewed next (spaced repetition)
    custom_tags = db.Column(String(255))  # User-defined tags
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    language_profile = db.relationship('LanguageProfile', back_populates='vocabulary_items')

    def __repr__(self):
        return f'<VocabularyItem {self.id}: {self.word}>'


class LearningSession(db.Model):
    """Record of a language learning session"""
    __tablename__ = 'learning_sessions'

    id = db.Column(Integer, primary_key=True)
    profile_id = db.Column(Integer, db.ForeignKey('language_profiles.id', ondelete='CASCADE'), nullable=False)
    session_type = db.Column(String(50), nullable=False)  # vocabulary, conversation, grammar, etc.
    duration_minutes = db.Column(Integer, nullable=False)  # How long the session was
    score = db.Column(Float)  # Optional score/performance metric (0-100)
    notes = db.Column(Text)  # User or system notes about the session
    items_covered = db.Column(Integer)  # Number of items/exercises covered
    success_rate = db.Column(Float)  # Percentage of correct answers
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)

    # Relationships
    language_profile = db.relationship('LanguageProfile', back_populates='learning_sessions')

    def __repr__(self):
        return f'<LearningSession {self.id}: {self.session_type} ({self.duration_minutes} min)>'


class ConversationTemplate(db.Model):
    """Templates for guided language practice conversations"""
    __tablename__ = 'conversation_templates'

    id = db.Column(Integer, primary_key=True)
    language = db.Column(String(10), nullable=False)  # Target language code
    difficulty = db.Column(String(20), nullable=False)  # beginner, intermediate, advanced
    category = db.Column(String(50), nullable=False)  # restaurant, travel, business, etc.
    title = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    context = db.Column(Text, nullable=False)  # Setting/scenario description
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompts = db.relationship('ConversationPrompt', back_populates='template', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ConversationTemplate {self.id}: {self.title} ({self.language})>'


class ConversationPrompt(db.Model):
    """Individual prompts within a conversation template"""
    __tablename__ = 'conversation_prompts'

    id = db.Column(Integer, primary_key=True)
    template_id = db.Column(Integer, db.ForeignKey('conversation_templates.id', ondelete='CASCADE'), nullable=False)
    sequence = db.Column(Integer, nullable=False)  # Order in conversation
    role = db.Column(String(50), nullable=False)  # system, assistant, or user
    content = db.Column(Text, nullable=False)  # The prompt text
    expected_responses = db.Column(Text)  # Possible correct responses (for user prompts)
    hint = db.Column(Text)  # Optional hint for the user

    # Relationships
    template = db.relationship('ConversationTemplate', back_populates='prompts')

    def __repr__(self):
        return f'<ConversationPrompt {self.id}: {self.role} #{self.sequence}>'