"""
Language Learning Models
Models for tracking language learning progress, sessions, and achievements
"""

from database import db
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
import json


class Language(db.Model):
    """Available languages for learning"""
    __tablename__ = 'languages'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)  # en, es, fr, etc.
    name = Column(String(100), nullable=False)
    native_name = Column(String(100))
    flag_emoji = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    learning_sessions = relationship("LanguageLearningSession", foreign_keys="[LanguageLearningSession.target_language_id]")
    progress_records = relationship("LanguageProgress", back_populates="language")


class LanguageLearningSession(db.Model):
    """Individual language learning sessions"""
    __tablename__ = 'language_learning_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    target_language_id = Column(Integer, nullable=False)
    native_language_id = Column(Integer, nullable=False)
    session_type = Column(String(50), nullable=False)  # vocabulary, grammar, conversation, reading
    lesson_topic = Column(String(255))
    duration_minutes = Column(Integer, default=0)
    words_learned = Column(Integer, default=0)
    exercises_completed = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)
    session_data = Column(Text)  # JSON data for session details
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    target_language = relationship("Language", foreign_keys=[target_language_id])
    native_language = relationship("Language", foreign_keys=[native_language_id])
    vocabulary_progress = relationship("VocabularyProgress", back_populates="session")


class LanguageProgress(db.Model):
    """Overall language learning progress tracking"""
    __tablename__ = 'language_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    language_id = Column(Integer, nullable=False)
    proficiency_level = Column(String(20), default='beginner')  # beginner, elementary, intermediate, advanced, fluent
    total_xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    total_hours = Column(Float, default=0.0)
    words_mastered = Column(Integer, default=0)
    last_session_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    language = relationship("Language", back_populates="progress_records")


class Vocabulary(db.Model):
    """Vocabulary words and phrases"""
    __tablename__ = 'vocabulary'
    
    id = Column(Integer, primary_key=True)
    language_id = Column(Integer, nullable=False)
    word = Column(String(255), nullable=False)
    translation = Column(String(255), nullable=False)
    pronunciation = Column(String(255))
    part_of_speech = Column(String(50))  # noun, verb, adjective, etc.
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    usage_example = Column(Text)
    audio_url = Column(String(500))
    image_url = Column(String(500))
    category = Column(String(100))  # colors, food, travel, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    language = relationship("Language")
    progress_records = relationship("VocabularyProgress", back_populates="vocabulary")


class VocabularyProgress(db.Model):
    """Track user progress on individual vocabulary words"""
    __tablename__ = 'vocabulary_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    vocabulary_id = Column(Integer, nullable=False)
    session_id = Column(Integer)
    mastery_level = Column(Integer, default=0)  # 0-5 scale (0=new, 5=mastered)
    correct_attempts = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime)
    next_review_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    vocabulary = relationship("Vocabulary", back_populates="progress_records")
    session = relationship("LanguageLearningSession", back_populates="vocabulary_progress")


class LanguageGoal(db.Model):
    """User-defined language learning goals"""
    __tablename__ = 'language_goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    language_id = Column(Integer, nullable=False)
    goal_type = Column(String(50), nullable=False)  # daily_minutes, words_per_week, streak_days
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    target_date = Column(DateTime)
    is_achieved = Column(Boolean, default=False)
    achieved_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    language = relationship("Language")


class LanguageAchievement(db.Model):
    """Language learning achievements and badges"""
    __tablename__ = 'language_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    language_id = Column(Integer)
    achievement_type = Column(String(100), nullable=False)  # first_lesson, streak_7_days, 100_words, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    badge_icon = Column(String(100))
    xp_reward = Column(Integer, default=0)
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    language = relationship("Language")


# Helper functions for language learning
def get_user_languages(user_id):
    """Get all languages a user is learning"""
    return LanguageProgress.query.filter_by(user_id=user_id).all()


def get_daily_vocabulary(language_id, difficulty_level=None, category=None, limit=10):
    """Get vocabulary words for daily practice"""
    query = Vocabulary.query.filter_by(language_id=language_id)
    
    if difficulty_level:
        query = query.filter_by(difficulty_level=difficulty_level)
    
    if category:
        query = query.filter_by(category=category)
    
    return query.limit(limit).all()


def update_language_progress(user_id, language_id, session_data):
    """Update user's overall language progress after a session"""
    progress = LanguageProgress.query.filter_by(
        user_id=user_id,
        language_id=language_id
    ).first()
    
    if not progress:
        progress = LanguageProgress(
            user_id=user_id,
            language_id=language_id
        )
        db.session.add(progress)
    
    # Update progress based on session
    progress.total_xp += session_data.get('xp_earned', 0)
    progress.total_sessions += 1
    progress.total_hours += session_data.get('duration_minutes', 0) / 60.0
    progress.last_session_at = datetime.now(timezone.utc)
    
    # Update streak
    if session_data.get('completed'):
        # Check if this continues a streak
        yesterday = datetime.now(timezone.utc).date() - datetime.timedelta(days=1)
        if progress.last_session_at and progress.last_session_at.date() >= yesterday:
            progress.current_streak += 1
        else:
            progress.current_streak = 1
        
        if progress.current_streak > progress.longest_streak:
            progress.longest_streak = progress.current_streak
    
    db.session.commit()
    return progress


def create_default_languages():
    """Create default set of popular languages"""
    default_languages = [
        {'code': 'en', 'name': 'English', 'native_name': 'English', 'flag_emoji': '🇺🇸'},
        {'code': 'es', 'name': 'Spanish', 'native_name': 'Español', 'flag_emoji': '🇪🇸'},
        {'code': 'fr', 'name': 'French', 'native_name': 'Français', 'flag_emoji': '🇫🇷'},
        {'code': 'de', 'name': 'German', 'native_name': 'Deutsch', 'flag_emoji': '🇩🇪'},
        {'code': 'it', 'name': 'Italian', 'native_name': 'Italiano', 'flag_emoji': '🇮🇹'},
        {'code': 'pt', 'name': 'Portuguese', 'native_name': 'Português', 'flag_emoji': '🇵🇹'},
        {'code': 'ru', 'name': 'Russian', 'native_name': 'Русский', 'flag_emoji': '🇷🇺'},
        {'code': 'zh', 'name': 'Chinese', 'native_name': '中文', 'flag_emoji': '🇨🇳'},
        {'code': 'ja', 'name': 'Japanese', 'native_name': '日本語', 'flag_emoji': '🇯🇵'},
        {'code': 'ko', 'name': 'Korean', 'native_name': '한국어', 'flag_emoji': '🇰🇷'},
    ]
    
    for lang_data in default_languages:
        existing = Language.query.filter_by(code=lang_data['code']).first()
        if not existing:
            language = Language(**lang_data)
            db.session.add(language)
    
    db.session.commit()
    return "Default languages created successfully"