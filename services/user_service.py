"""
Comprehensive User Service
Handles all user-related business logic, data management, and user experience optimization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
import json
from sqlalchemy import func, and_, or_
from models.user import User
from models.setup_models import UserPreferences, SetupProgress
from models.analytics_models import Activity, Insight, HealthMetric
from models.health_models import DBTSkillLog, DBTDiaryCard, DBTEmotionTrack
from database import db

logger = logging.getLogger(__name__)

class UserService:
    """Comprehensive user management service"""
    
    @staticmethod
    def get_user_by_id(user_id: Union[str, int]) -> Optional[User]:
        """Get user by ID with comprehensive error handling"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            return None
    
    @staticmethod
    def get_user_by_google_id(google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        try:
            return User.query.filter_by(google_id=google_id).first()
        except Exception as e:
            logger.error(f"Error retrieving user by Google ID {google_id}: {e}")
            return None
    
    @staticmethod
    def create_user(username: str, email: str, google_id: Optional[str] = None) -> Optional[User]:
        """Create new user with comprehensive setup"""
        try:
            # Check if user already exists
            existing_user = UserService.get_user_by_email(email)
            if existing_user:
                logger.warning(f"User with email {email} already exists")
                return existing_user
            
            # Create new user
            user = User(
                username=username,
                email=email,
                google_id=google_id,
                active=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create default setup progress
            setup_progress = SetupProgress(
                user_id=str(user.id),
                current_step='welcome',
                completed_steps=[],
                is_completed=False
            )
            db.session.add(setup_progress)
            
            # Create default preferences
            preferences = UserPreferences(
                user_id=str(user.id),
                primary_language='en-US',
                theme_preference='auto',
                therapeutic_approach='integrated',
                assistant_personality='empathetic',
                assistant_tone='compassionate',
                communication_style='balanced',
                notification_frequency='medium',
                data_privacy_level='full',
                crisis_support_enabled=True,
                voice_interface_enabled=True
            )
            db.session.add(preferences)
            
            db.session.commit()
            logger.info(f"Created new user: {username} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_user_profile(user_id: Union[str, int], updates: Dict[str, Any]) -> bool:
        """Update user profile information"""
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False
            
            # Update allowed fields
            if 'username' in updates:
                user.username = updates['username']
            if 'email' in updates:
                user.email = updates['email']
            if 'active' in updates:
                user.active = bool(updates['active'])
            
            db.session.commit()
            logger.info(f"Updated profile for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_preferences(user_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Get comprehensive user preferences"""
        try:
            preferences = UserPreferences.query.filter_by(user_id=str(user_id)).first()
            if not preferences:
                return UserService._get_default_preferences(user_id)
            return preferences.to_dict()
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            return UserService._get_default_preferences(user_id)
    
    @staticmethod
    def update_user_preferences(user_id: Union[str, int], preferences: Dict[str, Any]) -> bool:
        """Update user preferences with comprehensive validation"""
        try:
            user_prefs = UserPreferences.query.filter_by(user_id=str(user_id)).first()
            if not user_prefs:
                user_prefs = UserPreferences(user_id=str(user_id))
                db.session.add(user_prefs)
            
            # Update preferences with validation
            preference_fields = [
                'primary_language', 'secondary_languages', 'learning_languages',
                'is_neurodivergent', 'neurodivergent_conditions', 'theme_preference',
                'color_scheme', 'font_size', 'high_contrast', 'mental_health_goals',
                'therapeutic_approach', 'crisis_support_enabled', 'assistant_personality',
                'assistant_tone', 'communication_style', 'ai_assistance_level',
                'health_tracking_interests', 'wellness_goals', 'reminder_preferences',
                'notification_frequency', 'data_privacy_level', 'sharing_preferences',
                'voice_interface_enabled', 'voice_interface_mode', 'motor_accessibility',
                'cognitive_support_level', 'emergency_contacts', 'safety_planning_enabled',
                'location_services_enabled', 'budget_tracking_enabled',
                'financial_privacy_level', 'family_features_enabled', 'collaboration_level'
            ]
            
            for field in preference_fields:
                if field in preferences:
                    setattr(user_prefs, field, preferences[field])
            
            user_prefs.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_activity_summary(user_id: Union[str, int], days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user activity summary"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get activities
            activities = Activity.query.filter(
                and_(
                    Activity.user_id == user_id,
                    Activity.timestamp >= start_date,
                    Activity.timestamp <= end_date
                )
            ).order_by(Activity.timestamp.desc()).all()
            
            # Get insights
            insights = Insight.query.filter(
                and_(
                    Insight.user_id == user_id,
                    Insight.timestamp >= start_date,
                    Insight.timestamp <= end_date
                )
            ).order_by(Insight.timestamp.desc()).all()
            
            # Get health metrics
            health_metrics = HealthMetric.query.filter(
                and_(
                    HealthMetric.user_id == user_id,
                    HealthMetric.recorded_at >= start_date,
                    HealthMetric.recorded_at <= end_date
                )
            ).order_by(HealthMetric.recorded_at.desc()).all()
            
            # Calculate summary statistics
            activity_count_by_type = {}
            for activity in activities:
                activity_type = getattr(activity, 'activity_type', 'unknown')
                activity_count_by_type[activity_type] = activity_count_by_type.get(activity_type, 0) + 1
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'activities': {
                    'total': len(activities),
                    'by_type': activity_count_by_type,
                    'recent': [activity.to_dict() for activity in activities[:10]]
                },
                'insights': {
                    'total': len(insights),
                    'recent': [insight.to_dict() for insight in insights[:5]]
                },
                'health_metrics': {
                    'total': len(health_metrics),
                    'recent': [metric.to_dict() for metric in health_metrics[:5]]
                },
                'engagement_score': UserService._calculate_engagement_score(activities, insights, health_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving activity summary for user {user_id}: {e}")
            return {'error': 'Could not retrieve activity summary'}
    
    @staticmethod
    def get_therapeutic_progress(user_id: Union[str, int]) -> Dict[str, Any]:
        """Get comprehensive therapeutic progress summary"""
        try:
            # Get DBT skill logs
            dbt_skills = DBTSkillLog.query.filter_by(user_id=user_id).all()
            
            # Get diary cards
            diary_cards = DBTDiaryCard.query.filter_by(user_id=user_id).all()
            
            # Get emotion tracking
            emotion_tracks = DBTEmotionTrack.query.filter_by(user_id=user_id).all()
            
            # Calculate progress metrics
            skills_practiced = len(set([skill.skill_name for skill in dbt_skills]))
            total_sessions = len(diary_cards)
            mood_entries = len(emotion_tracks)
            
            # Calculate skill effectiveness
            skill_effectiveness = {}
            for skill in dbt_skills:
                skill_name = skill.skill_name
                if skill_name not in skill_effectiveness:
                    skill_effectiveness[skill_name] = {
                        'usage_count': 0,
                        'total_effectiveness': 0,
                        'average_effectiveness': 0
                    }
                
                skill_effectiveness[skill_name]['usage_count'] += 1
                if hasattr(skill, 'effectiveness_rating') and skill.effectiveness_rating:
                    skill_effectiveness[skill_name]['total_effectiveness'] += skill.effectiveness_rating
            
            # Calculate averages
            for skill_name in skill_effectiveness:
                if skill_effectiveness[skill_name]['usage_count'] > 0:
                    skill_effectiveness[skill_name]['average_effectiveness'] = (
                        skill_effectiveness[skill_name]['total_effectiveness'] / 
                        skill_effectiveness[skill_name]['usage_count']
                    )
            
            return {
                'summary': {
                    'total_sessions': total_sessions,
                    'skills_practiced': skills_practiced,
                    'mood_entries': mood_entries,
                    'goals_achieved': 0  # Placeholder for future implementation
                },
                'skill_effectiveness': skill_effectiveness,
                'recent_activities': {
                    'dbt_skills': [skill.to_dict() for skill in dbt_skills[-5:]],
                    'diary_cards': [card.to_dict() for card in diary_cards[-3:]],
                    'emotion_tracks': [track.to_dict() for track in emotion_tracks[-5:]]
                },
                'progress_trends': UserService._calculate_therapeutic_trends(dbt_skills, diary_cards, emotion_tracks)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving therapeutic progress for user {user_id}: {e}")
            return {'error': 'Could not retrieve therapeutic progress'}
    
    @staticmethod
    def get_user_dashboard_data(user_id: Union[str, int]) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Get all user data
            preferences = UserService.get_user_preferences(user_id)
            activity_summary = UserService.get_user_activity_summary(user_id, days=30)
            therapeutic_progress = UserService.get_therapeutic_progress(user_id)
            setup_progress = SetupProgress.query.filter_by(user_id=str(user_id)).first()
            
            return {
                'user': user.to_dict(),
                'setup_progress': setup_progress.to_dict() if setup_progress else None,
                'preferences': preferences,
                'activity_summary': activity_summary,
                'therapeutic_progress': therapeutic_progress,
                'dashboard_widgets': UserService._get_dashboard_widgets(user_id),
                'recommendations': UserService._get_user_recommendations(user_id),
                'quick_actions': UserService._get_quick_actions(user_id, preferences)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving dashboard data for user {user_id}: {e}")
            return {'error': 'Could not retrieve dashboard data'}
    
    @staticmethod
    def export_user_data(user_id: Union[str, int]) -> Dict[str, Any]:
        """Export comprehensive user data"""
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Collect all user data
            export_data = {
                'export_info': {
                    'user_id': str(user_id),
                    'export_date': datetime.utcnow().isoformat(),
                    'format_version': '1.0'
                },
                'user_profile': user.to_dict(),
                'preferences': UserService.get_user_preferences(user_id),
                'setup_progress': None,
                'activities': [],
                'insights': [],
                'health_metrics': [],
                'therapeutic_data': UserService.get_therapeutic_progress(user_id),
                'privacy_notice': 'This export contains all your personal data stored in the NOUS platform.'
            }
            
            # Add setup progress
            setup_progress = SetupProgress.query.filter_by(user_id=str(user_id)).first()
            if setup_progress:
                export_data['setup_progress'] = setup_progress.to_dict()
            
            # Add activities
            activities = Activity.query.filter_by(user_id=user_id).all()
            export_data['activities'] = [activity.to_dict() for activity in activities]
            
            # Add insights
            insights = Insight.query.filter_by(user_id=user_id).all()
            export_data['insights'] = [insight.to_dict() for insight in insights]
            
            # Add health metrics
            health_metrics = HealthMetric.query.filter_by(user_id=user_id).all()
            export_data['health_metrics'] = [metric.to_dict() for metric in health_metrics]
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting data for user {user_id}: {e}")
            return {'error': 'Could not export user data'}
    
    @staticmethod
    def delete_user_data(user_id: Union[str, int], confirmation: str) -> Dict[str, Any]:
        """Delete user account and all associated data"""
        try:
            if confirmation != 'DELETE_MY_ACCOUNT':
                return {'error': 'Invalid confirmation', 'success': False}
            
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {'error': 'User not found', 'success': False}
            
            # Delete related data (in proper order to avoid foreign key constraints)
            
            # Delete therapeutic data
            DBTSkillLog.query.filter_by(user_id=user_id).delete()
            DBTDiaryCard.query.filter_by(user_id=user_id).delete()
            DBTEmotionTrack.query.filter_by(user_id=user_id).delete()
            
            # Delete analytics data
            Activity.query.filter_by(user_id=user_id).delete()
            Insight.query.filter_by(user_id=user_id).delete()
            HealthMetric.query.filter_by(user_id=user_id).delete()
            
            # Delete setup data
            UserPreferences.query.filter_by(user_id=str(user_id)).delete()
            SetupProgress.query.filter_by(user_id=str(user_id)).delete()
            
            # Finally delete user
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"Deleted user account and all data for user {user_id}")
            return {'success': True, 'message': 'Account and all data deleted successfully'}
            
        except Exception as e:
            logger.error(f"Error deleting user data for user {user_id}: {e}")
            db.session.rollback()
            return {'error': 'Could not delete user data', 'success': False}
    
    @staticmethod
    def _get_default_preferences(user_id: Union[str, int]) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            'user_id': str(user_id),
            'primary_language': 'en-US',
            'theme_preference': 'auto',
            'therapeutic_approach': 'integrated',
            'assistant_personality': 'empathetic',
            'assistant_tone': 'compassionate',
            'communication_style': 'balanced',
            'notification_frequency': 'medium',
            'data_privacy_level': 'full',
            'crisis_support_enabled': True,
            'voice_interface_enabled': True,
            'voice_interface_mode': 'push-to-talk',
            'safety_planning_enabled': True,
            'is_neurodivergent': False,
            'neurodivergent_conditions': [],
            'mental_health_goals': [],
            'emergency_contacts': []
        }
    
    @staticmethod
    def _calculate_engagement_score(activities: List, insights: List, health_metrics: List) -> float:
        """Calculate user engagement score based on activity"""
        try:
            # Simple engagement scoring algorithm
            activity_score = min(len(activities) / 10.0, 1.0) * 40  # Max 40 points
            insight_score = min(len(insights) / 5.0, 1.0) * 30     # Max 30 points  
            health_score = min(len(health_metrics) / 10.0, 1.0) * 30  # Max 30 points
            
            return round(activity_score + insight_score + health_score, 1)
        except Exception:
            return 0.0
    
    @staticmethod
    def _calculate_therapeutic_trends(dbt_skills: List, diary_cards: List, emotion_tracks: List) -> Dict[str, Any]:
        """Calculate therapeutic progress trends"""
        try:
            # Simple trend calculation
            recent_skills = len([skill for skill in dbt_skills if hasattr(skill, 'created_at') and 
                               skill.created_at > datetime.utcnow() - timedelta(days=7)])
            recent_diary = len([card for card in diary_cards if hasattr(card, 'created_at') and 
                              card.created_at > datetime.utcnow() - timedelta(days=7)])
            recent_emotions = len([track for track in emotion_tracks if hasattr(track, 'created_at') and 
                                 track.created_at > datetime.utcnow() - timedelta(days=7)])
            
            return {
                'weekly_skill_usage': recent_skills,
                'weekly_diary_entries': recent_diary,
                'weekly_emotion_tracking': recent_emotions,
                'trend_direction': 'improving' if (recent_skills + recent_diary + recent_emotions) > 3 else 'stable'
            }
        except Exception:
            return {'trend_direction': 'unknown'}
    
    @staticmethod
    def _get_dashboard_widgets(user_id: Union[str, int]) -> List[Dict[str, Any]]:
        """Get dashboard widgets for user"""
        return [
            {
                'type': 'therapeutic_progress',
                'title': 'Therapeutic Progress',
                'priority': 1,
                'enabled': True
            },
            {
                'type': 'mood_tracker',
                'title': 'Mood Tracking',
                'priority': 2,
                'enabled': True
            },
            {
                'type': 'skill_practice',
                'title': 'Skill Practice',
                'priority': 3,
                'enabled': True
            },
            {
                'type': 'insights',
                'title': 'AI Insights',
                'priority': 4,
                'enabled': True
            }
        ]
    
    @staticmethod
    def _get_user_recommendations(user_id: Union[str, int]) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user"""
        return [
            {
                'type': 'skill_practice',
                'title': 'Practice Mindfulness Today',
                'description': 'Try a 5-minute mindfulness exercise to reduce stress',
                'priority': 'high',
                'action_url': '/dbt/mindfulness'
            },
            {
                'type': 'mood_tracking',
                'title': 'Log Your Mood',
                'description': 'Track your emotional state to identify patterns',
                'priority': 'medium',
                'action_url': '/mood-tracker'
            },
            {
                'type': 'therapeutic_goal',
                'title': 'Set Weekly Goal',
                'description': 'Define a therapeutic goal for this week',
                'priority': 'medium',
                'action_url': '/goals/create'
            }
        ]
    
    @staticmethod
    def _get_quick_actions(user_id: Union[str, int], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get quick actions based on user preferences"""
        actions = [
            {
                'title': 'Chat with AI Assistant',
                'icon': 'chat',
                'url': '/chat',
                'type': 'primary'
            },
            {
                'title': 'Practice DBT Skill',
                'icon': 'brain',
                'url': '/dbt/skills',
                'type': 'therapeutic'
            },
            {
                'title': 'Log Mood',
                'icon': 'heart',
                'url': '/mood-tracker',
                'type': 'tracking'
            },
            {
                'title': 'View Insights',
                'icon': 'chart',
                'url': '/analytics/insights',
                'type': 'analytics'
            }
        ]
        
        # Customize based on preferences
        if preferences and preferences.get('voice_interface_enabled'):
            actions.append({
                'title': 'Voice Assistant',
                'icon': 'microphone',
                'url': '/voice-interface',
                'type': 'voice'
            })
        
        return actions