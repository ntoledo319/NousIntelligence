"""
User Models - Core User Management and Authentication
User accounts, profiles, sessions, and authentication-related models
"""

from database import db
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """Main user model for authentication and profile management"""
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    
    # Profile information
    first_name = Column(String(50))
    last_name = Column(String(50))
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(500))
    
    # Authentication
    password_hash = Column(String(256))  # For local authentication
    google_id = Column(String(100), unique=True)  # For Google OAuth
    oauth_provider = Column(String(50))  # google, facebook, etc.
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Preferences
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    theme = Column(String(20), default='light')
    notification_preferences = Column(JSON)
    
    # Tracking
    last_login = Column(DateTime)
    last_seen = Column(DateTime)
    login_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'timezone': self.timezone,
            'language': self.language,
            'theme': self.theme,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserSession(db.Model):
    """Track user sessions for security and analytics"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    
    # Session details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    device_type = Column(String(50))  # mobile, tablet, desktop
    browser = Column(String(100))
    os = Column(String(100))
    
    # Location (optional)
    country = Column(String(100))
    city = Column(String(100))
    
    # Session tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


class UserPreferences(db.Model):
    """Detailed user preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Communication preferences
    communication_style = Column(String(20), default='casual')  # casual, professional, concise, detailed
    ai_assistance_level = Column(String(20), default='proactive')  # proactive, responsive, minimal
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(20), default='medium')  # high, medium, low, none
    
    # Privacy preferences
    data_sharing_level = Column(String(20), default='full')  # full, limited, minimal
    analytics_opt_in = Column(Boolean, default=True)
    personalization_enabled = Column(Boolean, default=True)
    
    # Interface preferences
    dashboard_layout = Column(String(20), default='standard')  # compact, standard, expanded
    default_view = Column(String(50), default='dashboard')
    keyboard_shortcuts = Column(Boolean, default=True)
    
    # Productivity preferences
    work_hours_start = Column(String(5), default='09:00')
    work_hours_end = Column(String(5), default='17:00')
    break_reminders = Column(Boolean, default=True)
    focus_mode_duration = Column(Integer, default=25)  # minutes
    
    # Updated tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserActivity(db.Model):
    """Track user activity for analytics and personalization"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # page_view, api_call, chat_message, etc.
    activity_data = Column(JSON)  # Additional activity-specific data
    
    # Context
    page_url = Column(String(500))
    referrer = Column(String(500))
    device_type = Column(String(50))
    
    # Timing
    duration = Column(Integer)  # Duration in seconds
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserGoal(db.Model):
    """User-defined goals and objectives"""
    __tablename__ = 'user_goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Goal details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # productivity, health, learning, financial, etc.
    
    # Goal metrics
    target_value = Column(Float)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50))  # hours, days, dollars, etc.
    
    # Timeline
    target_date = Column(DateTime)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completion_date = Column(DateTime)
    
    # Status
    status = Column(String(20), default='active')  # active, completed, paused, cancelled
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    
    # Progress tracking
    milestones = Column(JSON)  # Array of milestone objects
    progress_notes = Column(Text)
    
    # Created/updated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserNotification(db.Model):
    """User notifications and alerts"""
    __tablename__ = 'user_notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text)
    notification_type = Column(String(50))  # info, warning, error, success
    category = Column(String(100))  # system, goal, reminder, social, etc.
    
    # Action details
    action_url = Column(String(500))
    action_text = Column(String(100))
    
    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Delivery
    delivery_methods = Column(JSON)  # ['in_app', 'email', 'push', 'sms']
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Timing
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)


class UserApiKey(db.Model):
    """API keys for external service integrations"""
    __tablename__ = 'user_api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Service details
    service_name = Column(String(100), nullable=False)  # google, spotify, openai, etc.
    api_key = Column(String(500))  # Encrypted
    refresh_token = Column(String(500))  # Encrypted
    
    # Permissions and scope
    scopes = Column(JSON)  # Array of permission scopes
    permissions = Column(JSON)  # Detailed permissions
    
    # Status
    is_active = Column(Boolean, default=True)
    is_expired = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    
    # Usage tracking
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # Created/updated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# Helper functions for user management
def create_user(username: str, email: str, **kwargs) -> User:
    """Create a new user account"""
    try:
        user = User(
            username=username,
            email=email,
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
            display_name=kwargs.get('display_name', username),
            google_id=kwargs.get('google_id'),
            oauth_provider=kwargs.get('oauth_provider'),
            timezone=kwargs.get('timezone', 'UTC'),
            language=kwargs.get('language', 'en')
        )
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create default preferences
        preferences = UserPreferences(user_id=user.id)
        db.session.add(preferences)
        
        db.session.commit()
        return user
    
    except Exception as e:
        db.session.rollback()
        raise e


def get_user_by_email(email: str) -> User:
    """Get user by email address"""
    return User.query.filter_by(email=email).first()


def get_user_by_google_id(google_id: str) -> User:
    """Get user by Google ID"""
    return User.query.filter_by(google_id=google_id).first()


def update_user_login(user_id: int):
    """Update user login tracking"""
    try:
        user = User.query.get(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            user.last_seen = datetime.now(timezone.utc)
            user.login_count += 1
            db.session.commit()
    except Exception as e:
        db.session.rollback()


def create_user_session(user_id: int, session_token: str, **kwargs) -> UserSession:
    """Create a new user session"""
    try:
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            device_type=kwargs.get('device_type'),
            browser=kwargs.get('browser'),
            os=kwargs.get('os'),
            country=kwargs.get('country'),
            city=kwargs.get('city'),
            expires_at=kwargs.get('expires_at')
        )
        
        db.session.add(session)
        db.session.commit()
        return session
    
    except Exception as e:
        db.session.rollback()
        raise e


def log_user_activity(user_id: int, activity_type: str, **kwargs):
    """Log user activity"""
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=kwargs.get('activity_data'),
            page_url=kwargs.get('page_url'),
            referrer=kwargs.get('referrer'),
            device_type=kwargs.get('device_type'),
            duration=kwargs.get('duration')
        )
        
        db.session.add(activity)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()


def create_user_notification(user_id: int, title: str, message: str, **kwargs) -> UserNotification:
    """Create a new notification for user"""
    try:
        notification = UserNotification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=kwargs.get('notification_type', 'info'),
            category=kwargs.get('category', 'system'),
            action_url=kwargs.get('action_url'),
            action_text=kwargs.get('action_text'),
            delivery_methods=kwargs.get('delivery_methods', ['in_app']),
            expires_at=kwargs.get('expires_at')
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    except Exception as e:
        db.session.rollback()
        raise e


def get_user_statistics(user_id: int) -> dict:
    """Get user statistics and metrics"""
    try:
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Activity counts
        total_activities = UserActivity.query.filter_by(user_id=user_id).count()
        
        # Goal statistics
        total_goals = UserGoal.query.filter_by(user_id=user_id).count()
        completed_goals = UserGoal.query.filter_by(user_id=user_id, status='completed').count()
        
        # Notification statistics
        total_notifications = UserNotification.query.filter_by(user_id=user_id).count()
        unread_notifications = UserNotification.query.filter_by(user_id=user_id, is_read=False).count()
        
        # Session statistics
        total_sessions = UserSession.query.filter_by(user_id=user_id).count()
        active_sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).count()
        
        return {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'member_since': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count
            },
            'activity': {
                'total_activities': total_activities,
                'total_sessions': total_sessions,
                'active_sessions': active_sessions
            },
            'goals': {
                'total_goals': total_goals,
                'completed_goals': completed_goals,
                'completion_rate': (completed_goals / total_goals * 100) if total_goals > 0 else 0
            },
            'notifications': {
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications
            }
        }
    
    except Exception as e:
        return {'error': str(e)}