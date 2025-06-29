"""
Google Tasks Helper - Backward Compatibility Module
Provides compatibility layer for legacy google_tasks_helper imports
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Import the unified service
try:
    from .unified_google_services import UnifiedGoogleService
    _unified_service = UnifiedGoogleService()
except ImportError:
    logger.warning("Unified Google Services not available - using fallback")
    _unified_service = None

class GoogleTasksHelper:
    """Google Tasks helper with unified service backend"""
    
    def __init__(self):
        self.service = _unified_service
        
    def authenticate(self) -> bool:
        """Authenticate with Google Tasks API"""
        try:
            if self.service:
                return self.service.authenticate()
            return False
        except Exception as e:
            logger.error(f"Google Tasks authentication failed: {e}")
            return False
    
    def create_task(self, title: str, description: str = "", due_date: str = None) -> Optional[Dict]:
        """Create a new task"""
        try:
            if self.service:
                return self.service.create_task(title, description, due_date)
            return None
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    def get_tasks(self, tasklist_id: str = '@default') -> List[Dict]:
        """Get all tasks from a task list"""
        try:
            if self.service:
                return self.service.get_tasks(tasklist_id)
            return []
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def update_task(self, task_id: str, updates: Dict) -> Optional[Dict]:
        """Update a task"""
        try:
            if self.service:
                return self.service.update_task(task_id, updates)
            return None
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            if self.service:
                return self.service.delete_task(task_id)
            return False
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False
    
    def get_task_lists(self) -> List[Dict]:
        """Get all task lists"""
        try:
            if self.service:
                return self.service.get_task_lists()
            return []
        except Exception as e:
            logger.error(f"Failed to get task lists: {e}")
            return []

# Legacy function imports for backward compatibility
def get_tasks_service():
    """Get Google Tasks service instance"""
    return GoogleTasksHelper()

def create_task(title: str, description: str = "", due_date: str = None) -> Optional[Dict]:
    """Create a task - legacy function"""
    helper = GoogleTasksHelper()
    return helper.create_task(title, description, due_date)

def get_tasks(tasklist_id: str = '@default') -> List[Dict]:
    """Get tasks - legacy function"""
    helper = GoogleTasksHelper()
    return helper.get_tasks(tasklist_id)

def update_task(task_id: str, updates: Dict) -> Optional[Dict]:
    """Update task - legacy function"""
    helper = GoogleTasksHelper()
    return helper.update_task(task_id, updates)

def delete_task(task_id: str) -> bool:
    """Delete task - legacy function"""
    helper = GoogleTasksHelper()
    return helper.delete_task(task_id)

def get_task_lists() -> List[Dict]:
    """Get task lists - legacy function"""
    helper = GoogleTasksHelper()
    return helper.get_task_lists()

# Fallback implementations when Google services are not available
def _create_fallback_task(title: str, description: str = "", due_date: str = None) -> Dict:
    """Fallback task creation"""
    return {
        "id": f"fallback_{hash(title)}",
        "title": title,
        "description": description,
        "due_date": due_date,
        "status": "created",
        "fallback": True
    }

# Export the helper class and functions
__all__ = [
    'GoogleTasksHelper',
    'get_tasks_service',
    'create_task',
    'get_tasks',
    'update_task',
    'delete_task',
    'get_task_lists'
]