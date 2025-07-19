"""
Family Repository Module

This module provides data access layer for family-related operations.
Implements the repository pattern for family entity management.

@ai_prompt For family data operations, use FamilyRepository methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class FamilyRepository:
    """
    Repository class for managing family data operations.
    
    Provides CRUD operations for family entities with user-scoped access.
    Uses in-memory storage for testing purposes.
    """
    
    def __init__(self):
        """Initialize the repository with empty storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find all families for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of family dictionaries belonging to the user
        """
        return [family for family in self._storage.values() 
                if family.get('user_id') == user_id]
    
    def find_by_id_and_user(self, family_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a family by ID and user.
        
        Args:
            family_id: The ID of the family
            user_id: The ID of the user
            
        Returns:
            Family dictionary if found and belongs to user, None otherwise
        """
        family = self._storage.get(family_id)
        if family and family.get('user_id') == user_id:
            return family
        return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new family record.
        
        Args:
            data: Family data dictionary
            
        Returns:
            Created family with generated ID and timestamps
        """
        family_id = str(uuid.uuid4())
        family = {
            'id': family_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            **data
        }
        self._storage[family_id] = family
        return family
    
    def update(self, family_id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing family record.
        
        Args:
            family_id: The ID of the family to update
            data: Updated family data
            user_id: The ID of the user (for authorization)
            
        Returns:
            Updated family if found and authorized, None otherwise
        """
        family = self.find_by_id_and_user(family_id, user_id)
        if family:
            family.update(data)
            family['updated_at'] = datetime.utcnow().isoformat()
            return family
        return None
    
    def delete(self, family_id: str, user_id: str) -> bool:
        """
        Delete a family record.
        
        Args:
            family_id: The ID of the family to delete
            user_id: The ID of the user (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        family = self.find_by_id_and_user(family_id, user_id)
        if family:
            del self._storage[family_id]
            return True
        return False
