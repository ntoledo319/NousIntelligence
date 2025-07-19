"""
User Repository Module

This module provides data access layer for user-related operations.
Implements the repository pattern for user entity management.

@ai_prompt For user data operations, use UserRepository methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class UserRepository:
    """
    Repository class for managing user data operations.
    
    Provides CRUD operations for user entities.
    Uses in-memory storage for testing purposes.
    """
    
    def __init__(self):
        """Initialize the repository with empty storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find user data by user ID.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List containing user data if found
        """
        user = self._storage.get(user_id)
        return [user] if user else []
    
    def find_by_id_and_user(self, user_id: str, requesting_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by ID with authorization check.
        
        Args:
            user_id: The ID of the user to find
            requesting_user_id: The ID of the requesting user
            
        Returns:
            User dictionary if found and authorized, None otherwise
        """
        # For simplicity, users can only access their own data
        if user_id == requesting_user_id:
            return self._storage.get(user_id)
        return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user record.
        
        Args:
            data: User data dictionary
            
        Returns:
            Created user with generated ID and timestamps
        """
        user_id = data.get('id', str(uuid.uuid4()))
        user = {
            'id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'active': True,
            **data
        }
        self._storage[user_id] = user
        return user
    
    def update(self, user_id: str, data: Dict[str, Any], requesting_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing user record.
        
        Args:
            user_id: The ID of the user to update
            data: Updated user data
            requesting_user_id: The ID of the requesting user (for authorization)
            
        Returns:
            Updated user if found and authorized, None otherwise
        """
        user = self.find_by_id_and_user(user_id, requesting_user_id)
        if user:
            user.update(data)
            user['updated_at'] = datetime.utcnow().isoformat()
            return user
        return None
    
    def delete(self, user_id: str, requesting_user_id: str) -> bool:
        """
        Delete a user record.
        
        Args:
            user_id: The ID of the user to delete
            requesting_user_id: The ID of the requesting user (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        user = self.find_by_id_and_user(user_id, requesting_user_id)
        if user:
            del self._storage[user_id]
            return True
        return False
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        for user in self._storage.values():
            if user.get('email') == email:
                return user
        return None
