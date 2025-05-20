"""
Task Models

This module contains task-related database models for the NOUS application.
"""

from datetime import datetime
from app_factory import db

class Task(db.Model):
    """Task model for user task management"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=0)  # 0=normal, 1=important, 2=urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Tags stored as comma-separated string
    tags = db.Column(db.String(255))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags.split(',') if self.tags else []
        }
    
    def complete(self):
        """Mark the task as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
    def cancel(self):
        """Mark the task as canceled"""
        self.status = 'canceled'
        
    def reset(self):
        """Reset the task to pending status"""
        self.status = 'pending'
        self.completed_at = None