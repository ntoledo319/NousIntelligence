"""
Collaboration Models

This module contains collaboration and family/team models for the NOUS application,
supporting shared features, family dashboards, and collaborative workspaces.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
import json

class Family(db.Model):
    """Family groups for shared functionality"""
    __tablename__ = 'families'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    invite_code = db.Column(db.String(20), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    max_members = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_families', lazy=True))
    members = db.relationship('FamilyMember', backref='family', cascade='all, delete-orphan')
    shared_tasks = db.relationship('SharedTask', backref='family', cascade='all, delete-orphan')
    shared_events = db.relationship('SharedEvent', backref='family', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'invite_code': self.invite_code,
            'is_active': self.is_active,
            'max_members': self.max_members,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FamilyMember(db.Model):
    """Family membership and roles"""
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, member, child
    nickname = db.Column(db.String(50))  # Display name within family
    permissions = db.Column(db.JSON)  # Array of permission strings
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    invited_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('family_memberships', lazy=True))
    inviter = db.relationship('User', foreign_keys=[invited_by])

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'user_id': self.user_id,
            'role': self.role,
            'nickname': self.nickname,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'invited_by': self.invited_by,
            'user': self.user.to_dict() if self.user else None
        }

class SharedTask(db.Model):
    """Tasks shared among family members"""
    __tablename__ = 'shared_tasks'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))  # household, shopping, etc.
    priority = db.Column(db.String(20), default='medium')
    due_date = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.JSON)  # For recurring tasks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    creator = db.relationship('User', foreign_keys=[created_by])
    completer = db.relationship('User', foreign_keys=[completed_by])

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'category': self.category,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completed_by': self.completed_by,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SharedEvent(db.Model):
    """Shared calendar events for families"""
    __tablename__ = 'shared_events'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_all_day = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    attendees = db.Column(db.JSON)  # Array of user IDs
    reminder_minutes = db.Column(db.Integer, default=15)
    event_type = db.Column(db.String(50))  # appointment, meal, activity, etc.
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_shared_events', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_all_day': self.is_all_day,
            'created_by': self.created_by,
            'attendees': self.attendees,
            'reminder_minutes': self.reminder_minutes,
            'event_type': self.event_type,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SharedShoppingList(db.Model):
    """Collaborative shopping lists"""
    __tablename__ = 'shared_shopping_lists'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    store_location = db.Column(db.String(255))
    budget_limit = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_shopping_lists', lazy=True))
    items = db.relationship('SharedShoppingItem', backref='shopping_list', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'store_location': self.store_location,
            'budget_limit': float(self.budget_limit) if self.budget_limit else None,
            'item_count': len(self.items),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SharedShoppingItem(db.Model):
    """Items in shared shopping lists"""
    __tablename__ = 'shared_shopping_items'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('shared_shopping_lists.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(20))  # lbs, oz, etc.
    category = db.Column(db.String(50))
    estimated_price = db.Column(db.Numeric(8, 2))
    actual_price = db.Column(db.Numeric(8, 2))
    notes = db.Column(db.Text)
    is_purchased = db.Column(db.Boolean, default=False)
    purchased_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    purchased_at = db.Column(db.DateTime)
    added_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    purchaser = db.relationship('User', foreign_keys=[purchased_by])
    adder = db.relationship('User', foreign_keys=[added_by])

    def to_dict(self):
        return {
            'id': self.id,
            'list_id': self.list_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'category': self.category,
            'estimated_price': float(self.estimated_price) if self.estimated_price else None,
            'actual_price': float(self.actual_price) if self.actual_price else None,
            'notes': self.notes,
            'is_purchased': self.is_purchased,
            'purchased_by': self.purchased_by,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
            'added_by': self.added_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SupportGroup(db.Model):
    """Support groups for recovery and mental health"""
    __tablename__ = 'support_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    group_type = db.Column(db.String(50))  # aa, dbt, general, etc.
    is_private = db.Column(db.Boolean, default=True)
    max_members = db.Column(db.Integer, default=20)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    invite_code = db.Column(db.String(20), unique=True)
    meeting_schedule = db.Column(db.JSON)  # Meeting times and frequency
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_support_groups', lazy=True))
    members = db.relationship('SupportGroupMember', backref='group', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'group_type': self.group_type,
            'is_private': self.is_private,
            'max_members': self.max_members,
            'created_by': self.created_by,
            'invite_code': self.invite_code,
            'meeting_schedule': self.meeting_schedule,
            'is_active': self.is_active,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SupportGroupMember(db.Model):
    """Support group membership"""
    __tablename__ = 'support_group_members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('support_groups.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # facilitator, member
    anonymous_name = db.Column(db.String(50))  # For anonymity
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('support_group_memberships', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'role': self.role,
            'anonymous_name': self.anonymous_name,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
