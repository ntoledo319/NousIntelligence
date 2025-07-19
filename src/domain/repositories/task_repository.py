"""
Task Repository Module

This module provides data access layer for task-related operations.
Implements the repository pattern for task entity management.

@ai_prompt For task data operations, use TaskRepository methods
# AI-GENERATED 2025-07-11
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class TaskRepository:
    """
    Repository class for managing task data operations.
    
    Provides CRUD operations for task entities with user-scoped access.
    Uses in-memory storage for testing purposes.
    """
    
    def __init__(self):
        """Initialize the repository with empty storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find all tasks for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of task dictionaries belonging to the user
        """
        return [task for task in self._storage.values() 
                if task.get('user_id') == user_id]
    
    def find_by_id_and_user(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a task by ID and user.
        
        Args:
            task_id: The ID of the task
            user_id: The ID of the user
            
        Returns:
            Task dictionary if found and belongs to user, None otherwise
        """
        task = self._storage.get(task_id)
        if task and task.get('user_id') == user_id:
            return task
        return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task record.
        
        Args:
            data: Task data dictionary
            
        Returns:
            Created task with generated ID and timestamps
        """
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'pending',
            **data
        }
        self._storage[task_id] = task
        return task
    
    def update(self, task_id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing task record.
        
        Args:
            task_id: The ID of the task to update
            data: Updated task data
            user_id: The ID of the user (for authorization)
            
        Returns:
            Updated task if found and authorized, None otherwise
        """
        task = self.find_by_id_and_user(task_id, user_id)
        if task:
            task.update(data)
            task['updated_at'] = datetime.utcnow().isoformat()
            return task
        return None
    
    def delete(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task record.
        
        Args:
            task_id: The ID of the task to delete
            user_id: The ID of the user (for authorization)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        task = self.find_by_id_and_user(task_id, user_id)
        if task:
            del self._storage[task_id]
            return True
        return False
