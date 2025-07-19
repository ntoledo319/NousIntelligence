"""
Mood Service Module

This module provides business logic for mood-related operations.
Acts as an interface between the presentation layer and domain repositories.

@ai_prompt For mood operations, use MoodService methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
from src.domain.repositories.mood_repository import MoodRepository
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)


class MoodService:
    """
    Service class for managing mood-related business operations.
    
    Provides CRUD operations and business logic for mood entries
    with proper error handling and data validation.
    """
    
    def __init__(self, repository: MoodRepository):
        """
        Initialize the mood service.
        
        Args:
            repository: MoodRepository instance for data operations
        """
        self.repository = repository
    
    def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all mood entries for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of mood entry dictionaries
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting mood entries for user {user_id}: {e}")
            raise
    
    def get_by_id(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get mood entry by ID for a user.
        
        Args:
            id: The ID of the mood entry
            user_id: The ID of the user
            
        Returns:
            Mood entry dictionary if found, None otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.find_by_id_and_user(id, user_id)
        except Exception as e:
            logger.error(f"Error getting mood entry {id} for user {user_id}: {e}")
            raise
    
    def create(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create new mood entry.
        
        Args:
            data: Mood entry data dictionary
            user_id: The ID of the user
            
        Returns:
            Created mood entry dictionary
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            data['user_id'] = user_id
            # Encrypt sensitive fields if needed
            data = self._encrypt_sensitive_fields(data)
            return self.repository.create(data)
        except Exception as e:
            logger.error(f"Error creating mood entry: {e}")
            raise
    
    def update(self, id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update mood entry.
        
        Args:
            id: The ID of the mood entry to update
            data: Updated mood entry data
            user_id: The ID of the user
            
        Returns:
            Updated mood entry if found, None otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            data = self._encrypt_sensitive_fields(data)
            return self.repository.update(id, data, user_id)
        except Exception as e:
            logger.error(f"Error updating mood entry {id}: {e}")
            raise
    
    def delete(self, id: str, user_id: str) -> bool:
        """
        Delete mood entry.
        
        Args:
            id: The ID of the mood entry to delete
            user_id: The ID of the user
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.delete(id, user_id)
        except Exception as e:
            logger.error(f"Error deleting mood entry {id}: {e}")
            raise
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in mood entry data.
        
        Args:
            data: Mood entry data dictionary
            
        Returns:
            Data with encrypted sensitive fields
        """
        # For mood entries, notes might be considered sensitive
        if 'notes' in data and data['notes']:
            data['notes'] = encrypt_field(data['notes'])
        
        return data
