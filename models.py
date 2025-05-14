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

# Shopping List and Grocery Features
class ShoppingList(db.Model):
    """Model for shopping/grocery lists"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    store = db.Column(db.String(100))  # Optional store name
    is_recurring = db.Column(db.Boolean, default=False)  # If this is a recurring order list
    frequency_days = db.Column(db.Integer, default=0)  # For recurring orders, every X days
    next_order_date = db.Column(db.DateTime)  # For recurring orders
    last_ordered = db.Column(db.DateTime)  # When this list was last ordered
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with items
    items = db.relationship('ShoppingItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'store': self.store,
            'is_recurring': self.is_recurring,
            'frequency_days': self.frequency_days,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None,
            'items_count': len(self.items) if self.items else 0
        }

class ShoppingItem(db.Model):
    """Model for items in a shopping list"""
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # e.g., Produce, Dairy, etc.
    quantity = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(20))  # e.g., lbs, oz, etc.
    notes = db.Column(db.String(255))
    is_checked = db.Column(db.Boolean, default=False)  # For checked off items
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'is_checked': self.is_checked,
            'priority': self.priority
        }

# Prescription and Medication Management
class Medication(db.Model):
    """Model for tracking medications"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))  # e.g., 10mg
    instructions = db.Column(db.Text)  # e.g., Take twice daily with food
    prescription_number = db.Column(db.String(50))
    pharmacy = db.Column(db.String(100))
    pharmacy_phone = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    quantity_remaining = db.Column(db.Integer)  # Pills/doses remaining
    refills_remaining = db.Column(db.Integer, default=0)
    refill_reminder_threshold = db.Column(db.Integer, default=7)  # Remind when X days of medicine left
    next_refill_date = db.Column(db.DateTime)
    last_refilled = db.Column(db.DateTime)
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dosage': self.dosage,
            'instructions': self.instructions,
            'prescription_number': self.prescription_number,
            'pharmacy': self.pharmacy,
            'doctor_name': Doctor.query.get(self.doctor_id).name if self.doctor_id and Doctor.query.get(self.doctor_id) else None,
            'quantity_remaining': self.quantity_remaining,
            'refills_remaining': self.refills_remaining,
            'next_refill_date': self.next_refill_date.isoformat() if self.next_refill_date else None,
            'days_remaining': (self.next_refill_date - datetime.datetime.now()).days if self.next_refill_date else None
        }

# E-commerce Product Ordering
class Product(db.Model):
    """Model for tracking favorite or recurring products to order"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(255))  # Link to the product
    image_url = db.Column(db.String(255))  # Product image
    price = db.Column(db.Float)  # Last known price
    source = db.Column(db.String(50))  # e.g., Amazon, Target, etc.
    is_recurring = db.Column(db.Boolean, default=False)  # If this is a recurring order
    frequency_days = db.Column(db.Integer, default=0)  # For recurring orders, every X days
    next_order_date = db.Column(db.DateTime)  # For recurring orders
    last_ordered = db.Column(db.DateTime)  # When this product was last ordered
    user_id = db.Column(db.String(255))  # User identifier (from session)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'price': self.price,
            'source': self.source,
            'is_recurring': self.is_recurring,
            'frequency_days': self.frequency_days,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None
        }