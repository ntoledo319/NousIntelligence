"""
Personal Growth Models

This module defines database models for personal growth features including
goal setting, habit tracking, journaling, and vision boards.

@module models.personal_growth_models
@context_boundary Personal Development
"""

from database import db
from datetime import datetime, date
from sqlalchemy import func
import json


class Goal(db.Model):
    """Model for user goals and objectives"""
    
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # health, career, personal, financial, social
    goal_type = db.Column(db.String(20), default='long_term')  # daily, weekly, monthly, yearly, long_term
    
    # SMART goal components
    specific = db.Column(db.Text)  # What exactly will be accomplished?
    measurable = db.Column(db.Text)  # How will progress be measured?
    achievable = db.Column(db.Text)  # Is it realistic?
    relevant = db.Column(db.Text)  # Why is this goal important?
    time_bound = db.Column(db.Date)  # Target completion date
    
    # Progress tracking
    status = db.Column(db.String(20), default='active')  # active, paused, completed, abandoned
    progress = db.Column(db.Float, default=0.0)  # Percentage
    start_date = db.Column(db.Date, default=date.today)
    completed_date = db.Column(db.Date)
    
    # Parent-child relationships for sub-goals
    parent_goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # VOCAB: SMART Goal - Specific, Measurable, Achievable, Relevant, Time-bound objective
    # Relationships
    user = db.relationship('User', backref='goals')
    sub_goals = db.relationship('Goal', backref=db.backref('parent_goal', remote_side=[id]))
    milestones = db.relationship('GoalMilestone', back_populates='goal', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'goal_type': self.goal_type,
            'status': self.status,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'time_bound': self.time_bound.isoformat() if self.time_bound else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'milestone_count': len(self.milestones)
        }


class GoalMilestone(db.Model):
    """Model for goal milestones and checkpoints"""
    
    __tablename__ = 'goal_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Relationships
    goal = db.relationship('Goal', back_populates='milestones')


class Habit(db.Model):
    """Model for habit tracking"""
    
    __tablename__ = 'habits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # health, productivity, mindfulness, learning
    habit_type = db.Column(db.String(20), default='daily')  # daily, weekly, custom
    
    # Frequency settings
    frequency_type = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    frequency_days = db.Column(db.JSON)  # For weekly: ["mon", "wed", "fri"]
    frequency_count = db.Column(db.Integer, default=1)  # Times per period
    
    # Tracking settings
    tracking_type = db.Column(db.String(20), default='boolean')  # boolean, count, duration
    target_value = db.Column(db.Integer)  # For count/duration types
    unit = db.Column(db.String(20))  # minutes, reps, pages, etc.
    
    # Reminder settings
    reminder_enabled = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.Time)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    archived_at = db.Column(db.DateTime)
    
    # VOCAB: Habit - A regular practice for personal improvement
    # Relationships
    user = db.relationship('User', backref='habits')
    entries = db.relationship('HabitEntry', back_populates='habit', cascade='all, delete-orphan')
    
    def get_streak(self):
        """Calculate current streak for this habit"""
        # Implementation would check HabitEntry records
        return 0


class HabitEntry(db.Model):
    """Model for daily habit completion entries"""
    
    __tablename__ = 'habit_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    value = db.Column(db.Float)  # For count/duration tracking
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    habit = db.relationship('Habit', back_populates='entries')
    
    __table_args__ = (db.UniqueConstraint('habit_id', 'entry_date', name='_habit_entry_uc'),)


class JournalEntry(db.Model):
    """Model for journal/diary entries"""
    
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    entry_type = db.Column(db.String(50), default='general')  # general, gratitude, reflection, dream
    
    # Mood and emotion tracking
    mood_rating = db.Column(db.Integer)  # 1-10 scale
    emotions = db.Column(db.JSON)  # List of emotions
    
    # Privacy settings
    is_private = db.Column(db.Boolean, default=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    
    # Metadata
    weather = db.Column(db.String(50))
    location = db.Column(db.String(100))
    tags = db.Column(db.JSON)  # List of tags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # VOCAB: Journal Entry - Personal reflection or diary entry
    # Relationships
    user = db.relationship('User', backref='journal_entries')
    attachments = db.relationship('JournalAttachment', back_populates='entry', cascade='all, delete-orphan')


class JournalAttachment(db.Model):
    """Model for journal entry attachments (photos, voice notes, etc.)"""
    
    __tablename__ = 'journal_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    attachment_type = db.Column(db.String(20))  # photo, audio, video
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    caption = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    entry = db.relationship('JournalEntry', back_populates='attachments')


class VisionBoard(db.Model):
    """Model for vision boards"""
    
    __tablename__ = 'vision_boards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    theme = db.Column(db.String(50))  # career, health, relationships, personal
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # VOCAB: Vision Board - Visual representation of goals and aspirations
    # Relationships
    user = db.relationship('User', backref='vision_boards')
    items = db.relationship('VisionBoardItem', back_populates='board', cascade='all, delete-orphan')


class VisionBoardItem(db.Model):
    """Model for items on a vision board"""
    
    __tablename__ = 'vision_board_items'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('vision_boards.id'), nullable=False)
    item_type = db.Column(db.String(20))  # image, text, quote, goal_link
    content = db.Column(db.Text)  # URL for images, text for quotes
    caption = db.Column(db.Text)
    position_x = db.Column(db.Float, default=0)  # Position on board
    position_y = db.Column(db.Float, default=0)
    width = db.Column(db.Float, default=200)
    height = db.Column(db.Float, default=200)
    z_index = db.Column(db.Integer, default=0)  # Layering
    style_data = db.Column(db.JSON)  # Additional styling
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Link to goal if applicable
    linked_goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    
    # Relationships
    board = db.relationship('VisionBoard', back_populates='items')
    linked_goal = db.relationship('Goal')


class ReflectionPrompt(db.Model):
    """Model for journaling and reflection prompts"""
    
    __tablename__ = 'reflection_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # gratitude, growth, relationships, goals
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# AI-GENERATED [2024-12-01]
# HUMAN-VALIDATED [2024-12-01]
# NON-NEGOTIABLES: Privacy settings for journal entries must be respected 