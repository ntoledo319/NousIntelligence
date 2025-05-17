"""
User Repository Module

This module provides repository implementation for user operations.

@module repositories.user
@author NOUS Development Team
"""

from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import User, UserSettings
from repositories.base import Repository

logger = logging.getLogger(__name__)

class UserRepository(Repository[User]):
    """Repository for User model operations"""
    
    def __init__(self):
        """Initialize repository with User model"""
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User or None if not found
        """
        return self.find_one_by(email=email)
    
    def find_administrators(self) -> List[User]:
        """
        Find all users with administrator privileges.
        
        Returns:
            List of administrator users
        """
        return self.find_by(is_admin=True)
    
    def create_with_settings(self, settings_data=None, **user_data) -> User:
        """
        Create a user with default settings.
        
        Args:
            settings_data: Optional settings data
            **user_data: User attributes
            
        Returns:
            Created user with settings
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Create user
            user = self.create(**user_data)
            
            # Create default settings
            from models import ConversationDifficulty
            
            default_settings = {
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
            
            # Override defaults with provided settings
            if settings_data:
                default_settings.update(settings_data)
            
            # Create settings
            settings = UserSettings(user_id=user.id, **default_settings)
            
            from models import db
            db.session.add(settings)
            db.session.commit()
            
            # Refresh user to load settings relationship
            # Need to reload the user to include the settings relationship
            return self.get_by_id(user.id)
            
        except SQLAlchemyError as e:
            from models import db
            db.session.rollback()
            logger.error(f"Error creating user with settings: {str(e)}")
            raise
    
    def update_profile(self, user_id: str, **profile_data) -> Optional[User]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            **profile_data: Profile data to update
            
        Returns:
            Updated user or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        # Only update allowed profile fields
        allowed_fields = [
            'first_name', 'last_name', 'profile_image_url'
        ]
        
        update_data = {
            k: v for k, v in profile_data.items() 
            if k in allowed_fields
        }
        
        return self.update(user, **update_data)
    
    def set_admin_status(self, user_id: str, is_admin: bool) -> Optional[User]:
        """
        Set administrator status for a user.
        
        Args:
            user_id: User ID
            is_admin: Whether the user should be an administrator
            
        Returns:
            Updated user or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        return self.update(user, is_admin=is_admin)
    
    def deactivate(self, user_id: str) -> Optional[User]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        return self.update(user, account_active=False)
    
    def activate(self, user_id: str) -> Optional[User]:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        return self.update(user, account_active=True) 