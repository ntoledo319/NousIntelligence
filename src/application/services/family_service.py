from typing import List, Optional, Dict, Any
from src.domain.repositories.family_repository import FamilyRepository
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

class FamilyService:
    def __init__(self, repository: FamilyRepository):
        self.repository = repository
    
    def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all familys for a user"""
        try:
            return self.repository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting familys for user {user_id}: {e}")
            raise
    
    def get_by_id(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get family by ID for a user"""
        try:
            return self.repository.find_by_id_and_user(id, user_id)
        except Exception as e:
            logger.error(f"Error getting family {id} for user {user_id}: {e}")
            raise
    
    def create(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new family"""
        try:
            data['user_id'] = user_id
            # Encrypt sensitive fields if needed
            data = self._encrypt_sensitive_fields(data)
            return self.repository.create(data)
        except Exception as e:
            logger.error(f"Error creating family: {e}")
            raise
    
    def update(self, id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Update family"""
        try:
            data = self._encrypt_sensitive_fields(data)
            return self.repository.update(id, data, user_id)
        except Exception as e:
            logger.error(f"Error updating family {id}: {e}")
            raise
    
    def delete(self, id: str, user_id: str) -> bool:
        """Delete family"""
        try:
            return self.repository.delete(id, user_id)
        except Exception as e:
            logger.error(f"Error deleting family {id}: {e}")
            raise
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields - override in subclasses"""
        return data
