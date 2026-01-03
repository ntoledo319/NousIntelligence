"""
Task and Reminder Models
Database models for task management and reminders
"""
from datetime import datetime
from models.database import db
from sqlalchemy.dialects.postgresql import JSON


class Task(db.Model):
    """User tasks with Google Tasks sync support"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, index=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    category = db.Column(db.String(50), default='general', index=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime)
    recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(JSON)  # Store recurrence rules
    google_task_id = db.Column(db.String(100))  # For Google Tasks sync
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('tasks', lazy=True, cascade='all, delete-orphan'))
    reminders = db.relationship('Reminder', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'category': self.category,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'recurring': self.recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'google_task_id': self.google_task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Reminder(db.Model):
    """Reminders for tasks or standalone"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True, index=True)
    reminder_time = db.Column(db.DateTime, nullable=False, index=True)
    message = db.Column(db.Text)
    reminder_type = db.Column(db.String(50), default='notification')  # notification, email, sms
    sent = db.Column(db.Boolean, default=False, index=True)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('reminders', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'message': self.message,
            'reminder_type': self.reminder_type,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
