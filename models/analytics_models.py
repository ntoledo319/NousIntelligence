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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    metric_date = db.Column(db.Date, nullable=False)
    
    # Productivity metrics
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_created = db.Column(db.Integer, default=0)
    chat_sessions = db.Column(db.Integer, default=0)
    total_chat_time = db.Column(db.Integer, default=0)  # in seconds
    
    # Health metrics
    mood_entries = db.Column(db.Integer, default=0)
    mood_average = db.Column(db.Float)
    workout_sessions = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    app_sessions = db.Column(db.Integer, default=0)
    total_app_time = db.Column(db.Integer, default=0)  # in seconds
    features_used = db.Column(db.JSON)  # List of feature names used
    
    # Custom metrics (JSON for flexibility)
    custom_metrics = db.Column(db.JSON)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('metrics', lazy=True))

class UserInsights(db.Model):
    """AI-generated insights about user behavior and patterns"""
    __tablename__ = 'user_insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)  # pattern, trend, recommendation
    insight_category = db.Column(db.String(50))  # productivity, health, behavior
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    insight_data = db.Column(db.JSON)  # Supporting data and metrics
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # When insight becomes stale
    user_feedback = db.Column(db.String(20))  # helpful, not_helpful, neutral
    
    # Relationships
    user = db.relationship('User', backref=db.backref('insights', lazy=True))

class UserGoals(db.Model):
    """User goals and progress tracking"""
    __tablename__ = 'user_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # productivity, health, learning
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50))  # tasks, minutes, pounds, etc.
    target_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed, paused, cancelled
    
    # Progress tracking
    progress_data = db.Column(db.JSON)  # Historical progress points
    
    # Relationships
    user = db.relationship('User', backref=db.backref('goals', lazy=True))

class EngagementMetrics(db.Model):
    """Track user engagement patterns"""
    __tablename__ = 'engagement_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Session metrics
    sessions_count = db.Column(db.Integer, default=0)
    total_session_time = db.Column(db.Integer, default=0)  # in seconds
    avg_session_time = db.Column(db.Float)
    
    # Interaction metrics
    clicks_count = db.Column(db.Integer, default=0)
    features_explored = db.Column(db.JSON)  # List of features used
    new_features_tried = db.Column(db.JSON)  # First-time feature usage
    
    # Content engagement
    content_created = db.Column(db.Integer, default=0)  # notes, tasks, etc.
    content_consumed = db.Column(db.Integer, default=0)  # articles read, videos watched
    
    # Help and support
    help_requests = db.Column(db.Integer, default=0)
    feedback_given = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('engagement_metrics', lazy=True))

class RetentionMetrics(db.Model):
    """Track user retention and churn patterns"""
    __tablename__ = 'retention_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # Week since signup
    month_number = db.Column(db.Integer, nullable=False)  # Month since signup
    
    # Retention flags
    was_active_this_week = db.Column(db.Boolean, default=False)
    was_active_this_month = db.Column(db.Boolean, default=False)
    
    # Activity summary
    sessions_this_period = db.Column(db.Integer, default=0)
    features_used_this_period = db.Column(db.JSON)
    last_activity_date = db.Column(db.Date)
    
    # Calculated at period end
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('retention_metrics', lazy=True))

class PerformanceMetrics(db.Model):
    """Track system performance metrics per user"""
    __tablename__ = 'performance_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Response time metrics
    avg_response_time = db.Column(db.Float)  # in milliseconds
    max_response_time = db.Column(db.Float)
    min_response_time = db.Column(db.Float)
    
    # Error metrics
    error_count = db.Column(db.Integer, default=0)
    error_types = db.Column(db.JSON)  # List of error types encountered
    
    # Resource usage
    memory_usage = db.Column(db.Float)  # in MB
    cpu_usage = db.Column(db.Float)  # percentage
    
    # Feature-specific metrics
    feature_performance = db.Column(db.JSON)  # Per-feature performance data
    
    # Relationships
    user = db.relationship('User', backref=db.backref('performance_metrics', lazy=True))

# Legacy aliases for backward compatibility
Activity = UserActivity
Insight = UserInsights
Goal = UserGoals
HealthMetric = UserMetrics
AnalyticsData = UserMetrics