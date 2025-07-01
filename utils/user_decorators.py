"""
Comprehensive User Authentication Decorators and Middleware
Advanced user session management, authentication, and authorization decorators
"""

from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
import logging
from flask import session, request, jsonify, redirect, url_for, current_app, g
from models.user import User
from models.setup_models import UserPreferences
from database import db

logger = logging.getLogger(__name__)

class UserAuthDecorators:
    """Comprehensive user authentication and authorization decorators"""
    
    @staticmethod
    def login_required(f: Callable) -> Callable:
        """Require user to be logged in"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not UserAuthDecorators._is_user_authenticated():
                if request.is_json:
                    return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
                return redirect(url_for('auth.login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def demo_or_auth_required(f: Callable) -> Callable:
        """Require user to be logged in or allow demo mode"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not UserAuthDecorators._is_user_authenticated() and not UserAuthDecorators._is_demo_mode():
                # Enable demo mode for public access
                UserAuthDecorators._enable_demo_mode()
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def admin_required(f: Callable) -> Callable:
        """Require user to be an admin"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not UserAuthDecorators._is_user_authenticated():
                if request.is_json:
                    return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
                return redirect(url_for('auth.login'))
            
            user = UserAuthDecorators._get_current_user()
            if not user or not getattr(user, 'is_admin', False):
                if request.is_json:
                    return jsonify({'error': 'Admin access required', 'code': 'ADMIN_REQUIRED'}), 403
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def permission_required(permission: str):
        """Require specific permission"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not UserAuthDecorators._is_user_authenticated():
                    if request.is_json:
                        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
                    return redirect(url_for('auth.login'))
                
                user = UserAuthDecorators._get_current_user()
                if not user or not UserAuthDecorators._check_user_permission(user, permission):
                    if request.is_json:
                        return jsonify({'error': f'Permission {permission} required', 'code': 'PERMISSION_REQUIRED'}), 403
                    return redirect(url_for('main.index'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def rate_limit(max_requests: int = 100, per_minutes: int = 60):
        """Rate limiting decorator"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = UserAuthDecorators._get_user_id()
                if user_id and not UserAuthDecorators._check_rate_limit(user_id, f.__name__, max_requests, per_minutes):
                    if request.is_json:
                        return jsonify({'error': 'Rate limit exceeded', 'code': 'RATE_LIMIT_EXCEEDED'}), 429
                    return "Rate limit exceeded", 429
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def track_activity(activity_type: str):
        """Track user activity decorator"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = UserAuthDecorators._get_user_id()
                if user_id:
                    UserAuthDecorators._track_user_activity(user_id, activity_type, {
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_session(f: Callable) -> Callable:
        """Validate and refresh user session"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if UserAuthDecorators._is_user_authenticated():
                if not UserAuthDecorators._validate_session():
                    UserAuthDecorators._clear_session()
                    if request.is_json:
                        return jsonify({'error': 'Session expired', 'code': 'SESSION_EXPIRED'}), 401
                    return redirect(url_for('auth.login'))
                else:
                    UserAuthDecorators._refresh_session()
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def setup_required(f: Callable) -> Callable:
        """Require user to complete setup wizard"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if UserAuthDecorators._is_demo_mode():
                return f(*args, **kwargs)  # Skip setup for demo
            
            if not UserAuthDecorators._is_user_authenticated():
                if request.is_json:
                    return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
                return redirect(url_for('auth.login'))
            
            user_id = UserAuthDecorators._get_user_id()
            if user_id and not UserAuthDecorators._is_setup_complete(user_id):
                if request.is_json:
                    return jsonify({'error': 'Setup required', 'code': 'SETUP_REQUIRED', 'redirect': '/setup'}), 302
                return redirect(url_for('setup.wizard'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def preferences_context(f: Callable) -> Callable:
        """Add user preferences to request context"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = UserAuthDecorators._get_user_id()
            if user_id:
                preferences = UserAuthDecorators._get_user_preferences(user_id)
                g.user_preferences = preferences
            else:
                g.user_preferences = UserAuthDecorators._get_default_preferences()
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def crisis_check(f: Callable) -> Callable:
        """Check for crisis keywords and provide resources"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check request data for crisis keywords
            crisis_keywords = [
                'suicide', 'kill myself', 'end my life', 'self harm', 'hurt myself',
                'overdose', 'pills', 'can\'t go on', 'want to die', 'no point'
            ]
            
            request_text = ""
            if request.is_json and request.json:
                request_text = str(request.json).lower()
            elif request.form:
                request_text = str(dict(request.form)).lower()
            
            if any(keyword in request_text for keyword in crisis_keywords):
                UserAuthDecorators._log_crisis_trigger()
                # Add crisis resources to response context
                g.crisis_detected = True
                g.crisis_resources = UserAuthDecorators._get_crisis_resources()
            
            return f(*args, **kwargs)
        return decorated_function
    
    # Helper methods
    
    @staticmethod
    def _is_user_authenticated() -> bool:
        """Check if user is authenticated"""
        return 'user_id' in session and session['user_id'] is not None
    
    @staticmethod
    def _is_demo_mode() -> bool:
        """Check if in demo mode"""
        return session.get('is_demo', False)
    
    @staticmethod
    def _enable_demo_mode() -> None:
        """Enable demo mode"""
        session['is_demo'] = True
        session['user_id'] = 'demo'
        session['username'] = 'Demo User'
        session['email'] = 'demo@nous.app'
        session['created_at'] = datetime.utcnow().isoformat()
    
    @staticmethod
    def _get_current_user() -> Optional[User]:
        """Get current authenticated user"""
        if UserAuthDecorators._is_demo_mode():
            return UserAuthDecorators._get_demo_user()
        
        user_id = session.get('user_id')
        if not user_id:
            return None
        
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None
    
    @staticmethod
    def _get_demo_user() -> Any:
        """Get demo user object"""
        class DemoUser:
            def __init__(self):
                self.id = 'demo'
                self.username = 'Demo User'
                self.email = 'demo@nous.app'
                self.is_demo = True
                self.active = True
                self.created_at = datetime.utcnow()
                self.last_login = datetime.utcnow()
                self.is_admin = False
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'username': self.username,
                    'email': self.email,
                    'is_demo': self.is_demo,
                    'active': self.active,
                    'created_at': self.created_at.isoformat(),
                    'last_login': self.last_login.isoformat()
                }
        
        return DemoUser()
    
    @staticmethod
    def _get_user_id() -> Optional[str]:
        """Get current user ID"""
        return session.get('user_id')
    
    @staticmethod
    def _validate_session() -> bool:
        """Validate current session"""
        try:
            if not UserAuthDecorators._is_user_authenticated():
                return False
            
            # Check session timeout (24 hours)
            created_at = session.get('created_at')
            if created_at:
                created_time = datetime.fromisoformat(created_at)
                if datetime.utcnow() - created_time > timedelta(hours=24):
                    return False
            
            # Check if user still exists and is active (skip for demo)
            if not UserAuthDecorators._is_demo_mode():
                user_id = session.get('user_id')
                user = User.query.get(user_id)
                if not user or not user.active:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False
    
    @staticmethod
    def _refresh_session() -> None:
        """Refresh session timestamp"""
        session['last_activity'] = datetime.utcnow().isoformat()
    
    @staticmethod
    def _clear_session() -> None:
        """Clear user session"""
        session.clear()
    
    @staticmethod
    def _check_user_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        # Basic permission system (can be extended)
        basic_permissions = [
            'read_profile', 'update_profile', 'read_preferences', 
            'update_preferences', 'read_activity', 'read_insights',
            'use_therapeutic_tools', 'access_ai_assistant'
        ]
        
        if permission in basic_permissions:
            return user.active
        
        # Admin permissions
        admin_permissions = [
            'manage_users', 'access_admin_panel', 'view_system_logs'
        ]
        
        if permission in admin_permissions:
            return getattr(user, 'is_admin', False)
        
        return False
    
    @staticmethod
    def _check_rate_limit(user_id: str, endpoint: str, max_requests: int, per_minutes: int) -> bool:
        """Check rate limiting for user"""
        try:
            # Simple in-memory rate limiting (can be extended with Redis)
            if not hasattr(current_app, 'rate_limits'):
                current_app.rate_limits = {}
            
            key = f"{user_id}:{endpoint}"
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=per_minutes)
            
            if key not in current_app.rate_limits:
                current_app.rate_limits[key] = []
            
            # Clean old requests
            current_app.rate_limits[key] = [
                req_time for req_time in current_app.rate_limits[key] 
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(current_app.rate_limits[key]) >= max_requests:
                return False
            
            # Add current request
            current_app.rate_limits[key].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    @staticmethod
    def _track_user_activity(user_id: str, activity_type: str, activity_data: Dict[str, Any]) -> None:
        """Track user activity"""
        try:
            from models.analytics_models import Activity
            import json
            
            activity = Activity(
                user_id=user_id,
                activity_type=activity_type,
                data=json.dumps(activity_data),
                timestamp=datetime.utcnow()
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error tracking activity: {e}")
            db.session.rollback()
    
    @staticmethod
    def _is_setup_complete(user_id: str) -> bool:
        """Check if user has completed setup wizard"""
        try:
            from models.setup_models import SetupProgress
            
            setup_progress = SetupProgress.query.filter_by(user_id=str(user_id)).first()
            return setup_progress and setup_progress.is_completed
            
        except Exception as e:
            logger.error(f"Error checking setup completion: {e}")
            return True  # Assume complete on error
    
    @staticmethod
    def _get_user_preferences(user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            preferences = UserPreferences.query.filter_by(user_id=str(user_id)).first()
            if preferences:
                return preferences.to_dict()
            return UserAuthDecorators._get_default_preferences()
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return UserAuthDecorators._get_default_preferences()
    
    @staticmethod
    def _get_default_preferences() -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            'primary_language': 'en-US',
            'theme_preference': 'auto',
            'therapeutic_approach': 'integrated',
            'assistant_personality': 'empathetic',
            'assistant_tone': 'compassionate',
            'communication_style': 'balanced',
            'notification_frequency': 'medium',
            'data_privacy_level': 'full',
            'crisis_support_enabled': True,
            'voice_interface_enabled': True
        }
    
    @staticmethod
    def _log_crisis_trigger() -> None:
        """Log crisis keyword detection"""
        try:
            user_id = UserAuthDecorators._get_user_id()
            if user_id:
                UserAuthDecorators._track_user_activity(user_id, 'crisis_trigger', {
                    'timestamp': datetime.utcnow().isoformat(),
                    'endpoint': request.endpoint,
                    'user_agent': request.headers.get('User-Agent', 'Unknown')
                })
        except Exception as e:
            logger.error(f"Error logging crisis trigger: {e}")
    
    @staticmethod
    def _get_crisis_resources() -> Dict[str, Any]:
        """Get crisis intervention resources"""
        return {
            'immediate_help': {
                'national_suicide_prevention_lifeline': '988',
                'crisis_text_line': 'Text HOME to 741741',
                'international_association_for_suicide_prevention': 'https://www.iasp.info/resources/Crisis_Centres/'
            },
            'online_resources': [
                {
                    'name': 'National Suicide Prevention Lifeline',
                    'url': 'https://suicidepreventionlifeline.org/',
                    'description': '24/7 free and confidential support'
                },
                {
                    'name': 'Crisis Text Line',
                    'url': 'https://www.crisistextline.org/',
                    'description': 'Text-based crisis support'
                },
                {
                    'name': 'SAMHSA National Helpline',
                    'url': 'https://www.samhsa.gov/find-help/national-helpline',
                    'description': 'Treatment referral and information service'
                }
            ],
            'message': 'You are not alone. Help is available 24/7. Please reach out to any of these resources for immediate support.'
        }

class UserContextManager:
    """Manage user context throughout request lifecycle"""
    
    @staticmethod
    def inject_user_context():
        """Inject user context into all templates"""
        user = UserAuthDecorators._get_current_user()
        preferences = UserAuthDecorators._get_user_preferences(user.id if user else 'demo')
        
        return {
            'current_user': user,
            'user_preferences': preferences,
            'is_demo_mode': UserAuthDecorators._is_demo_mode(),
            'crisis_resources_available': True
        }
    
    @staticmethod
    def setup_request_context():
        """Setup request context with user data"""
        g.user = UserAuthDecorators._get_current_user()
        g.is_demo = UserAuthDecorators._is_demo_mode()
        
        if g.user:
            g.user_preferences = UserAuthDecorators._get_user_preferences(g.user.id)
        else:
            g.user_preferences = UserAuthDecorators._get_default_preferences()
    
    @staticmethod
    def cleanup_request_context():
        """Cleanup request context"""
        for key in ['user', 'is_demo', 'user_preferences', 'crisis_detected', 'crisis_resources']:
            if hasattr(g, key):
                delattr(g, key)

# Convenience decorator combinations
def authenticated_user(f: Callable) -> Callable:
    """Combined decorator for authenticated user with session validation and activity tracking"""
    @UserAuthDecorators.validate_session
    @UserAuthDecorators.login_required
    @UserAuthDecorators.track_activity('page_view')
    @UserAuthDecorators.preferences_context
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def public_or_demo(f: Callable) -> Callable:
    """Combined decorator for public access with demo fallback"""
    @UserAuthDecorators.validate_session
    @UserAuthDecorators.demo_or_auth_required
    @UserAuthDecorators.track_activity('public_access')
    @UserAuthDecorators.preferences_context
    @UserAuthDecorators.crisis_check
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def therapeutic_endpoint(f: Callable) -> Callable:
    """Combined decorator for therapeutic endpoints with crisis detection"""
    @UserAuthDecorators.validate_session
    @UserAuthDecorators.demo_or_auth_required
    @UserAuthDecorators.setup_required
    @UserAuthDecorators.track_activity('therapeutic_interaction')
    @UserAuthDecorators.preferences_context
    @UserAuthDecorators.crisis_check
    @UserAuthDecorators.rate_limit(max_requests=50, per_minutes=60)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def admin_endpoint(f: Callable) -> Callable:
    """Combined decorator for admin endpoints"""
    @UserAuthDecorators.validate_session
    @UserAuthDecorators.admin_required
    @UserAuthDecorators.track_activity('admin_action')
    @UserAuthDecorators.rate_limit(max_requests=200, per_minutes=60)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function