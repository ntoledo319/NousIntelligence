"""
Health API routes.
Handles health-related functionality such as doctors, appointments, medications, etc.

@module health
@context_boundary Health Management
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import logging
import datetime
from models import db, Doctor, Appointment, AppointmentReminder, Medication
from utils.security_helper import rate_limit

# Create blueprint
health_bp = Blueprint('health_api', __name__, url_prefix='/api/health')

# Error handler for the blueprint
@health_bp.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions for this blueprint"""
    logging.error(f"Health API error: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500

# Doctor routes
@health_bp.route('/doctors', methods=['GET'])
@login_required
def get_doctors():
    """Get all doctors for the current user"""
    try:
        user_id = current_user.id
        doctors = Doctor.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'doctors': [doctor.to_dict() for doctor in doctors]
        })
    except Exception as e:
        logging.error(f"Error fetching doctors: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@login_required
def get_doctor(doctor_id):
    """Get a specific doctor by ID"""
    try:
        user_id = current_user.id
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'error': 'Doctor not found'
            }), 404
            
        return jsonify({
            'success': True,
            'doctor': doctor.to_dict()
        })
    except Exception as e:
        logging.error(f"Error fetching doctor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/doctors', methods=['POST'])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def add_doctor():
    """Add a new doctor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Create new doctor
        doctor = Doctor(
            name=data['name'],
            specialty=data.get('specialty', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            notes=data.get('notes', ''),
            user_id=current_user.id
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'doctor': doctor.to_dict(),
            'message': 'Doctor added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding doctor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@login_required
def update_doctor(doctor_id):
    """Update an existing doctor"""
    try:
        user_id = current_user.id
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'error': 'Doctor not found'
            }), 404
            
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Update doctor fields
        if 'name' in data:
            doctor.name = data['name']
        if 'specialty' in data:
            doctor.specialty = data['specialty']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'address' in data:
            doctor.address = data['address']
        if 'notes' in data:
            doctor.notes = data['notes']
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'doctor': doctor.to_dict(),
            'message': 'Doctor updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating doctor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@login_required
def delete_doctor(doctor_id):
    """Delete a doctor"""
    try:
        user_id = current_user.id
        doctor = Doctor.query.filter_by(id=doctor_id, user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'error': 'Doctor not found'
            }), 404
            
        db.session.delete(doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting doctor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Appointment routes
@health_bp.route('/appointments', methods=['GET'])
@login_required
def get_appointments():
    """Get all appointments for the current user"""
    try:
        user_id = current_user.id
        appointments = Appointment.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'appointments': [appointment.to_dict() for appointment in appointments]
        })
    except Exception as e:
        logging.error(f"Error fetching appointments: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/upcoming-appointments', methods=['GET'])
@login_required
def get_upcoming_appointments():
    """Get upcoming appointments"""
    try:
        user_id = current_user.id
        now = datetime.datetime.now()
        
        appointments = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date > now,
            Appointment.status == 'scheduled'
        ).order_by(Appointment.date).all()
        
        return jsonify({
            'success': True,
            'appointments': [appointment.to_dict() for appointment in appointments]
        })
    except Exception as e:
        logging.error(f"Error fetching upcoming appointments: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/appointments', methods=['POST'])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def add_appointment():
    """Add a new appointment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['doctor_id', 'date']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Validate doctor ID
        doctor = Doctor.query.filter_by(id=data['doctor_id'], user_id=current_user.id).first()
        if not doctor:
            return jsonify({
                'success': False,
                'error': 'Doctor not found'
            }), 404
            
        # Parse date
        try:
            date = datetime.datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
            }), 400
            
        # Create new appointment
        appointment = Appointment(
            doctor_id=data['doctor_id'],
            date=date,
            reason=data.get('reason', ''),
            status=data.get('status', 'scheduled'),
            notes=data.get('notes', ''),
            user_id=current_user.id
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'appointment': appointment.to_dict(),
            'message': 'Appointment added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding appointment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Medication routes
@health_bp.route('/medications', methods=['GET'])
@login_required
def get_medications():
    """Get all medications for the current user"""
    try:
        user_id = current_user.id
        medications = Medication.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'medications': [medication.to_dict() for medication in medications]
        })
    except Exception as e:
        logging.error(f"Error fetching medications: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/medications-to-refill', methods=['GET'])
@login_required
def get_medications_to_refill():
    """Get medications that need refill"""
    try:
        user_id = current_user.id
        
        # Get medications where quantity is below threshold
        medications = Medication.query.filter(
            Medication.user_id == user_id,
            Medication.quantity_remaining <= Medication.refill_reminder_threshold
        ).all()
        
        return jsonify({
            'success': True,
            'medications': [medication.to_dict() for medication in medications]
        })
    except Exception as e:
        logging.error(f"Error fetching medications to refill: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/medications', methods=['POST'])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def add_medication():
    """Add a new medication"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Validate doctor ID if provided
        doctor_id = data.get('doctor_id')
        if doctor_id:
            doctor = Doctor.query.filter_by(id=doctor_id, user_id=current_user.id).first()
            if not doctor:
                return jsonify({
                    'success': False,
                    'error': 'Doctor not found'
                }), 404
                
        # Create new medication
        medication = Medication(
            name=data['name'],
            dosage=data.get('dosage', ''),
            instructions=data.get('instructions', ''),
            prescription_number=data.get('prescription_number', ''),
            pharmacy=data.get('pharmacy', ''),
            pharmacy_phone=data.get('pharmacy_phone', ''),
            doctor_id=doctor_id,
            quantity_remaining=data.get('quantity_remaining', 0),
            refills_remaining=data.get('refills_remaining', 0),
            refill_reminder_threshold=data.get('refill_reminder_threshold', 7),
            user_id=current_user.id
        )
        
        # Set dates if provided
        if 'next_refill_date' in data:
            try:
                medication.next_refill_date = datetime.datetime.fromisoformat(
                    data['next_refill_date'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid next_refill_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
                
        if 'last_refilled' in data:
            try:
                medication.last_refilled = datetime.datetime.fromisoformat(
                    data['last_refilled'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid last_refilled format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        db.session.add(medication)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'medication': medication.to_dict(),
            'message': 'Medication added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding medication: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/medications/<int:medication_id>/refill', methods=['PUT'])
@login_required
def refill_medication(medication_id):
    """Refill a medication"""
    try:
        user_id = current_user.id
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        
        if not medication:
            return jsonify({
                'success': False,
                'error': 'Medication not found'
            }), 404
            
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Update medication refill information
        if 'quantity' in data:
            medication.quantity_remaining = data['quantity']
            
        # Decrement refills_remaining if specified
        if data.get('use_refill', False) and medication.refills_remaining > 0:
            medication.refills_remaining -= 1
            
        # Update last refilled date
        medication.last_refilled = datetime.datetime.now()
        
        # Update next refill date if provided
        if 'next_refill_date' in data:
            try:
                medication.next_refill_date = datetime.datetime.fromisoformat(
                    data['next_refill_date'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid next_refill_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
                
        db.session.commit()
        
        return jsonify({
            'success': True,
            'medication': medication.to_dict(),
            'message': 'Medication refilled successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error refilling medication: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 