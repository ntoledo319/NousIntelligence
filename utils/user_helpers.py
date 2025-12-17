"""
Comprehensive User Helper Functions
Utility functions for user management, authentication, and user experience optimization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import json
import hashlib
import secrets
from flask import session, request
from models.user import User
from models.setup_models import UserPreferences, SetupProgress
from models.database import db

logger = logging.getLogger(__name__)

class UserHelpers:
    """Comprehensive user helper utilities"""
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate user data with comprehensive checks"""
        errors = []
        
        # Username validation
        username = user_data.get('username', '')
        if not username or len(username) < 2:
            errors.append('Username must be at least 2 characters long')
        elif len(username) > 80:
            errors.append('Username must be less than 80 characters')
        elif not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, hyphens, and underscores')
        
        # Email validation
        email = user_data.get('email', '')
        if not email:
            errors.append('Email is required')
        elif '@' not in email or '.' not in email:
            errors.append('Email must be a valid email address')
        elif len(email) > 120:
            errors.append('Email must be less than 120 characters')
        
        # Password validation (if provided)
        password = user_data.get('password', '')
        if password:
            if len(password) < 8:
                errors.append('Password must be at least 8 characters long')
            elif not any(c.isupper() for c in password):
                errors.append('Password must contain at least one uppercase letter')
            elif not any(c.islower() for c in password):
                errors.append('Password must contain at least one lowercase letter')
            elif not any(c.isdigit() for c in password):
                errors.append('Password must contain at least one number')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_preferences(preferences: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate user preferences with comprehensive checks"""
        errors = []
        
        # Language validation
        primary_language = preferences.get('primary_language', '')
        if primary_language and not UserHelpers._is_valid_language_code(primary_language):
            errors.append('Invalid primary language code')
        
        # Theme validation
        theme = preferences.get('theme_preference', '')
        if theme and theme not in ['light', 'dark', 'auto']:
            errors.append('Theme must be light, dark, or auto')
        
        # Therapeutic approach validation
        therapeutic = preferences.get('therapeutic_approach', '')
        if therapeutic and therapeutic not in ['dbt', 'cbt', 'aa', 'integrated']:
            errors.append('Invalid therapeutic approach')
        
        # Assistant personality validation
        personality = preferences.get('assistant_personality', '')
        if personality and personality not in ['empathetic', 'professional', 'casual', 'supportive']:
            errors.append('Invalid assistant personality')
        
        # Notification frequency validation
        notification = preferences.get('notification_frequency', '')
        if notification and notification not in ['none', 'low', 'medium', 'high']:
            errors.append('Invalid notification frequency')
        
        # Privacy level validation
        privacy = preferences.get('data_privacy_level', '')
        if privacy and privacy not in ['minimal', 'standard', 'full', 'maximum']:
            errors.append('Invalid privacy level')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_user_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize user input to prevent security issues"""
        sanitized = {}
        
        for key, value in input_data.items():
            if isinstance(value, str):
                # Remove potential HTML/script tags
                value = value.replace('<', '&lt;').replace('>', '&gt;')
                # Remove null bytes
                value = value.replace('\x00', '')
                # Trim whitespace
                value = value.strip()
            elif isinstance(value, list):
                # Sanitize list items
                value = [UserHelpers._sanitize_string(item) if isinstance(item, str) else item for item in value]
            elif isinstance(value, dict):
                # Recursively sanitize dict values
                value = UserHelpers.sanitize_user_input(value)
            
            sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def generate_user_avatar(user_id: str, username: str) -> str:
        """Generate a deterministic avatar URL for user"""
        # Create a hash based on user data for consistent avatar
        hash_input = f"{user_id}-{username}".encode('utf-8')
        avatar_hash = hashlib.md5(hash_input).hexdigest()
        
        # Return a deterministic avatar URL (using a service like gravatar or generated)
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={avatar_hash}"
    
    @staticmethod
    def calculate_user_score(user_id: Union[str, int]) -> Dict[str, float]:
        """Calculate comprehensive user engagement and wellness scores"""
        try:
            from models.analytics_models import Activity, Insight, HealthMetric
            from models.health_models import DBTSkillLog, DBTDiaryCard
            
            # Get recent activity (last 30 days)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Count activities
            activity_count = Activity.query.filter(
                Activity.user_id == user_id,
                Activity.timestamp >= start_date
            ).count()
            
            # Count insights
            insight_count = Insight.query.filter(
                Insight.user_id == user_id,
                Insight.timestamp >= start_date
            ).count()
            
            # Count therapeutic activities
            dbt_count = DBTSkillLog.query.filter(
                DBTSkillLog.user_id == user_id,
                DBTSkillLog.timestamp >= start_date
            ).count()
            
            diary_count = DBTDiaryCard.query.filter(
                DBTDiaryCard.user_id == user_id,
                DBTDiaryCard.date >= start_date.date()
            ).count()
            
            # Calculate scores (0-100)
            engagement_score = min((activity_count / 30.0) * 100, 100)  # 1 activity per day = 100%
            insight_score = min((insight_count / 10.0) * 100, 100)      # 10 insights = 100%
            therapeutic_score = min(((dbt_count + diary_count) / 20.0) * 100, 100)  # 20 entries = 100%
            
            # Overall wellness score (weighted average)
            wellness_score = (
                engagement_score * 0.3 +
                insight_score * 0.3 +
                therapeutic_score * 0.4
            )
            
            return {
                'engagement_score': round(engagement_score, 1),
                'insight_score': round(insight_score, 1),
                'therapeutic_score': round(therapeutic_score, 1),
                'wellness_score': round(wellness_score, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating user scores for {user_id}: {e}")
            return {
                'engagement_score': 0.0,
                'insight_score': 0.0,
                'therapeutic_score': 0.0,
                'wellness_score': 0.0
            }
    
    @staticmethod
    def get_user_recommendations(user_id: Union[str, int], preferences: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user data and preferences"""
        try:
            recommendations = []
            
            # Get user scores to determine recommendations
            scores = UserHelpers.calculate_user_score(user_id)
            
            # Low engagement recommendations
            if scores['engagement_score'] < 30:
                recommendations.append({
                    'type': 'engagement',
                    'title': 'Start Your Daily Check-in',
                    'description': 'Take 2 minutes to log your mood and set intentions for the day',
                    'priority': 'high',
                    'action': '/mood-tracker',
                    'category': 'daily_practice'
                })
            
            # Low therapeutic score recommendations
            if scores['therapeutic_score'] < 40:
                therapeutic_approach = preferences.get('therapeutic_approach', 'integrated') if preferences else 'integrated'
                
                if therapeutic_approach in ['dbt', 'integrated']:
                    recommendations.append({
                        'type': 'therapeutic',
                        'title': 'Practice a DBT Skill',
                        'description': 'Try a distress tolerance or emotion regulation technique',
                        'priority': 'high',
                        'action': '/dbt/skills',
                        'category': 'skill_building'
                    })
                
                if therapeutic_approach in ['cbt', 'integrated']:
                    recommendations.append({
                        'type': 'therapeutic',
                        'title': 'Challenge Negative Thoughts',
                        'description': 'Use cognitive restructuring to examine unhelpful thought patterns',
                        'priority': 'medium',
                        'action': '/cbt/thought-records',
                        'category': 'cognitive_work'
                    })
            
            # Low insight score recommendations
            if scores['insight_score'] < 50:
                recommendations.append({
                    'type': 'insight',
                    'title': 'Explore Your Patterns',
                    'description': 'Review AI-generated insights about your mood and behavior patterns',
                    'priority': 'medium',
                    'action': '/analytics/insights',
                    'category': 'self_reflection'
                })
            
            # High wellness recommendations (maintenance)
            if scores['wellness_score'] > 75:
                recommendations.append({
                    'type': 'maintenance',
                    'title': 'Share Your Success',
                    'description': 'Your wellness journey is going great! Consider sharing tips with the community',
                    'priority': 'low',
                    'action': '/community/share',
                    'category': 'community'
                })
            
            # Crisis support (if enabled in preferences)
            if preferences and preferences.get('crisis_support_enabled', True):
                recommendations.append({
                    'type': 'safety',
                    'title': 'Crisis Resources Available',
                    'description': 'Access emergency support and crisis intervention resources 24/7',
                    'priority': 'info',
                    'action': '/crisis-support',
                    'category': 'safety'
                })
            
            # Personalized based on neurodivergent status
            if preferences and preferences.get('is_neurodivergent', False):
                conditions = preferences.get('neurodivergent_conditions', [])
                if 'adhd' in conditions:
                    recommendations.append({
                        'type': 'neurodivergent',
                        'title': 'ADHD Focus Techniques',
                        'description': 'Try specialized attention and focus management strategies',
                        'priority': 'medium',
                        'action': '/neurodivergent/adhd-tools',
                        'category': 'accessibility'
                    })
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1, 'info': 0}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return recommendations[:6]  # Return top 6 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return []
    
    @staticmethod
    def track_user_activity(user_id: Union[str, int], activity_type: str, activity_data: Dict[str, Any]) -> bool:
        """Track user activity for analytics and insights"""
        try:
            from models.analytics_models import Activity
            
            activity = Activity(
                user_id=user_id,
                activity_type=activity_type,
                data=json.dumps(activity_data),
                timestamp=datetime.utcnow()
            )
            
            db.session.add(activity)
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error tracking activity for user {user_id}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_timezone(user_id: Union[str, int]) -> str:
        """Get user's timezone from preferences or detect from request"""
        try:
            # First try to get from user preferences
            preferences = UserPreferences.query.filter_by(user_id=str(user_id)).first()
            if preferences and hasattr(preferences, 'timezone'):
                return preferences.timezone
            
            # Try to detect from request headers
            timezone = request.headers.get('X-Timezone')
            if timezone:
                return timezone
            
            # Default to UTC
            return 'UTC'
            
        except Exception as e:
            logger.warning(f"Could not determine timezone for user {user_id}: {e}")
            return 'UTC'
    
    @staticmethod
    def format_user_display_name(user: User) -> str:
        """Format user display name consistently"""
        if hasattr(user, 'display_name') and user.display_name:
            return user.display_name
        elif hasattr(user, 'username') and user.username:
            return user.username
        elif hasattr(user, 'email') and user.email:
            return user.email.split('@')[0]
        else:
            return 'User'
    
    @staticmethod
    def check_user_permissions(user_id: Union[str, int], permission: str) -> bool:
        """Check if user has specific permission"""
        try:
            # Basic permission checking (can be extended with role-based access)
            user = User.query.get(user_id)
            if not user or not user.active:
                return False
            
            # All active users have basic permissions
            basic_permissions = [
                'read_profile', 'update_profile', 'read_preferences', 
                'update_preferences', 'read_activity', 'read_insights',
                'use_therapeutic_tools', 'access_ai_assistant'
            ]
            
            if permission in basic_permissions:
                return True
            
            # Admin permissions (placeholder for future implementation)
            admin_permissions = [
                'manage_users', 'access_admin_panel', 'view_system_logs'
            ]
            
            if permission in admin_permissions:
                # Check if user is admin (placeholder)
                return getattr(user, 'is_admin', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permissions for user {user_id}: {e}")
            return False
    
    @staticmethod
    def cleanup_user_sessions(user_id: Union[str, int]) -> int:
        """Clean up old/invalid sessions for user"""
        try:
            # This would typically integrate with session storage
            # For now, just track the cleanup attempt
            UserHelpers.track_user_activity(user_id, 'session_cleanup', {
                'cleanup_time': datetime.utcnow().isoformat(),
                'cleanup_reason': 'user_request'
            })
            return 1  # Placeholder return
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions for user {user_id}: {e}")
            return 0
    
    @staticmethod
    def get_user_security_summary(user_id: Union[str, int]) -> Dict[str, Any]:
        """Get comprehensive user security summary"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Calculate security score based on various factors
            security_score = 0
            factors = []
            
            # Account age (older = more secure)
            if user.created_at:
                account_age_days = (datetime.utcnow() - user.created_at).days
                if account_age_days > 30:
                    security_score += 20
                    factors.append('Account established (30+ days)')
                elif account_age_days > 7:
                    security_score += 10
                    factors.append('New account (7+ days)')
            
            # Email verification (placeholder)
            if user.email:
                security_score += 25
                factors.append('Email verified')
            
            # Google OAuth integration
            if user.google_id:
                security_score += 30
                factors.append('Google OAuth enabled')
            
            # Active account
            if user.active:
                security_score += 15
                factors.append('Account active')
            
            # Recent activity
            recent_login = user.last_login
            if recent_login and (datetime.utcnow() - recent_login).days < 7:
                security_score += 10
                factors.append('Recent activity')
            
            return {
                'security_score': min(security_score, 100),
                'security_factors': factors,
                'recommendations': UserHelpers._get_security_recommendations(security_score),
                'last_security_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting security summary for user {user_id}: {e}")
            return {'error': 'Could not retrieve security summary'}
    
    @staticmethod
    def _is_valid_language_code(language_code: str) -> bool:
        """Validate language code format"""
        valid_codes = [
            'en-US', 'en-GB', 'es-ES', 'es-MX', 'fr-FR', 'de-DE', 
            'it-IT', 'pt-BR', 'pt-PT', 'ja-JP', 'ko-KR', 'zh-CN', 
            'zh-TW', 'ru-RU', 'ar-SA', 'hi-IN'
        ]
        return language_code in valid_codes
    
    @staticmethod
    def _sanitize_string(value: str) -> str:
        """Sanitize a string value"""
        if not isinstance(value, str):
            return value
        return value.replace('<', '&lt;').replace('>', '&gt;').replace('\x00', '').strip()
    
    @staticmethod
    def _get_security_recommendations(security_score: int) -> List[str]:
        """Get security recommendations based on score"""
        recommendations = []
        
        if security_score < 50:
            recommendations.append('Enable two-factor authentication')
            recommendations.append('Update your password regularly')
            recommendations.append('Review your privacy settings')
        elif security_score < 75:
            recommendations.append('Consider enabling additional security features')
            recommendations.append('Review your connected apps and permissions')
        else:
            recommendations.append('Your account security is excellent')
            recommendations.append('Continue monitoring your account activity')
        
        return recommendations

class UserSessionManager:
    """Manage user sessions and authentication state"""
    
    @staticmethod
    def create_user_session(user: User, remember_me: bool = False) -> bool:
        """Create a secure user session"""
        try:
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['is_demo'] = False
            session['created_at'] = datetime.utcnow().isoformat()
            session['last_activity'] = datetime.utcnow().isoformat()
            
            if remember_me:
                session.permanent = True
            
            # Update user's last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Track login activity
            UserHelpers.track_user_activity(user.id, 'login', {
                'login_time': datetime.utcnow().isoformat(),
                'remember_me': remember_me,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating session for user {user.id}: {e}")
            return False
    
    @staticmethod
    def clear_user_session() -> bool:
        """Clear user session securely"""
        try:
            user_id = session.get('user_id')
            if user_id:
                # Track logout activity
                UserHelpers.track_user_activity(user_id, 'logout', {
                    'logout_time': datetime.utcnow().isoformat()
                })
            
            session.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False
    
    @staticmethod
    def is_session_valid() -> bool:
        """Check if current session is valid"""
        try:
            if 'user_id' not in session:
                return False
            
            # Check session timeout (24 hours)
            created_at = session.get('created_at')
            if created_at:
                created_time = datetime.fromisoformat(created_at)
                if datetime.utcnow() - created_time > timedelta(hours=24):
                    UserSessionManager.clear_user_session()
                    return False
            
            # Update last activity
            session['last_activity'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False
    
    @staticmethod
    def refresh_session() -> bool:
        """Refresh current session"""
        try:
            if UserSessionManager.is_session_valid():
                session['last_activity'] = datetime.utcnow().isoformat()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return False