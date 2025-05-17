"""
Settings Service Module

This module provides service implementation for user settings operations.
The service layer coordinates operations and combines repository calls
with business logic.

@module services.settings
@author NOUS Development Team
"""

from typing import Optional, Dict, Any, Union
import logging
from flask import session

from models import UserSettings, ConversationDifficulty, User
from repositories.user_settings import UserSettingsRepository
from utils.adaptive_conversation import set_difficulty

logger = logging.getLogger(__name__)

class SettingsService:
    """Service for user settings operations"""
    
    def __init__(self):
        """Initialize service with repositories"""
        self.settings_repo = UserSettingsRepository()
    
    def get_settings(self, user_id: str) -> Optional[UserSettings]:
        """
        Get settings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            UserSettings or None if not found
        """
        return self.settings_repo.get_by_user_id(user_id)
    
    def get_or_create_settings(self, user_id: str) -> UserSettings:
        """
        Get settings for a user or create if not found.
        
        Args:
            user_id: User ID
            
        Returns:
            UserSettings (existing or new)
        """
        return self.settings_repo.get_or_create_settings(user_id)
    
    def update_settings(self, user_id: str, settings_data: Dict[str, Any]) -> Optional[UserSettings]:
        """
        Update settings for a user.
        
        Args:
            user_id: User ID
            settings_data: Dictionary of settings to update
            
        Returns:
            Updated UserSettings or None if not found
            
        Raises:
            ValueError: If invalid values are provided
        """
        # Handle conversation difficulty update separately to update adaptive system
        if 'conversation_difficulty' in settings_data:
            try:
                # Update the adaptive conversation system
                set_difficulty(settings_data['conversation_difficulty'])
            except Exception as e:
                logger.error(f"Error updating adaptive conversation difficulty: {str(e)}")
        
        # Update settings in database
        return self.settings_repo.update_settings(user_id, settings_data)
    
    def reset_to_defaults(self, user_id: str) -> Optional[UserSettings]:
        """
        Reset settings to defaults for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated UserSettings or None if not found
        """
        # Reset settings in database
        settings = self.settings_repo.reset_to_defaults(user_id)
        
        # Reset the adaptive conversation system
        if settings:
            try:
                set_difficulty(ConversationDifficulty.INTERMEDIATE.value)
            except Exception as e:
                logger.error(f"Error resetting adaptive conversation difficulty: {str(e)}")
                
        return settings
    
    def get_session_settings(self) -> Dict[str, Any]:
        """
        Get settings from the current session.
        
        Returns:
            Dictionary with session settings
        """
        return {
            'conversation_difficulty': session.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value),
            'enable_voice_responses': session.get('enable_voice_responses', False),
            'preferred_language': session.get('preferred_language', 'en-US'),
            'theme': session.get('theme', 'light'),
            'color_theme': session.get('color_theme', 'default')
        }
    
    def update_session_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update settings in the current session.
        
        Args:
            settings_data: Dictionary of settings to update
            
        Returns:
            Updated session settings
        """
        # Handle conversation difficulty update separately to update adaptive system
        if 'conversation_difficulty' in settings_data:
            try:
                # Update the adaptive conversation system
                set_difficulty(settings_data['conversation_difficulty'])
            except Exception as e:
                logger.error(f"Error updating adaptive conversation difficulty: {str(e)}")
        
        # Update session settings
        for key, value in settings_data.items():
            session[key] = value
            
        # Make sure changes are saved
        session.modified = True
        
        return self.get_session_settings()
    
    def get_settings_for_user_or_session(self, user: Optional[User]) -> Dict[str, Any]:
        """
        Get settings for a user or from session if not authenticated.
        
        Args:
            user: User object or None if not authenticated
            
        Returns:
            Dictionary with settings
        """
        if user and user.is_authenticated:
            # Get settings from database
            settings = self.get_or_create_settings(user.id)
            return settings.to_dict()
        else:
            # Get settings from session
            return self.get_session_settings()
    
    def update_settings_for_user_or_session(self, user: Optional[User], settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update settings for a user or in session if not authenticated.
        
        Args:
            user: User object or None if not authenticated
            settings_data: Dictionary of settings to update
            
        Returns:
            Dictionary with updated settings
        """
        if user and user.is_authenticated:
            # Update settings in database
            settings = self.update_settings(user.id, settings_data)
            return settings.to_dict()
        else:
            # Update settings in session
            return self.update_session_settings(settings_data) 