"""
Doctor Repository Module

This module provides repository implementation for doctor-related operations.

@module repositories.doctor
@author NOUS Development Team
"""

from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import Doctor
from repositories.base import Repository

logger = logging.getLogger(__name__)

class DoctorRepository(Repository[Doctor]):
    """Repository for Doctor model operations"""
    
    def __init__(self):
        """Initialize repository with Doctor model"""
        super().__init__(Doctor)
    
    def get_by_user_id(self, user_id: str) -> List[Doctor]:
        """
        Get all doctors for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of doctors
        """
        return self.find_by(user_id=user_id)
    
    def get_by_name_and_user(self, name: str, user_id: str) -> Optional[Doctor]:
        """
        Get a doctor by name for a specific user.
        
        Args:
            name: Doctor name
            user_id: User ID
            
        Returns:
            Doctor or None if not found
        """
        return self.find_one_by(name=name, user_id=user_id)
    
    def get_by_specialty(self, specialty: str, user_id: str) -> List[Doctor]:
        """
        Get doctors by specialty for a specific user.
        
        Args:
            specialty: Medical specialty
            user_id: User ID
            
        Returns:
            List of doctors with the given specialty
        """
        return Doctor.query.filter(
            Doctor.specialty.ilike(f"%{specialty}%"),
            Doctor.user_id == user_id
        ).all() 