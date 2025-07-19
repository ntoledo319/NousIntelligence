"""
Thought Service Module

This module provides business logic for thought-related operations.
Acts as an interface between the presentation layer and domain repositories.

@ai_prompt For thought operations, use ThoughtService methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
from src.domain.repositories.thought_repository import ThoughtRepository
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)


class ThoughtService:
    """
    Service class for managing thought-related business operations.
    
    Provides CRUD operations and business logic for thought records
    with proper error handling and data validation.
    """
    
    def __init__(self, repository: ThoughtRepository):
        """
        Initialize the thought service.
        
        Args:
            repository: ThoughtRepository instance for data operations
        """
        self.repository = repository
    
    def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all thought records for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of thought record dictionaries
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting thought records for user {user_id}: {e}")
            raise
    
    def get_by_id(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get thought record by ID for a user.
        
        Args:
            id: The ID of the thought record
            user_id: The ID of the user
            
        Returns:
            Thought record dictionary if found, None otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.find_by_id_and_user(id, user_id)
        except Exception as e:
            logger.error(f"Error getting thought record {id} for user {user_id}: {e}")
            raise
    
    def create(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create new thought record.
        
        Args:
            data: Thought record data dictionary
            user_id: The ID of the user
            
        Returns:
            Created thought record dictionary
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            data['user_id'] = user_id
            # Encrypt sensitive fields if needed
            data = self._encrypt_sensitive_fields(data)
            return self.repository.create(data)
        except Exception as e:
            logger.error(f"Error creating thought record: {e}")
            raise
    
    def update(self, id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update thought record.
        
        Args:
            id: The ID of the thought record to update
            data: Updated thought record data
            user_id: The ID of the user
            
        Returns:
            Updated thought record if found, None otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            data = self._encrypt_sensitive_fields(data)
            return self.repository.update(id, data, user_id)
        except Exception as e:
            logger.error(f"Error updating thought record {id}: {e}")
            raise
    
    def delete(self, id: str, user_id: str) -> bool:
        """
        Delete thought record.
        
        Args:
            id: The ID of the thought record to delete
            user_id: The ID of the user
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            Exception: If repository operation fails
        """
        try:
            return self.repository.delete(id, user_id)
        except Exception as e:
            logger.error(f"Error deleting thought record {id}: {e}")
            raise
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in thought record data.
        
        Args:
            data: Thought record data dictionary
            
        Returns:
            Data with encrypted sensitive fields
        """
        # For thought records, content might be considered sensitive
        sensitive_fields = ['content', 'notes', 'thoughts']
        
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = encrypt_field(data[field])
        
        return data
