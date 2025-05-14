from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Doctor(db.Model):
    """Model for storing doctor information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with appointments
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes
        }

class Appointment(db.Model):
    """Model for tracking appointment history and upcoming appointments"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(255))  # User identifier (from session)
    
    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat() if self.date else None,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes
        }

class AppointmentReminder(db.Model):
    """Model for storing when to remind users about making appointments"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    frequency_months = db.Column(db.Integer, default=6)  # How often to see this doctor (in months)
    last_appointment = db.Column(db.DateTime)  # Date of the last appointment
    next_reminder = db.Column(db.DateTime)  # When to remind about making the next appointment
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)