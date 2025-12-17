"""
Social and Community Models

This module defines database models for social features including support groups,
peer connections, anonymous sharing, and community interactions.

@module models.social_models
@context_boundary Social Features
"""

from models.database import db
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class SupportGroup(db.Model):
    """Model for support groups where users can connect"""
    
    __tablename__ = 'support_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'anxiety', 'depression', 'addiction'
    privacy_level = db.Column(db.String(20), default='private')  # private, public, invite-only
    max_members = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), db.ForeignKey('users.id'))
    
    # VOCAB: Support Group - A safe space for peer support
    # Relationships
    members = db.relationship('GroupMembership', back_populates='group', lazy='dynamic')
    posts = db.relationship('GroupPost', back_populates='group', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'privacy_level': self.privacy_level,
            'member_count': self.members.count(),
            'max_members': self.max_members,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GroupMembership(db.Model):
    """Model for user membership in support groups"""
    
    __tablename__ = 'group_memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('support_groups.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # member, moderator, admin
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    notification_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    group = db.relationship('SupportGroup', back_populates='members')
    user = db.relationship('User', backref='group_memberships')


class PeerConnection(db.Model):
    """Model for peer-to-peer connections (like friends)"""
    
    __tablename__ = 'peer_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    peer_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    connection_type = db.Column(db.String(20), default='peer')  # peer, mentor, mentee
    status = db.Column(db.String(20), default='pending')  # pending, accepted, blocked
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    
    # VOCAB: Peer Connection - A supportive relationship between users
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='connections_initiated')
    peer = db.relationship('User', foreign_keys=[peer_id], backref='connections_received')


class AnonymousShare(db.Model):
    """Model for anonymous sharing of experiences"""
    
    __tablename__ = 'anonymous_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    share_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    mood_at_sharing = db.Column(db.String(20))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Anonymous but trackable for moderation
    user_hash = db.Column(db.String(64))  # Hashed user ID for tracking abuse
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    support_count = db.Column(db.Integer, default=0)  # Like "helpful" reactions
    
    # Relationships
    responses = db.relationship('AnonymousResponse', back_populates='share', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'share_id': self.share_id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'mood_at_sharing': self.mood_at_sharing,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'view_count': self.view_count,
            'support_count': self.support_count,
            'response_count': self.responses.count()
        }


class AnonymousResponse(db.Model):
    """Model for responses to anonymous shares"""
    
    __tablename__ = 'anonymous_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    share_id = db.Column(db.Integer, db.ForeignKey('anonymous_shares.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_supportive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Anonymous but trackable
    responder_hash = db.Column(db.String(64))
    
    # Relationships
    share = db.relationship('AnonymousShare', back_populates='responses')


class GroupPost(db.Model):
    """Model for posts within support groups"""
    
    __tablename__ = 'group_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('support_groups.id'), nullable=False)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), default='discussion')  # discussion, question, achievement
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    group = db.relationship('SupportGroup', back_populates='posts')
    author = db.relationship('User', backref='group_posts')
    comments = db.relationship('GroupComment', back_populates='post', lazy='dynamic')


class GroupComment(db.Model):
    """Model for comments on group posts"""
    
    __tablename__ = 'group_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('group_posts.id'), nullable=False)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('GroupPost', back_populates='comments')
    author = db.relationship('User', backref='group_comments')


# AI-GENERATED [2024-12-01]
# ACCEPTABLE_VARIANTS: Could also implement using graph database for connections 