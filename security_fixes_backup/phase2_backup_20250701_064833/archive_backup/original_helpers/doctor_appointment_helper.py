import datetime
import logging
from models import db, Doctor, Appointment, AppointmentReminder

def get_user_id_from_session(session):
    """Extract a unique user identifier from the session"""
    if 'google_creds' in session and 'client_id' in session['google_creds']:
        return session['google_creds']['client_id']
    elif 'spotify_user' in session:
        return session['spotify_user']
    else:
        # Fallback to session ID if no other identifier is available
        return session.get('_id', 'anonymous')

def get_doctors(session):
    """Get all doctors for the current user"""
    user_id = get_user_id_from_session(session)
    return Doctor.query.filter_by(user_id=user_id).all()

def get_doctor_by_id(doctor_id, session):
    """Get a specific doctor by ID for the current user"""
    user_id = get_user_id_from_session(session)
    return Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()

def get_doctor_by_name(name, session):
    """Get a doctor by name (case-insensitive) for the current user"""
    user_id = get_user_id_from_session(session)
    return Doctor.query.filter(Doctor.name.ilike(f"%{name}%"), Doctor.user_id == user_id).first()

def add_doctor(name, specialty=None, phone=None, address=None, notes=None, session=None):
    """Add a new doctor to the database"""
    try:
        user_id = get_user_id_from_session(session)
        doctor = Doctor(
            name=name,
            specialty=specialty,
            phone=phone,
            address=address,
            notes=notes,
            user_id=user_id
        )

        db.session.add(doctor)
        db.session.commit()
        return doctor
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding doctor: {str(e)}")
        return None

def update_doctor(doctor_id, name=None, specialty=None, phone=None, address=None, notes=None, session=None):
    """Update doctor information"""
    try:
        user_id = get_user_id_from_session(session)
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        if not doctor:
            return None

        if name:
            doctor.name = name
        if specialty is not None:
            doctor.specialty = specialty
        if phone is not None:
            doctor.phone = phone
        if address is not None:
            doctor.address = address
        if notes is not None:
            doctor.notes = notes

        db.session.commit()
        return doctor
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating doctor: {str(e)}")
        return None

def delete_doctor(doctor_id, session):
    """Delete a doctor from the database"""
    try:
        user_id = get_user_id_from_session(session)
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        if not doctor:
            return False

        db.session.delete(doctor)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting doctor: {str(e)}")
        return False

def get_upcoming_appointments(session):
    """Get upcoming appointments for the current user"""
    user_id = get_user_id_from_session(session)
    now = datetime.datetime.now()
    return Appointment.query.filter(
        Appointment.user_id == user_id,
        Appointment.date >= now,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.date).all()

def get_appointments_by_doctor(doctor_id, session):
    """Get all appointments for a specific doctor"""
    user_id = get_user_id_from_session(session)
    return Appointment.query.filter_by(
        doctor_id=doctor_id,
        user_id=user_id
    ).order_by(Appointment.date.desc()).all()

def add_appointment(doctor_id, date, reason=None, status='scheduled', notes=None, session=None):
    """Add a new appointment"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify doctor exists
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        if not doctor:
            return None

        appointment = Appointment(
            doctor_id=doctor_id,
            date=date,
            reason=reason,
            status=status,
            notes=notes,
            user_id=user_id
        )

        db.session.add(appointment)
        db.session.commit()

        # Update appointment reminder if it exists
        reminder = AppointmentReminder.query.filter_by(doctor_id=doctor_id, user_id=user_id).first()
        if reminder:
            reminder.last_appointment = date
            # Calculate next reminder date based on frequency
            reminder.next_reminder = date + datetime.timedelta(days=30*reminder.frequency_months)
            db.session.commit()

        return appointment
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding appointment: {str(e)}")
        return None

def update_appointment_status(appointment_id, new_status, session):
    """Update an appointment's status"""
    try:
        user_id = get_user_id_from_session(session)
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()
        if not appointment:
            return None

        appointment.status = new_status
        db.session.commit()
        return appointment
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating appointment status: {str(e)}")
        return None

def set_appointment_reminder(doctor_id, frequency_months=6, session=None):
    """Set or update a reminder for regular appointments with a doctor"""
    try:
        user_id = get_user_id_from_session(session)

        # Get the most recent appointment with this doctor
        latest_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            user_id=user_id
        ).order_by(Appointment.date.desc()).first()

        last_date = latest_appointment.date if latest_appointment else datetime.datetime.now()
        next_reminder = last_date + datetime.timedelta(days=30*frequency_months)

        # Check if reminder already exists
        reminder = AppointmentReminder.query.filter_by(doctor_id=doctor_id, user_id=user_id).first()

        if reminder:
            reminder.frequency_months = frequency_months
            reminder.last_appointment = last_date
            reminder.next_reminder = next_reminder
        else:
            reminder = AppointmentReminder(
                doctor_id=doctor_id,
                frequency_months=frequency_months,
                last_appointment=last_date,
                next_reminder=next_reminder,
                user_id=user_id
            )
            db.session.add(reminder)

        db.session.commit()
        return reminder
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error setting appointment reminder: {str(e)}")
        return None

def get_due_appointment_reminders(session):
    """Get reminders that are due for scheduling new appointments"""
    user_id = get_user_id_from_session(session)
    now = datetime.datetime.now()

    return AppointmentReminder.query.filter(
        AppointmentReminder.user_id == user_id,
        AppointmentReminder.next_reminder <= now
    ).all()