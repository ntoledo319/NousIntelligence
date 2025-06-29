"""
Analytics Models

This module contains analytics and insights models for the NOUS application,
supporting comprehensive user analytics, activity tracking, and AI-powered insights.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, text
from sqlalchemy.ext.hybrid import hybrid_property
import json

# Import the shared database instance
from database import db

class UserActivity(db.Model):
    """Track user activities and interactions"""
    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # chat, task, mood, workout, etc.
    activity_category = db.Column(db.String(50))  # productivity, health, entertainment, etc.
    activity_data = db.Column(db.JSON)  # Flexible data storage
    duration_seconds = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(64))  # Group activities by session
    
    # Relationships
    user = db.relationship('User', backref=db.backref('activities', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_category': self.activity_category,
            'activity_data': self.activity_data,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }

class UserMetrics(db.Model):
    """Aggregate user metrics for analytics"""
    __tablename__ = 'user_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    metric_date = db.Column(db.Date, nullable=False)
    
    # Productivity metrics
    tasks_completed = db.Column(db.Integer, default=0)
    chat_messages_sent = db.Column(db.Integer, default=0)
    features_used = db.Column(db.JSON)  # Array of feature names used
    active_time_minutes = db.Column(db.Integer, default=0)
    
    # Health metrics
    mood_average = db.Column(db.Float)
    workouts_logged = db.Column(db.Integer, default=0)
    dbt_skills_used = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    login_count = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('metrics', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'metric_type': self.metric_type,
            'metric_date': self.metric_date.isoformat() if self.metric_date else None,
            'tasks_completed': self.tasks_completed,
            'chat_messages_sent': self.chat_messages_sent,
            'features_used': self.features_used,
            'active_time_minutes': self.active_time_minutes,
            'mood_average': self.mood_average,
            'workouts_logged': self.workouts_logged,
            'dbt_skills_used': self.dbt_skills_used,
            'login_count': self.login_count,
            'streak_days': self.streak_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserInsight(db.Model):
    """AI-generated insights about user behavior and recommendations"""
    __tablename__ = 'user_insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)  # trend, recommendation, achievement, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)  # AI confidence in insight
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    is_read = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # For time-sensitive insights
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_insights', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'insight_type': self.insight_type,
            'title': self.title,
            'content': self.content,
            'confidence_score': self.confidence_score,
            'priority': self.priority,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class UserGoal(db.Model):
    """User goals and targets"""
    __tablename__ = 'user_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # productivity, health, learning, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20))  # tasks, minutes, workouts, etc.
    target_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_goals', lazy=True))

    @hybrid_property
    def progress_percentage(self):
        if not self.target_value or self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'title': self.title,
            'description': self.description,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_completed': self.is_completed,
            'is_active': self.is_active,
            'progress_percentage': self.progress_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class NotificationQueue(db.Model):
    """User notifications and alerts"""
    __tablename__ = 'notification_queue'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # system, reminder, achievement, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_read = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500))  # Optional action link
    extra_data = db.Column(db.JSON)  # Additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'action_url': self.action_url,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class WorkflowAutomation(db.Model):
    """User-defined workflow automations"""
    __tablename__ = 'workflow_automations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    trigger_config = db.Column(db.JSON, nullable=False)  # Trigger conditions
    action_config = db.Column(db.JSON, nullable=False)  # Actions to perform
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('automations', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'trigger_config': self.trigger_config,
            'action_config': self.action_config,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SearchIndex(db.Model):
    """Global search index for all user content"""
    __tablename__ = 'search_index'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # task, note, chat, etc.
    content_id = db.Column(db.String(50), nullable=False)  # ID of the source content
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    tags = db.Column(db.JSON)  # Array of tags for categorization
    search_vector = db.Column(db.Text)  # Pre-processed for search
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('search_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 
class Goal(db.Model):
    """User goals and objectives tracking"""
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # health, career, personal, etc.
    target_value = db.Column(db.Float)  # Numeric target if applicable
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))  # days, pounds, hours, etc.
    status = db.Column(db.String(20), default='active')  # active, completed, paused, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    start_date = db.Column(db.Date)
    target_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('analytics_goals', lazy=True))

    @hybrid_property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if self.target_value and self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'status': self.status,
            'priority': self.priority,
            'progress_percentage': self.progress_percentage,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Insight(db.Model):
    """AI-generated insights and recommendations"""
    __tablename__ = 'insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    insight_type = db.Column(db.String(50))  # pattern, recommendation, alert, etc.
    category = db.Column(db.String(50))  # health, productivity, relationships, etc.
    priority = db.Column(db.Integer, default=5)  # 1-10 scale
    confidence_score = db.Column(db.Float, default=0.5)  # 0.0-1.0
    data_sources = db.Column(db.JSON)  # What data was used to generate this insight
    action_items = db.Column(db.JSON)  # Suggested actions
    is_read = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Some insights may have expiration
    
    # Relationships
    user = db.relationship('User', backref=db.backref('analytics_insights', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'insight_type': self.insight_type,
            'category': self.category,
            'priority': self.priority,
            'confidence_score': self.confidence_score,
            'data_sources': self.data_sources,
            'action_items': self.action_items,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
