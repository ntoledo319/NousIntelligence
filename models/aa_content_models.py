"""
Alcoholics Anonymous Content Models

This module contains database models for storing AA content like the Big Book text,
audio versions, and speaker recordings. This content is kept in the database
for reliable access and to reduce API costs.
"""

from datetime import datetime
from app_factory import db
from sqlalchemy import Text

class AABigBook(db.Model):
    """AA Big Book content by chapter"""
    __tablename__ = 'aa_big_book'

    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_title = db.Column(db.String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    is_foreword = db.Column(db.Boolean, default=False)
    is_appendix = db.Column(db.Boolean, default=False)
    edition = db.Column(db.String(50), default="4th")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AABigBook {self.chapter_title}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chapter_number': self.chapter_number,
            'chapter_title': self.chapter_title,
            'content': self.content,
            'is_foreword': self.is_foreword,
            'is_appendix': self.is_appendix,
            'edition': self.edition,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AABigBookAudio(db.Model):
    """Audio files for the AA Big Book"""
    __tablename__ = 'aa_big_book_audio'

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('aa_big_book.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    narrator = db.Column(db.String(100), nullable=True)
    audio_quality = db.Column(db.String(50), nullable=True)
    format = db.Column(db.String(10), default="mp3")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    chapter = db.relationship('AABigBook', backref=db.backref('audio_files', lazy=True))

    def __repr__(self):
        return f"<AABigBookAudio for {self.chapter.chapter_title if self.chapter else 'Unknown'}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'file_path': self.file_path,
            'duration_seconds': self.duration_seconds,
            'narrator': self.narrator,
            'audio_quality': self.audio_quality,
            'format': self.format,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AASpeakerRecording(db.Model):
    """AA speaker recordings"""
    __tablename__ = 'aa_speaker_recordings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    speaker_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    year_recorded = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    format = db.Column(db.String(10), default="mp3")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AASpeakerRecording {self.title} by {self.speaker_name}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'speaker_name': self.speaker_name,
            'file_path': self.file_path,
            'description': self.description,
            'year_recorded': self.year_recorded,
            'location': self.location,
            'duration_seconds': self.duration_seconds,
            'tags': self.tags,
            'format': self.format,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AADailyReflection(db.Model):
    """AA daily reflections content"""
    __tablename__ = 'aa_daily_reflections'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    reference = db.Column(db.String(255), nullable=True)  # Reference to Big Book or other source
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AADailyReflection {self.month}/{self.day}: {self.title}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'month': self.month,
            'day': self.day,
            'title': self.title,
            'content': self.content,
            'reference': self.reference,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AAFavorite(db.Model):
    """User favorites for AA content"""
    __tablename__ = 'aa_favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'big_book', 'speaker', 'daily'
    content_id = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('aa_favorites', lazy=True))

    def __repr__(self):
        return f"<AAFavorite by {self.user_id}: {self.content_type} #{self.content_id}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }