"""
Appointment Repository Module

This module provides repository implementation for appointment-related operations.

@module repositories.appointment
@author NOUS Development Team
"""

from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from models import Appointment, db
from repositories.base import Repository

logger = logging.getLogger(__name__)

class AppointmentRepository(Repository[Appointment]):
    """Repository for Appointment model operations"""
    
    def __init__(self):
        """Initialize repository with Appointment model"""
        super().__init__(Appointment)
    
    def get_by_user_id(self, user_id: str) -> List[Appointment]:
        """
        Get all appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of appointments
        """
        return self.find_by(user_id=user_id)
    
    def get_by_doctor_id(self, doctor_id: int, user_id: str) -> List[Appointment]:
        """
        Get appointments for a specific doctor.
        
        Args:
            doctor_id: Doctor ID
            user_id: User ID
            
        Returns:
            List of appointments for the given doctor
        """
        return self.find_by(doctor_id=doctor_id, user_id=user_id)
    
    def get_upcoming(self, user_id: str) -> List[Appointment]:
        """
        Get upcoming appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of upcoming appointments
        """
        return Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date >= datetime.now(),
            Appointment.status == 'scheduled'
        ).order_by(Appointment.date).all()
    
    def get_past(self, user_id: str) -> List[Appointment]:
        """
        Get past appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of past appointments
        """
        return Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date < datetime.now()
        ).order_by(Appointment.date.desc()).all()
    
    def update_status(self, appointment_id: int, status: str, user_id: str) -> Optional[Appointment]:
        """
        Update the status of an appointment.
        
        Args:
            appointment_id: Appointment ID
            status: New status ('scheduled', 'completed', 'cancelled')
            user_id: User ID
            
        Returns:
            Updated appointment or None if not found
            
        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['scheduled', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid values: {valid_statuses}")
        
        appointment = self.find_one_by(id=appointment_id, user_id=user_id)
        if not appointment:
            return None
        
        return self.update(appointment, status=status) 