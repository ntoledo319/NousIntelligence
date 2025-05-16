from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
import numpy as np
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy import UniqueConstraint, func, text, Index
import json
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

# Enum for conversation difficulty levels
class ConversationDifficulty(enum.Enum):
    BEGINNER = "beginner"        # Simple language, basic concepts, extra explanations
    INTERMEDIATE = "intermediate"  # Standard language, more technical terms
    ADVANCED = "advanced"        # Technical language, assumes domain knowledge
    EXPERT = "expert"            # Highly technical, specialized terminology

# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    profile_image_url = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    account_active = db.Column(db.Boolean, default=True)  # Renamed to avoid conflict with UserMixin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    password_hash = db.Column(db.String(256), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Two-factor authentication fields
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    
    # Relationship with user settings
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade="all, delete-orphan")
    
    # Relationship with assistant profile (must be defined after AssistantProfile class)
    assistant = db.relationship('AssistantProfile', 
                               foreign_keys='AssistantProfile.user_id',
                               backref=db.backref('owner', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    
    # Relationship with memory entries
    memory_entries = db.relationship('UserMemoryEntry', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with topic interests
    topic_interests = db.relationship('UserTopicInterest', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with entity memories
    entity_memories = db.relationship('UserEntityMemory', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with backup codes
    backup_codes = db.relationship('TwoFactorBackupCode', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def is_administrator(self):
        """Check if user has admin privileges"""
        return self.is_admin
    
    # Override UserMixin's is_active property to use our account_active field
    @property
    def is_active(self):
        """Return whether the user account is active"""
        return self.account_active
    
    @is_active.setter
    def is_active(self, value):
        """Set whether the user account is active"""
        self.account_active = value
    
    def set_password(self, password):
        """Set user password with secure hashing"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check a password against the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        """Required by Flask-Login"""
        return True
    
    @property
    def is_anonymous(self):
        """Required by Flask-Login"""
        return False
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_active', 'account_active'),
    )

# TwoFactorBackupCode model for 2FA recovery codes
class TwoFactorBackupCode(db.Model):
    """Model for storing two-factor authentication backup codes"""
    __tablename__ = 'two_factor_backup_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)  # Stores hashed backup code
    used = db.Column(db.Boolean, default=False)  # Whether this code has been used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)  # When the code was used
    
    __table_args__ = (
        Index('idx_backup_codes_user_id', 'user_id'),
        Index('idx_backup_codes_used', 'used'),
    )
    
    def __repr__(self):
        return f'<TwoFactorBackupCode {self.id} (User: {self.user_id}, Used: {self.used})>'
    
    def use_code(self):
        """Mark this code as used"""
        self.used = True
        self.used_at = datetime.utcnow()

# UserSettings model to store user preferences
class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    conversation_difficulty = db.Column(db.String(20), default=ConversationDifficulty.INTERMEDIATE.value)
    enable_voice_responses = db.Column(db.Boolean, default=False)
    preferred_language = db.Column(db.String(10), default='en-US')
    theme = db.Column(db.String(20), default='light')
    color_theme = db.Column(db.String(20), default='default')
    
    # AI Character customization
    ai_name = db.Column(db.String(30), default='NOUS')
    ai_personality = db.Column(db.String(20), default='helpful')
    ai_formality = db.Column(db.String(20), default='casual')  # casual, neutral, formal
    ai_verbosity = db.Column(db.String(20), default='balanced')  # concise, balanced, detailed  
    ai_enthusiasm = db.Column(db.String(20), default='moderate')  # low, moderate, high
    ai_emoji_usage = db.Column(db.String(20), default='occasional')  # none, occasional, frequent
    ai_voice_type = db.Column(db.String(20), default='neutral')  # neutral, warm, authoritative, energetic, calm
    ai_backstory = db.Column(db.Text, nullable=True)  # Custom backstory for the AI
    
    # Setup wizard progress tracking
    setup_progress = db.Column(db.Text)  # JSON string to track setup wizard progress
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=False)
    
    # Feature settings
    medication_reminders = db.Column(db.Boolean, default=False)
    pain_tracking = db.Column(db.Boolean, default=False)
    mindfulness_features = db.Column(db.Boolean, default=False)
    shopping_lists = db.Column(db.Boolean, default=False)
    product_tracking = db.Column(db.Boolean, default=False)
    budget_reminder_enabled = db.Column(db.Boolean, default=False)
    weather_alerts = db.Column(db.Boolean, default=False)
    travel_planning = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conversation_difficulty': self.conversation_difficulty,
            'enable_voice_responses': self.enable_voice_responses,
            'preferred_language': self.preferred_language,
            'theme': self.theme,
            'ai_name': self.ai_name,
            'ai_personality': self.ai_personality,
            'ai_formality': self.ai_formality,
            'ai_verbosity': self.ai_verbosity,
            'ai_enthusiasm': self.ai_enthusiasm,
            'ai_emoji_usage': self.ai_emoji_usage,
            'ai_voice_type': self.ai_voice_type,
            'ai_backstory': self.ai_backstory
        }

# OAuth model for token storage
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

# AssistantProfile model for customizing the assistant
class AssistantProfile(db.Model):
    __tablename__ = 'assistant_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for default profile
    
    # Basic information
    name = db.Column(db.String(50), nullable=False, default="NOUS")  # Internal name
    display_name = db.Column(db.String(50), nullable=False, default="NOUS")  # Name shown to user
    tagline = db.Column(db.String(100))  # Short description/tagline
    description = db.Column(db.Text)  # Longer description
    
    # Appearance
    primary_color = db.Column(db.String(20), default="#6f42c1")  # Primary color in hex
    theme = db.Column(db.String(20), default="dark")  # dark, light
    logo_path = db.Column(db.String(255))  # Path to logo image
    
    # Behavior
    personality = db.Column(db.String(50), default="friendly")  # Affects tone and style
    
    # Flags
    is_default = db.Column(db.Boolean, default=False)  # Whether this is the default profile
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'tagline': self.tagline,
            'description': self.description,
            'primary_color': self.primary_color,
            'theme': self.theme,
            'personality': self.personality,
            'is_default': self.is_default,
            'logo_path': self.logo_path,
        }
    
# Beta tester model
class BetaTester(db.Model):
    """Model for managing beta testers"""
    __tablename__ = 'beta_testers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, unique=True)
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive'
    notes = db.Column(db.Text, nullable=True)
    feedback_count = db.Column(db.Integer, default=0)  # Count of feedback submissions
    last_activity = db.Column(db.DateTime, nullable=True)
    activated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deactivated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('beta_tester', uselist=False))
    
    # Relationship with feedback
    feedback = db.relationship('BetaFeedback', backref='tester', lazy='dynamic', cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'feedback_count': self.feedback_count,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'deactivated_at': self.deactivated_at.isoformat() if self.deactivated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Beta feedback model
class BetaFeedback(db.Model):
    """Model for feedback from beta testers"""
    __tablename__ = 'beta_feedback'
    id = db.Column(db.Integer, primary_key=True)
    tester_id = db.Column(db.Integer, db.ForeignKey('beta_testers.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'bug', 'feature', 'suggestion', 'general'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, default=3)  # 1-5 scale (1:critical, 5:trivial)
    status = db.Column(db.String(20), default='new')  # 'new', 'in_progress', 'resolved', 'wont_fix'
    resolution_notes = db.Column(db.Text, nullable=True)
    screenshots = db.Column(db.Text, nullable=True)  # JSON array of screenshot URLs or base64 data
    browser = db.Column(db.String(100), nullable=True)  # Browser info
    device = db.Column(db.String(100), nullable=True)  # Device info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'tester_id': self.tester_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'resolution_notes': self.resolution_notes,
            'screenshots': self.screenshots,
            'browser': self.browser,
            'device': self.device,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Enhanced Memory Models for Personalized Conversation

class UserMemoryEntry(db.Model):
    """Stores conversation message history"""
    __tablename__ = 'user_memory_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    importance = db.Column(db.Integer, default=1)  # 1-5 scale
    embedding = db.Column(db.Text, nullable=True)  # Vector embedding for semantic search
    
    user = db.relationship(User, backref='memory_entries')
    
    __table_args__ = (
        Index('idx_memory_user_timestamp', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserMemoryEntry {self.id}: {self.role} at {self.timestamp}>"

class UserTopicInterest(db.Model):
    """Tracks user interests in topics based on conversation history"""
    __tablename__ = 'user_topic_interests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    topic_name = db.Column(db.String(50), nullable=False)
    interest_level = db.Column(db.Float, default=0.5)  # 0-1 scale
    last_discussed = db.Column(db.DateTime, default=datetime.utcnow)
    engagement_count = db.Column(db.Integer, default=1)  # How many times mentioned
    
    user = db.relationship(User, backref='topic_interests')
    
    __table_args__ = (UniqueConstraint(
        'user_id', 
        'topic_name',
        name='uq_user_topic'
    ),)
    
    def __repr__(self):
        return f"<UserTopicInterest {self.topic_name}: level {self.interest_level}>"

class UserEntityMemory(db.Model):
    """Stores information about entities (people, places, things) mentioned by the user"""
    __tablename__ = 'user_entity_memories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    entity_name = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # person, place, thing, etc.
    attributes = db.Column(db.JSON, nullable=False)
    last_mentioned = db.Column(db.DateTime, default=datetime.utcnow)
    mention_count = db.Column(db.Integer, default=1)
    
    user = db.relationship(User, backref='entity_memories')
    
    __table_args__ = (UniqueConstraint(
        'user_id', 
        'entity_name',
        name='uq_user_entity'
    ),)
    
    def __repr__(self):
        return f"<UserEntityMemory {self.entity_name} ({self.entity_type})>"

class UserEmotionLog(db.Model):
    """Logs detected user emotions from interactions"""
    __tablename__ = 'user_emotion_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    emotion = db.Column(db.String(30), nullable=False)  # happiness, sadness, anger, etc.
    confidence = db.Column(db.Float, default=0.0)  # 0-1 scale of detection confidence
    source = db.Column(db.String(20), nullable=False)  # 'text', 'voice', 'image'
    details = db.Column(db.Text, nullable=True)  # Optional details about the emotion
    
    user = db.relationship(User, backref='emotion_logs')
    
    def __repr__(self):
        return f"<UserEmotionLog {self.emotion} ({self.confidence:.2f}) at {self.timestamp}>"
    
# Third-party service connections for users
class UserConnection(db.Model):
    __tablename__ = 'user_connections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    service = db.Column(db.String(50), nullable=False)  # 'google', 'spotify', etc.
    token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_uri = db.Column(db.String(255), nullable=True)
    client_id = db.Column(db.String(255), nullable=True)
    client_secret = db.Column(db.String(255), nullable=True)
    scopes = db.Column(db.Text, nullable=True)  # JSON string of scopes
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('connections', lazy=True))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'service', name='uq_user_service'),
    )

# Enum for DBT (Dialectical Behavior Therapy) skills
class DBTSkillCategory(enum.Enum):
    MINDFULNESS = "Mindfulness"
    DISTRESS_TOLERANCE = "Distress Tolerance"
    EMOTION_REGULATION = "Emotion Regulation"
    INTERPERSONAL_EFFECTIVENESS = "Interpersonal Effectiveness"
    RADICAL_ACCEPTANCE = "Radical Acceptance"
    WISE_MIND = "Wise Mind"
    DIALECTICS = "Dialectics"
    OTHER = "Other"

# DBT Skills log model
class DBTSkillLog(db.Model):
    """Model for tracking DBT skill usage"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Uses DBTSkillCategory values
    situation = db.Column(db.Text)  # The situation where the skill was used
    effectiveness = db.Column(db.Integer)  # Rating from 1-5 of how effective the skill was
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category,
            'situation': self.situation,
            'effectiveness': self.effectiveness,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# DBT Diary Card model
class DBTDiaryCard(db.Model):
    """Model for DBT diary cards"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    date = db.Column(db.Date, default=datetime.utcnow().date)
    mood_rating = db.Column(db.Integer)  # 0-5 scale
    triggers = db.Column(db.Text)  # What triggered emotions
    urges = db.Column(db.Text)  # Urges felt
    skills_used = db.Column(db.Text)  # Skills used
    reflection = db.Column(db.Text)  # Reflection notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'mood_rating': self.mood_rating,
            'triggers': self.triggers,
            'urges': self.urges,
            'skills_used': self.skills_used,
            'reflection': self.reflection,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# DBT Skill Recommendation model
class DBTSkillRecommendation(db.Model):
    """Model for personalized skill recommendations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    situation_type = db.Column(db.String(100))  # General type of situation
    skill_name = db.Column(db.String(100))  # Recommended skill
    category = db.Column(db.String(50))  # Skill category
    confidence_score = db.Column(db.Float, default=0.0)  # How confident we are in this recommendation (0.0-1.0)
    times_used = db.Column(db.Integer, default=0)  # How many times user has used this skill
    avg_effectiveness = db.Column(db.Float, default=0.0)  # Average effectiveness rating (0.0-5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'situation_type': self.situation_type,
            'skill_name': self.skill_name,
            'category': self.category,
            'confidence_score': self.confidence_score,
            'times_used': self.times_used,
            'avg_effectiveness': self.avg_effectiveness
        }

# DBT Skill Challenge model
class DBTSkillChallenge(db.Model):
    """Model for DBT skill challenges"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    challenge_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    skill_category = db.Column(db.String(50))  # Primary skill category for this challenge
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    is_completed = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)  # Progress percentage (0-100)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'challenge_name': self.challenge_name,
            'description': self.description,
            'skill_category': self.skill_category,
            'difficulty': self.difficulty,
            'is_completed': self.is_completed,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }

# Crisis Resource model
class DBTCrisisResource(db.Model):
    """Model for crisis resources"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))  # e.g., hotline, therapist, hospital
    notes = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_info': self.contact_info,
            'resource_type': self.resource_type,
            'notes': self.notes,
            'is_emergency': self.is_emergency
        }

# Emotion Tracking model
class DBTEmotionTrack(db.Model):
    """Model for tracking emotions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    emotion_name = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Integer)  # 1-10 scale
    trigger = db.Column(db.Text)
    body_sensations = db.Column(db.Text)  # Physical sensations
    thoughts = db.Column(db.Text)  # Associated thoughts
    urges = db.Column(db.Text)  # Action urges
    opposite_action = db.Column(db.Text)  # Opposite action taken
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion_name': self.emotion_name,
            'intensity': self.intensity,
            'trigger': self.trigger,
            'body_sensations': self.body_sensations,
            'thoughts': self.thoughts,
            'urges': self.urges,
            'opposite_action': self.opposite_action,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }

# Enum for expense categories
class ExpenseCategory(enum.Enum):
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    FOOD = "Food"
    UTILITIES = "Utilities"
    INSURANCE = "Insurance"
    HEALTHCARE = "Healthcare"
    SAVINGS = "Savings"
    PERSONAL = "Personal"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education" 
    DEBT = "Debt"
    GIFTS = "Gifts"
    TRAVEL = "Travel"
    OTHER = "Other"

class Doctor(db.Model):
    """Model for storing doctor information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with appointments
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_doctor_user', 'user_id'),
        Index('idx_doctor_name', 'name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes
        }

class Appointment(db.Model):
    """Model for tracking appointment history and upcoming appointments"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    
    __table_args__ = (
        Index('idx_appointment_user', 'user_id'),
        Index('idx_appointment_doctor', 'doctor_id'),
        Index('idx_appointment_date', 'date'),
        Index('idx_appointment_status', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat() if self.date else None,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes
        }

class AppointmentReminder(db.Model):
    """Model for storing when to remind users about making appointments"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    frequency_months = db.Column(db.Integer, default=6)  # How often to see this doctor (in months)
    last_appointment = db.Column(db.DateTime)  # Date of the last appointment
    next_reminder = db.Column(db.DateTime)  # When to remind about making the next appointment
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Shopping List and Grocery Features
class ShoppingList(db.Model):
    """Model for shopping/grocery lists"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    store = db.Column(db.String(100))  # Optional store name
    is_recurring = db.Column(db.Boolean, default=False)  # If this is a recurring order list
    frequency_days = db.Column(db.Integer, default=0)  # For recurring orders, every X days
    next_order_date = db.Column(db.DateTime)  # For recurring orders
    last_ordered = db.Column(db.DateTime)  # When this list was last ordered
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with items
    items = db.relationship('ShoppingItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'store': self.store,
            'is_recurring': self.is_recurring,
            'frequency_days': self.frequency_days,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None,
            'items_count': len(self.items) if self.items else 0
        }

class ShoppingItem(db.Model):
    """Model for items in a shopping list"""
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # e.g., Produce, Dairy, etc.
    quantity = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(20))  # e.g., lbs, oz, etc.
    notes = db.Column(db.String(255))
    is_checked = db.Column(db.Boolean, default=False)  # For checked off items
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'is_checked': self.is_checked,
            'priority': self.priority
        }

# Prescription and Medication Management
class Medication(db.Model):
    """Model for tracking medications"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))  # e.g., 10mg
    instructions = db.Column(db.Text)  # e.g., Take twice daily with food
    prescription_number = db.Column(db.String(50))
    pharmacy = db.Column(db.String(100))
    pharmacy_phone = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    quantity_remaining = db.Column(db.Integer)  # Pills/doses remaining
    refills_remaining = db.Column(db.Integer, default=0)
    refill_reminder_threshold = db.Column(db.Integer, default=7)  # Remind when X days of medicine left
    next_refill_date = db.Column(db.DateTime)
    last_refilled = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_medication_user', 'user_id'),
        Index('idx_medication_doctor', 'doctor_id'),
        Index('idx_medication_refill_date', 'next_refill_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dosage': self.dosage,
            'instructions': self.instructions,
            'prescription_number': self.prescription_number,
            'pharmacy': self.pharmacy,
            'doctor_name': Doctor.query.get(self.doctor_id).name if self.doctor_id and Doctor.query.get(self.doctor_id) else None,
            'quantity_remaining': self.quantity_remaining,
            'refills_remaining': self.refills_remaining,
            'next_refill_date': self.next_refill_date.isoformat() if self.next_refill_date else None,
            'days_remaining': (self.next_refill_date - datetime.datetime.now()).days if self.next_refill_date else None
        }

# E-commerce Product Ordering
class Product(db.Model):
    """Model for tracking favorite or recurring products to order"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(255))  # Link to the product
    image_url = db.Column(db.String(255))  # Product image
    price = db.Column(db.Float)  # Last known price
    source = db.Column(db.String(50))  # e.g., Amazon, Target, etc.
    is_recurring = db.Column(db.Boolean, default=False)  # If this is a recurring order
    frequency_days = db.Column(db.Integer, default=0)  # For recurring orders, every X days
    next_order_date = db.Column(db.DateTime)  # For recurring orders
    last_ordered = db.Column(db.DateTime)  # When this product was last ordered
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'price': self.price,
            'source': self.source,
            'is_recurring': self.is_recurring,
            'frequency_days': self.frequency_days,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None
        }
        
# Budget & Expense Tracking Models

class Budget(db.Model):
    """Model for budget categories and limits"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Uses ExpenseCategory values
    amount = db.Column(db.Float, nullable=False)  # Monthly budget amount
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)  # For fixed-period budgets
    is_recurring = db.Column(db.Boolean, default=True)  # Monthly recurring by default
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with expenses
    expenses = db.relationship('Expense', backref='budget', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'amount': self.amount,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_recurring': self.is_recurring,
            'spent': sum(expense.amount for expense in self.expenses) if self.expenses else 0,
            'remaining': self.amount - sum(expense.amount for expense in self.expenses) if self.expenses else self.amount
        }

class Expense(db.Model):
    """Model for tracking expenses"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))  # Uses ExpenseCategory values
    payment_method = db.Column(db.String(50))  # e.g., cash, credit card, etc.
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    next_due_date = db.Column(db.DateTime)  # For recurring expenses
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'category': self.category,
            'payment_method': self.payment_method,
            'budget_name': self.budget.name if self.budget else None,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'notes': self.notes
        }

class RecurringPayment(db.Model):
    """Model for tracking recurring payments"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_day = db.Column(db.Integer)  # Day of month when payment is due
    frequency = db.Column(db.String(20), nullable=False)  # monthly, yearly, etc.
    category = db.Column(db.String(50))  # Uses ExpenseCategory values
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)  # For fixed-term payments
    next_due_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    website = db.Column(db.String(255))  # For online payments
    notes = db.Column(db.Text)
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'due_day': self.due_day,
            'frequency': self.frequency,
            'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'payment_method': self.payment_method,
            'website': self.website,
            'notes': self.notes
        }

# Travel Planning Models

class Trip(db.Model):
    """Model for storing trip information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    budget = db.Column(db.Float)  # Budget for the trip
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    itinerary_items = db.relationship('ItineraryItem', backref='trip', lazy=True, cascade="all, delete-orphan")
    accommodations = db.relationship('Accommodation', backref='trip', lazy=True, cascade="all, delete-orphan")
    travel_documents = db.relationship('TravelDocument', backref='trip', lazy=True, cascade="all, delete-orphan")
    packing_items = db.relationship('PackingItem', backref='trip', lazy=True, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_trip_user', 'user_id'),
        Index('idx_trip_dates', 'start_date', 'end_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
            'budget': self.budget,
            'duration': (self.end_date - self.start_date).days if self.start_date and self.end_date else None,
            'itinerary_count': len(self.itinerary_items) if self.itinerary_items else 0,
            'accommodation_count': len(self.accommodations) if self.accommodations else 0,
            'document_count': len(self.travel_documents) if self.travel_documents else 0,
            'packed_items': sum(1 for item in self.packing_items if item.is_packed) if self.packing_items else 0,
            'total_items': len(self.packing_items) if self.packing_items else 0
        }

class ItineraryItem(db.Model):
    """Model for trip itinerary items"""
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(255))
    address = db.Column(db.String(255))
    reservation_confirmation = db.Column(db.String(100))
    category = db.Column(db.String(50))  # e.g., activity, transportation, meal
    notes = db.Column(db.Text)
    cost = db.Column(db.Float)  # Cost of this activity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'address': self.address,
            'reservation_confirmation': self.reservation_confirmation,
            'category': self.category,
            'notes': self.notes,
            'cost': self.cost
        }

class Accommodation(db.Model):
    """Model for trip accommodations"""
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    check_in_date = db.Column(db.DateTime)
    check_out_date = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    booking_confirmation = db.Column(db.String(100))
    booking_site = db.Column(db.String(100))  # e.g., Airbnb, Booking.com
    phone = db.Column(db.String(20))
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'name': self.name,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'address': self.address,
            'booking_confirmation': self.booking_confirmation,
            'booking_site': self.booking_site,
            'phone': self.phone,
            'cost': self.cost,
            'notes': self.notes
        }

class TravelDocument(db.Model):
    """Model for storing travel documents"""
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(50))  # e.g., flight, train, rental car
    confirmation_number = db.Column(db.String(100))
    provider = db.Column(db.String(100))  # e.g., airline, rail company
    departure_location = db.Column(db.String(100))
    arrival_location = db.Column(db.String(100))
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'name': self.name,
            'document_type': self.document_type,
            'confirmation_number': self.confirmation_number,
            'provider': self.provider,
            'departure_location': self.departure_location,
            'arrival_location': self.arrival_location,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'notes': self.notes,
            'cost': self.cost
        }

class PackingItem(db.Model):
    """Model for trip packing list items"""
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # e.g., clothing, toiletries, documents
    quantity = db.Column(db.Integer, default=1)
    is_packed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'is_packed': self.is_packed,
            'notes': self.notes
        }


class WeatherLocation(db.Model):
    """Model for storing saved weather locations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # User-provided name for this location
    display_name = db.Column(db.String(255))  # Full formatted location name from API
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # If this is the user's main location
    units = db.Column(db.String(20), default="imperial")  # imperial or metric
    user_id = db.Column(db.String(255))  # User identifier (from session)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    
    __table_args__ = (
        Index('idx_weather_user', 'user_id'),
        Index('idx_weather_primary', 'is_primary'),
        Index('idx_weather_coords', 'latitude', 'longitude'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_primary': self.is_primary,
            'units': self.units,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

# Knowledge Base Models for AI Self-Learning
class KnowledgeBase(db.Model):
    """
    Stores learned information in the knowledge base.
    Each entry contains content and its embedding for semantic search.
    """
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=True)  # Can be null for global knowledge
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)  # Store embedding as binary
    source = db.Column(db.String(50), default='conversation')  # conversation, training, reflection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)  # Track when this was last retrieved
    access_count = db.Column(db.Integer, default=0)  # How many times this knowledge was accessed
    relevance_score = db.Column(db.Float, default=1.0)  # Higher = more relevant (for pruning)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('knowledge_entries', lazy=True))
    
    __table_args__ = (
        Index('idx_knowledge_user_relevance', 'user_id', 'relevance_score'),
        Index('idx_knowledge_source', 'source'),
        Index('idx_knowledge_access', 'access_count'),
    )
        
    def get_embedding_array(self):
        """
        Convert stored binary embedding back to numpy array.
        Handles both compressed and uncompressed formats.
        """
        try:
            # First try to decompress (for newer compressed embeddings)
            import zlib
            decompressed = zlib.decompress(self.embedding)
            return np.frombuffer(decompressed, dtype=np.float16).astype(np.float32)
        except:
            # Fall back to legacy uncompressed format
            try:
                return np.frombuffer(self.embedding, dtype=np.float32)
            except:
                # Last resort fallback
                import logging
                logging.warning(f"Failed to decode embedding for knowledge entry {self.id}")
                return np.zeros(1536, dtype=np.float32)
    
    def set_embedding_array(self, embedding_array):
        """
        Convert numpy array to compressed binary for storage.
        Uses float16 precision and zlib compression to reduce size.
        """
        try:
            # Convert to float16 and compress with zlib
            import zlib
            # Use moderate compression level (6) for good balance of speed/size
            compressed = zlib.compress(
                embedding_array.astype(np.float16).tobytes(), 
                level=6
            )
            self.embedding = compressed
        except:
            # Fall back to uncompressed if compression fails
            self.embedding = embedding_array.astype(np.float32).tobytes()
        
    def increment_access(self):
        """Update access metrics when this entry is retrieved"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'content': self.content,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count,
            'relevance_score': self.relevance_score
        }

class ReflectionPrompt(db.Model):
    """
    Stores prompts used during self-reflection to identify knowledge gaps.
    These prompts are used periodically to improve the knowledge base.
    """
    __tablename__ = 'reflection_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='general')  # general, gap-finding, consistency, etc.
    last_used = db.Column(db.DateTime, nullable=True)
    use_count = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<ReflectionPrompt {self.id}: {self.prompt[:30]}...>"
        
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'description': self.description,
            'category': self.category,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'use_count': self.use_count,
            'enabled': self.enabled
        }

# API Key Management Models
class APIKey(db.Model):
    """
    Model for storing and managing API keys with rotation support.
    Each user can have multiple API keys with different scopes and statuses.
    """
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # User-defined name for this key
    key_prefix = db.Column(db.String(8), nullable=False)  # First few chars of key (shown to user)
    key_hash = db.Column(db.String(255), nullable=False)  # Securely hashed API key
    scopes = db.Column(db.Text, nullable=False)  # JSON list of permitted scopes
    status = db.Column(db.String(20), default='active')  # active, rotated, revoked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration date
    last_used_at = db.Column(db.DateTime, nullable=True)
    use_count = db.Column(db.Integer, default=0)
    last_rotated_at = db.Column(db.DateTime, nullable=True)
    rotation_count = db.Column(db.Integer, default=0)
    
    # For audit purposes
    rotated_from_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=True)
    rotated_to_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=True)
    
    # For tracking rate limits
    hourly_usage = db.Column(db.Integer, default=0)
    daily_usage = db.Column(db.Integer, default=0)
    hourly_reset_at = db.Column(db.DateTime, default=datetime.utcnow)
    daily_reset_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationships for tracking rotation history
    rotated_from = db.relationship('APIKey', foreign_keys=[rotated_from_id],
                                 remote_side=[id], backref='rotated_to_prev')
    rotated_to = db.relationship('APIKey', foreign_keys=[rotated_to_id],
                               remote_side=[id], backref='rotated_from_next')
    
    # User relationship
    user = db.relationship('User', backref=db.backref('api_keys', lazy=True))
    
    __table_args__ = (
        UniqueConstraint('key_prefix', name='uq_api_key_prefix'),
        Index('idx_api_key_user', 'user_id'),
        Index('idx_api_key_status', 'status'),
        Index('idx_api_key_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<APIKey {self.key_prefix}... ({self.status})>"
    
    def is_active(self):
        """Check if the API key is active and not expired"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
        
    def has_scope(self, scope):
        """Check if the API key has the requested scope"""
        import json
        if not self.is_active():
            return False
        
        try:
            key_scopes = json.loads(self.scopes)
            # If key has '*' scope, it has access to everything
            if '*' in key_scopes:
                return True
            return scope in key_scopes
        except json.JSONDecodeError:
            return False
    
    def record_usage(self):
        """Record usage of this API key and update rate limit counters"""
        now = datetime.utcnow()
        self.last_used_at = now
        self.use_count += 1
        
        # Reset hourly counter if needed
        hourly_diff = now - self.hourly_reset_at
        if hourly_diff.total_seconds() > 3600:  # 1 hour
            self.hourly_usage = 0
            self.hourly_reset_at = now
        
        # Reset daily counter if needed
        daily_diff = now - self.daily_reset_at
        if daily_diff.total_seconds() > 86400:  # 24 hours
            self.daily_usage = 0
            self.daily_reset_at = now
        
        # Increment counters
        self.hourly_usage += 1
        self.daily_usage += 1
    
    def to_dict(self, include_metadata=False):
        """Convert to dictionary for API responses"""
        import json
        result = {
            'id': self.id,
            'name': self.name,
            'key_prefix': f"{self.key_prefix}...",
            'status': self.status,
            'scopes': json.loads(self.scopes) if isinstance(self.scopes, str) else self.scopes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'rotation_count': self.rotation_count
        }
        
        if include_metadata:
            result.update({
                'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
                'use_count': self.use_count,
                'last_rotated_at': self.last_rotated_at.isoformat() if self.last_rotated_at else None,
                'hourly_usage': self.hourly_usage,
                'daily_usage': self.daily_usage
            })
            
        return result
            
class APIKeyEvent(db.Model):
    """
    Model for tracking API key lifecycle events for auditing purposes.
    Records all key creations, rotations, and revocations.
    """
    __tablename__ = 'api_key_events'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # created, rotated, revoked
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = db.Column(db.String(255), nullable=True)
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    metadata = db.Column(db.Text, nullable=True)  # JSON string with additional info
    
    # Relationships
    api_key = db.relationship('APIKey', backref=db.backref('events', lazy=True))
    performed_by = db.relationship('User', backref=db.backref('api_key_events', lazy=True))
    
    __table_args__ = (
        Index('idx_api_key_event_key', 'api_key_id'),
        Index('idx_api_key_event_type', 'event_type'),
        Index('idx_api_key_event_time', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<APIKeyEvent {self.event_type} for key {self.api_key_id} at {self.timestamp}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        import json
        result = {
            'id': self.id,
            'api_key_id': self.api_key_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'performed_by_id': self.performed_by_id
        }
        
        if self.metadata:
            try:
                result['metadata'] = json.loads(self.metadata)
            except json.JSONDecodeError:
                result['metadata'] = self.metadata
                
        return result