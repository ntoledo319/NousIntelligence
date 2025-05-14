import datetime
import logging
from models import db, Medication, Doctor
from utils.doctor_appointment_helper import get_user_id_from_session, get_doctor_by_name

def get_medications(session):
    """Get all medications for the current user"""
    user_id = get_user_id_from_session(session)
    return Medication.query.filter_by(user_id=user_id).all()

def get_medication_by_id(medication_id, session):
    """Get a specific medication by ID"""
    user_id = get_user_id_from_session(session)
    return Medication.query.filter_by(id=medication_id, user_id=user_id).first()

def get_medication_by_name(name, session):
    """Get a medication by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return Medication.query.filter(
        Medication.name.ilike(f"%{name}%"),
        Medication.user_id == user_id
    ).first()

def add_medication(name, dosage=None, instructions=None, doctor_name=None, 
                   pharmacy=None, quantity=None, refills=None, session=None):
    """Add a new medication to track"""
    try:
        user_id = get_user_id_from_session(session)
        
        # If a doctor name is provided, look up the doctor
        doctor_id = None
        if doctor_name:
            doctor = get_doctor_by_name(doctor_name, session)
            if doctor:
                doctor_id = doctor.id
        
        # Create the medication record
        medication = Medication(
            name=name,
            dosage=dosage,
            instructions=instructions,
            doctor_id=doctor_id,
            pharmacy=pharmacy,
            quantity_remaining=quantity,
            refills_remaining=refills if refills is not None else 0,
            user_id=user_id
        )
        
        db.session.add(medication)
        db.session.commit()
        return medication
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding medication: {str(e)}")
        return None

def update_medication_quantity(medication_id, new_quantity, session):
    """Update the remaining quantity of a medication"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the medication exists and belongs to the user
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        if not medication:
            return None
            
        medication.quantity_remaining = new_quantity
        
        # If quantity is getting low, calculate when it will run out
        if medication.quantity_remaining is not None and medication.quantity_remaining > 0:
            # This is a very simplified calculation - in reality would depend on dosage schedule
            # Assuming 1 dose per day for simplicity
            days_remaining = medication.quantity_remaining
            medication.next_refill_date = datetime.datetime.now() + datetime.timedelta(days=days_remaining)
            
        db.session.commit()
        return medication
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating medication quantity: {str(e)}")
        return None

def refill_medication(medication_id, quantity_added, refills_remaining=None, session=None):
    """Record a medication refill"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the medication exists and belongs to the user
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        if not medication:
            return None
            
        # Update quantities
        if medication.quantity_remaining is not None:
            medication.quantity_remaining += quantity_added
        else:
            medication.quantity_remaining = quantity_added
            
        # Update refills if provided
        if refills_remaining is not None:
            medication.refills_remaining = refills_remaining
            
        # Update refill date and last refilled date
        medication.last_refilled = datetime.datetime.now()
        
        # Calculate next refill date based on quantity and assumed usage (1 per day)
        if medication.quantity_remaining > 0:
            days_remaining = medication.quantity_remaining
            medication.next_refill_date = medication.last_refilled + datetime.timedelta(days=days_remaining)
            
        db.session.commit()
        return medication
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error refilling medication: {str(e)}")
        return None

def get_medications_to_refill(session):
    """Get medications that need to be refilled soon based on threshold and quantity"""
    user_id = get_user_id_from_session(session)
    now = datetime.datetime.now()
    
    # Get medications where:
    # 1. Quantity is below refill threshold, or
    # 2. Next refill date is within the next 7 days
    threshold_date = now + datetime.timedelta(days=7)
    
    return Medication.query.filter(
        Medication.user_id == user_id,
        db.or_(
            Medication.next_refill_date <= threshold_date,
            Medication.quantity_remaining <= Medication.refill_reminder_threshold
        )
    ).all()

def get_medications_by_doctor(doctor_id, session):
    """Get all medications prescribed by a specific doctor"""
    user_id = get_user_id_from_session(session)
    return Medication.query.filter_by(doctor_id=doctor_id, user_id=user_id).all()