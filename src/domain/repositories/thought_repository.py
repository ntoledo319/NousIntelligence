"""
Thought Repository Module

This module provides data access layer for thought-related operations.
Implements the repository pattern for thought entity management.

@ai_prompt For thought data operations, use ThoughtRepository methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class ThoughtRepository:
    """
    Repository class for managing thought data operations.
    
    Provides CRUD operations for thought entities with user-scoped access.
    Uses in-memory storage for testing purposes.
    """
    
    def __init__(self):
        """Initialize the repository with empty storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find all thought records for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of thought dictionaries belonging to the user
        """
        return [thought for thought in self._storage.values() 
                if thought.get('user_id') == user_id]
    
    def find_by_id_and_user(self, thought_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a thought record by ID and user.
        
        Args:
            thought_id: The ID of the thought record
            user_id: The ID of the user
            
        Returns:
            Thought dictionary if found and belongs to user, None otherwise
        """
        thought = self._storage.get(thought_id)
        if thought and thought.get('user_id') == user_id:
            return thought
        return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new thought record.
        
        Args:
            data: Thought record data dictionary
            
        Returns:
            Created thought record with generated ID and timestamps
        """
        thought_id = str(uuid.uuid4())
        thought = {
            'id': thought_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'category': data.get('category', 'general'),
            **data
        }
        self._storage[thought_id] = thought
        return thought
    
    def update(self, thought_id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing thought record.
        
        Args:
            thought_id: The ID of the thought record to update
            data: Updated thought record data
            user_id: The ID of the user (for authorization)
            
        Returns:
            Updated thought record if found and authorized, None otherwise
        """
        thought = self.find_by_id_and_user(thought_id, user_id)
        if thought:
            thought.update(data)
            thought['updated_at'] = datetime.utcnow().isoformat()
            return thought
        return None
    
    def delete(self, thought_id: str, user_id: str) -> bool:
        """
        Delete a thought record.
        
        Args:
            thought_id: The ID of the thought record to delete
            user_id: The ID of the user (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        thought = self.find_by_id_and_user(thought_id, user_id)
        if thought:
            del self._storage[thought_id]
            return True
        return False
