"""
Setup Service

Business logic for the user setup wizard and onboarding process.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from models.database import db
from models.setup_models import SetupProgress, UserPreferences
from models.user import User

logger = logging.getLogger(__name__)


class SetupService:
    """Service for managing user setup and onboarding"""
    
    # Setup steps in order
    SETUP_STEPS = [
        'welcome',
        'languages', 
        'neurodivergent',
        'mental_health',
        'ai_assistant',
        'health_wellness',
        'theme_accessibility',
        'notifications_privacy',
        'integrations',
        'emergency_safety',
        'features_guide',
        'complete'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_or_create_setup_progress(self, user_id: str) -> SetupProgress:
        """Get or create setup progress for user"""
        try:
            progress = SetupProgress.query.filter_by(user_id=user_id).first()
            if not progress:
                progress = SetupProgress(
                    user_id=user_id,
                    current_step='welcome',
                    completed_steps=[]
                )
                db.session.add(progress)
                db.session.commit()
            return progress
        except Exception as e:
            self.logger.error(f"Error getting/creating setup progress: {e}")
            db.session.rollback()
            raise
    
    def get_or_create_user_preferences(self, user_id: str) -> UserPreferences:
        """Get or create user preferences"""
        try:
            preferences = UserPreferences.query.filter_by(user_id=user_id).first()
            if not preferences:
                preferences = UserPreferences(user_id=user_id)
                db.session.add(preferences)
                db.session.commit()
            return preferences
        except Exception as e:
            self.logger.error(f"Error getting/creating user preferences: {e}")
            db.session.rollback()
            raise
    
    def update_setup_step(self, user_id: str, step: str, data: Dict[str, Any] = None) -> bool:
        """Update setup progress and save step data"""
        try:
            progress = self.get_or_create_setup_progress(user_id)
            preferences = self.get_or_create_user_preferences(user_id)
            
            # Mark step as completed
            if step not in progress.completed_steps:
                completed_steps = progress.completed_steps or []
                completed_steps.append(step)
                progress.completed_steps = completed_steps
            
            # Update current step to next step
            try:
                current_index = self.SETUP_STEPS.index(step)
                if current_index < len(self.SETUP_STEPS) - 1:
                    progress.current_step = self.SETUP_STEPS[current_index + 1]
                else:
                    progress.current_step = 'complete'
                    progress.is_completed = True
                    progress.completed_at = datetime.utcnow()
            except ValueError:
                # Step not in list, keep current
                pass
            
            progress.updated_at = datetime.utcnow()
            
            # Save step-specific data
            if data:
                self._save_step_data(preferences, step, data)
            
            db.session.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating setup step: {e}")
            db.session.rollback()
            return False
    
    def _save_step_data(self, preferences: UserPreferences, step: str, data: Dict[str, Any]):
        """Save step-specific data to preferences"""
        if step == 'languages':
            preferences.primary_language = data.get('primary_language', 'en-US')
            preferences.secondary_languages = data.get('secondary_languages', [])
            preferences.learning_languages = data.get('learning_languages', [])
            
        elif step == 'neurodivergent':
            preferences.is_neurodivergent = data.get('is_neurodivergent', False)
            preferences.neurodivergent_conditions = data.get('conditions', [])
            
        elif step == 'mental_health':
            preferences.mental_health_goals = data.get('goals', [])
            preferences.therapeutic_approach = data.get('therapeutic_approach', 'integrated')
            preferences.crisis_support_enabled = data.get('crisis_support', True)
            
        elif step == 'ai_assistant':
            preferences.assistant_personality = data.get('personality', 'empathetic')
            preferences.assistant_tone = data.get('tone', 'compassionate')
            preferences.communication_style = data.get('communication_style', 'balanced')
            preferences.ai_assistance_level = data.get('assistance_level', 'responsive')
            
        elif step == 'health_wellness':
            preferences.health_tracking_interests = data.get('health_tracking', [])
            preferences.wellness_goals = data.get('wellness_goals', [])
            preferences.reminder_preferences = data.get('reminders', {})
            
        elif step == 'theme_accessibility':
            preferences.theme_preference = data.get('theme', 'auto')
            preferences.color_scheme = data.get('color_scheme', 'blue')
            preferences.font_size = data.get('font_size', 'medium')
            preferences.high_contrast = data.get('high_contrast', False)
            preferences.voice_interface_enabled = data.get('voice_enabled', True)
            preferences.voice_interface_mode = data.get('voice_mode', 'push-to-talk')
            preferences.motor_accessibility = data.get('motor_accessibility', {})
            preferences.cognitive_support_level = data.get('cognitive_support', 'standard')
            
        elif step == 'notifications_privacy':
            preferences.notification_frequency = data.get('notification_frequency', 'medium')
            preferences.data_privacy_level = data.get('privacy_level', 'full')
            preferences.sharing_preferences = data.get('sharing', {})
            
        elif step == 'integrations':
            preferences.google_services_integration = data.get('google_services', {})
            preferences.spotify_integration_enabled = data.get('spotify_enabled', True)
            preferences.external_integrations = data.get('external', {})
            preferences.budget_tracking_enabled = data.get('budget_tracking', False)
            preferences.financial_privacy_level = data.get('financial_privacy', 'full')
            preferences.family_features_enabled = data.get('family_features', False)
            preferences.collaboration_level = data.get('collaboration_level', 'private')
            
        elif step == 'emergency_safety':
            preferences.emergency_contacts = data.get('emergency_contacts', [])
            preferences.safety_planning_enabled = data.get('safety_planning', True)
            preferences.location_services_enabled = data.get('location_services', False)
        
        preferences.updated_at = datetime.utcnow()
    
    def get_setup_data(self, user_id: str) -> Dict[str, Any]:
        """Get complete setup data for user"""
        try:
            progress = self.get_or_create_setup_progress(user_id)
            preferences = self.get_or_create_user_preferences(user_id)
            
            return {
                'progress': progress.to_dict(),
                'preferences': preferences.to_dict(),
                'next_step': progress.current_step,
                'is_completed': progress.is_completed,
                'setup_steps': self.SETUP_STEPS
            }
        except Exception as e:
            self.logger.error(f"Error getting setup data: {e}")
            return {
                'progress': {},
                'preferences': {},
                'next_step': 'welcome',
                'is_completed': False,
                'setup_steps': self.SETUP_STEPS
            }
    
    def is_setup_completed(self, user_id: str) -> bool:
        """Check if user has completed setup"""
        try:
            progress = SetupProgress.query.filter_by(user_id=user_id).first()
            return progress and progress.is_completed
        except Exception as e:
            self.logger.error(f"Error checking setup completion: {e}")
            return False
    
    def get_step_progress(self, user_id: str) -> Dict[str, Any]:
        """Get step-by-step progress information"""
        try:
            progress = self.get_or_create_setup_progress(user_id)
            completed_steps = progress.completed_steps or []
            
            step_info = {}
            for i, step in enumerate(self.SETUP_STEPS):
                step_info[step] = {
                    'completed': step in completed_steps,
                    'current': step == progress.current_step,
                    'order': i + 1,
                    'name': self._get_step_display_name(step)
                }
            
            return {
                'steps': step_info,
                'current_step': progress.current_step,
                'completed_count': len(completed_steps),
                'total_steps': len(self.SETUP_STEPS),
                'progress_percentage': (len(completed_steps) / len(self.SETUP_STEPS)) * 100
            }
        except Exception as e:
            self.logger.error(f"Error getting step progress: {e}")
            return {
                'steps': {},
                'current_step': 'welcome',
                'completed_count': 0,
                'total_steps': len(self.SETUP_STEPS),
                'progress_percentage': 0
            }
    
    def _get_step_display_name(self, step: str) -> str:
        """Get human-readable step name"""
        names = {
            'welcome': 'Welcome',
            'languages': 'Languages',
            'neurodivergent': 'Accessibility Needs',
            'mental_health': 'Mental Health Goals',
            'ai_assistant': 'AI Assistant',
            'health_wellness': 'Health & Wellness',
            'theme_accessibility': 'Theme & Accessibility',
            'notifications_privacy': 'Notifications & Privacy',
            'integrations': 'Integrations',
            'emergency_safety': 'Emergency & Safety',
            'features_guide': 'Features Guide',
            'complete': 'Complete'
        }
        return names.get(step, step.title())


# Singleton instance
setup_service = SetupService()