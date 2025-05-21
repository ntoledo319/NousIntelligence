"""
Memory Models

This module defines database models related to the memory system,
including user conversation history, topics of interest, and entity memories.

@module models.memory_models
@description Memory-related database models
"""

import json
import datetime
from typing import Dict, Any, Optional
from app_factory import db

class UserMemoryEntry(db.Model):
    """
    Model for storing user chat and voice interactions.
    
    Attributes:
        id: Unique identifier for the memory entry
        user_id: Foreign key to the user this memory belongs to
        role: Role in the conversation (user, assistant, system)
        content: Content of the message
        source_type: Source of the message (text, voice, etc.)
        emotion: Detected emotion in the message (if applicable)
        timestamp: When the message was created
        interaction_id: Identifier for linking related messages in a conversation
        metadata: Additional metadata about the message (JSON)
    """
    __tablename__ = 'user_memory_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    source_type = db.Column(db.String(20), default='text')  # text, voice, etc.
    emotion = db.Column(db.String(20))  # happy, sad, neutral, etc.
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    interaction_id = db.Column(db.String(36))  # To group related messages
    metadata = db.Column(db.Text)  # JSON string for additional data
    
    # Relationships
    user = db.relationship('User', backref=db.backref('memory_entries', lazy=True))
    
    def __repr__(self):
        return f'<UserMemoryEntry {self.id} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert memory entry to dictionary"""
        import json
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'source_type': self.source_type,
            'emotion': self.emotion,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'interaction_id': self.interaction_id,
            'metadata': json.loads(self.metadata) if self.metadata and isinstance(self.metadata, str) else {}
        }


class UserTopicInterest(db.Model):
    """
    Model for tracking user interests in various topics.
    
    Attributes:
        id: Unique identifier for the topic interest
        user_id: Foreign key to the user
        topic_name: Name of the topic
        interest_level: Level of interest (1-10)
        last_discussed: When the topic was last discussed
        engagement_count: How many times user has engaged with this topic
        metadata: Additional metadata about the interest (JSON)
    """
    __tablename__ = 'user_topic_interests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    interest_level = db.Column(db.Integer, default=1)  # 1-10 scale
    last_discussed = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    engagement_count = db.Column(db.Integer, default=1)
    metadata = db.Column(db.Text)  # JSON string for additional data
    
    # Relationships
    user = db.relationship('User', backref=db.backref('topic_interests', lazy=True))
    
    # Composite index for efficient querying
    __table_args__ = (
        db.Index('idx_user_topic', user_id, topic_name),
    )
    
    def __repr__(self):
        return f'<UserTopicInterest {self.topic_name} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert topic interest to dictionary"""
        import json
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'interest_level': self.interest_level,
            'last_discussed': self.last_discussed.isoformat() if self.last_discussed else None,
            'engagement_count': self.engagement_count,
            'metadata': json.loads(self.metadata) if self.metadata and isinstance(self.metadata, str) else {}
        }


class UserEntityMemory(db.Model):
    """
    Model for storing entities (people, places, things) the user has mentioned.
    
    Attributes:
        id: Unique identifier for the entity memory
        user_id: Foreign key to the user
        entity_name: Name of the entity
        entity_type: Type of entity (person, place, thing, etc.)
        attributes: Attributes of the entity (JSON)
        last_mentioned: When the entity was last mentioned
        mention_count: How many times the entity has been mentioned
        importance: Importance score for the entity (1-10)
    """
    __tablename__ = 'user_entity_memories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    entity_name = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # person, place, thing, etc.
    attributes = db.Column(db.Text, nullable=False)  # JSON string
    last_mentioned = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    mention_count = db.Column(db.Integer, default=1)
    importance = db.Column(db.Integer, default=5)  # 1-10 scale
    
    # Relationships
    user = db.relationship('User', backref=db.backref('entity_memories', lazy=True))
    
    # Composite index for efficient querying
    __table_args__ = (
        db.Index('idx_user_entity', user_id, entity_name),
    )
    
    def __repr__(self):
        return f'<UserEntityMemory {self.entity_name} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert entity memory to dictionary"""
        import json
        return {
            'id': self.id,
            'entity_name': self.entity_name,
            'entity_type': self.entity_type,
            'attributes': json.loads(self.attributes) if self.attributes and isinstance(self.attributes, str) else {},
            'last_mentioned': self.last_mentioned.isoformat() if self.last_mentioned else None,
            'mention_count': self.mention_count,
            'importance': self.importance
        }