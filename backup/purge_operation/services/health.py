"""
Health Service Module

This module provides service implementation for health-related operations,
including doctors and appointments.

@module services.health
@author NOUS Development Team
"""

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from models import Doctor, Appointment
from repositories.doctor import DoctorRepository
from repositories.appointment import AppointmentRepository

logger = logging.getLogger(__name__)

class HealthService:
    """Service for health-related operations"""
    
    def __init__(self):
        """Initialize service with repositories"""
        self.doctor_repo = DoctorRepository()
        self.appointment_repo = AppointmentRepository()
    
    # Doctor operations
    
    def get_all_doctors(self, user_id: str) -> List[Doctor]:
        """
        Get all doctors for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of doctors
        """
        return self.doctor_repo.get_by_user_id(user_id)
    
    def get_doctor(self, doctor_id: int) -> Optional[Doctor]:
        """
        Get a doctor by ID.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            Doctor or None if not found
        """
        return self.doctor_repo.get_by_id(doctor_id)
    
    def create_doctor(self, doctor_data: Dict[str, Any], user_id: str) -> Doctor:
        """
        Create a new doctor.
        
        Args:
            doctor_data: Doctor data
            user_id: User ID
            
        Returns:
            Created doctor
        """
        # Add user_id to doctor data
        doctor_data['user_id'] = user_id
        
        # Create the doctor
        return self.doctor_repo.create(**doctor_data)
    
    def update_doctor(self, doctor_id: int, doctor_data: Dict[str, Any], user_id: str) -> Optional[Doctor]:
        """
        Update a doctor.
        
        Args:
            doctor_id: Doctor ID
            doctor_data: Doctor data to update
            user_id: User ID
            
        Returns:
            Updated doctor or None if not found
        """
        doctor = self.doctor_repo.find_one_by(id=doctor_id, user_id=user_id)
        if not doctor:
            return None
        
        return self.doctor_repo.update(doctor, **doctor_data)
    
    def delete_doctor(self, doctor_id: int, user_id: str) -> bool:
        """
        Delete a doctor.
        
        Args:
            doctor_id: Doctor ID
            user_id: User ID
            
        Returns:
            True if successful, False if doctor not found
        """
        doctor = self.doctor_repo.find_one_by(id=doctor_id, user_id=user_id)
        if not doctor:
            return False
        
        return self.doctor_repo.delete(doctor)
    
    # Appointment operations
    
    def get_all_appointments(self, user_id: str) -> List[Appointment]:
        """
        Get all appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of appointments
        """
        return self.appointment_repo.get_by_user_id(user_id)
    
    def get_upcoming_appointments(self, user_id: str) -> List[Appointment]:
        """
        Get upcoming appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of upcoming appointments
        """
        return self.appointment_repo.get_upcoming(user_id)
    
    def get_appointments_by_doctor(self, doctor_id: int, user_id: str) -> List[Appointment]:
        """
        Get appointments for a specific doctor.
        
        Args:
            doctor_id: Doctor ID
            user_id: User ID
            
        Returns:
            List of appointments for the doctor
        """
        return self.appointment_repo.get_by_doctor_id(doctor_id, user_id)
    
    def create_appointment(self, appointment_data: Dict[str, Any], user_id: str) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            appointment_data: Appointment data
            user_id: User ID
            
        Returns:
            Created appointment
            
        Raises:
            ValueError: If doctor_id is invalid or date format is incorrect
        """
        # Validate doctor exists
        doctor_id = appointment_data.get('doctor_id')
        if doctor_id and not self.doctor_repo.find_one_by(id=doctor_id, user_id=user_id):
            raise ValueError(f"Doctor not found with ID: {doctor_id}")
        
        # Add user_id to appointment data
        appointment_data['user_id'] = user_id
        
        # Ensure status is set
        if 'status' not in appointment_data:
            appointment_data['status'] = 'scheduled'
        
        # Create the appointment
        return self.appointment_repo.create(**appointment_data)
    
    def update_appointment_status(self, appointment_id: int, status: str, user_id: str) -> Optional[Appointment]:
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
        return self.appointment_repo.update_status(appointment_id, status, user_id)
    
    def find_doctors_by_specialty(self, specialty: str, user_id: str) -> List[Doctor]:
        """
        Find doctors by specialty.
        
        Args:
            specialty: Medical specialty
            user_id: User ID
            
        Returns:
            List of doctors with the given specialty
        """
        return self.doctor_repo.get_by_specialty(specialty, user_id) 