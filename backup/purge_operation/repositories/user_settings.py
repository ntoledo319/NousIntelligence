"""
User Settings Repository Module

This module provides repository implementation for user settings operations.

@module repositories.user_settings
@author NOUS Development Team
"""

from typing import Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import UserSettings, ConversationDifficulty
from repositories.base import Repository
from models import db

logger = logging.getLogger(__name__)

class UserSettingsRepository(Repository[UserSettings]):
    """Repository for UserSettings model operations"""
    
    def __init__(self):
        """Initialize repository with UserSettings model"""
        super().__init__(UserSettings)
    
    def get_by_user_id(self, user_id: str) -> Optional[UserSettings]:
        """
        Get settings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            UserSettings or None if not found
        """
        return self.find_one_by(user_id=user_id)
    
    def get_or_create_settings(self, user_id: str) -> UserSettings:
        """
        Get settings for a user or create if not found.
        
        Args:
            user_id: User ID
            
        Returns:
            UserSettings (existing or new)
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        settings = self.get_by_user_id(user_id)
        if settings:
            return settings
            
        # Create default settings
        default_settings = {
            'user_id': user_id,
            'conversation_difficulty': ConversationDifficulty.INTERMEDIATE.value,
            'enable_voice_responses': False,
            'preferred_language': 'en-US',
            'theme': 'light',
            'color_theme': 'default',
            'ai_name': 'NOUS',
            'ai_personality': 'helpful',
            'ai_formality': 'casual',
            'ai_verbosity': 'balanced',
            'ai_enthusiasm': 'moderate',
            'ai_emoji_usage': 'occasional',
            'ai_voice_type': 'neutral'
        }
        
        return self.create(**default_settings)
    
    def update_settings(self, user_id: str, settings_data: Dict[str, Any]) -> Optional[UserSettings]:
        """
        Update settings for a user.
        
        Args:
            user_id: User ID
            settings_data: Dictionary of settings to update
            
        Returns:
            Updated UserSettings or None if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
            ValueError: If invalid values are provided
        """
        # Validate conversation_difficulty if provided
        if 'conversation_difficulty' in settings_data:
            difficulty = settings_data['conversation_difficulty']
            if difficulty not in [e.value for e in ConversationDifficulty]:
                valid_values = [e.value for e in ConversationDifficulty]
                raise ValueError(f"Invalid conversation_difficulty value: {difficulty}. Valid values: {valid_values}")
        
        # Get existing settings or create new ones
        settings = self.get_by_user_id(user_id)
        if not settings:
            # Create with provided settings
            settings_data['user_id'] = user_id
            return self.create(**settings_data)
        
        # Update existing settings
        return self.update(settings, **settings_data)
    
    def reset_to_defaults(self, user_id: str) -> Optional[UserSettings]:
        """
        Reset settings to defaults for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated UserSettings or None if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        settings = self.get_by_user_id(user_id)
        if not settings:
            return None
            
        # Default settings values
        default_values = {
            'conversation_difficulty': ConversationDifficulty.INTERMEDIATE.value,
            'enable_voice_responses': False,
            'preferred_language': 'en-US',
            'theme': 'light',
            'color_theme': 'default',
            'ai_name': 'NOUS',
            'ai_personality': 'helpful',
            'ai_formality': 'casual',
            'ai_verbosity': 'balanced',
            'ai_enthusiasm': 'moderate',
            'ai_emoji_usage': 'occasional',
            'ai_voice_type': 'neutral',
            'ai_backstory': None,
            'medication_reminders': False,
            'pain_tracking': False,
            'mindfulness_features': False,
            'shopping_lists': False,
            'product_tracking': False,
            'budget_reminder_enabled': False,
            'weather_alerts': False,
            'travel_planning': False
        }
        
        return self.update(settings, **default_values) 