"""
Database Models

This module defines the database models for the application.
It contains SQLAlchemy model classes for users, settings, and other core entities.
Optimized for better performance with model mixins and efficient querying.

@module models
@description SQLAlchemy database models
@context_boundary Database Layer
"""

import uuid
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Union
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, and_, or_
from app_factory import db

logger = logging.getLogger(__name__)

# Type variable for generic model operations
T = TypeVar('T')

# Create model helper functions instead of using a mixin
# This avoids potential issues with class attribute access

def get_by_id(model_class, id):
    """
    Get a database object by ID with query timing
    
    Args:
        model_class: SQLAlchemy model class
        id: Object ID
        
    Returns:
        Model instance or None if not found
    """
    start_time = time.time()
    result = model_class.query.get(id)
    query_time = time.time() - start_time
    
    # Log slow queries for optimization
    if query_time > 0.1:  # Log queries taking more than 100ms
        logger.warning(f"Slow query in {model_class.__name__}.get_by_id(): {query_time:.3f}s")
        
    return result

def get_all(model_class):
    """
    Get all objects with query timing
    
    Args:
        model_class: SQLAlchemy model class
        
    Returns:
        List of model instances
    """
    start_time = time.time()
    result = model_class.query.all()
    query_time = time.time() - start_time
    
    # Log slow queries for optimization
    if query_time > 0.2:  # Log queries taking more than 200ms
        logger.warning(f"Slow query in {model_class.__name__}.get_all(): {query_time:.3f}s")
        
    return result

def create_object(model_class, **kwargs):
    """
    Create a new database object
    
    Args:
        model_class: SQLAlchemy model class
        **kwargs: Object attributes
        
    Returns:
        Created model instance
    """
    obj = model_class(**kwargs)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_object(obj, **kwargs):
    """
    Update a database object
    
    Args:
        obj: Model instance
        **kwargs: Attributes to update
        
    Returns:
        Updated model instance
    """
    for key, value in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, value)
    db.session.commit()
    return obj

def delete_object(obj):
    """
    Delete a database object
    
    Args:
        obj: Model instance
    """
    db.session.delete(obj)
    db.session.commit()

def model_to_dict(obj):
    """
    Convert a model instance to a dictionary
    
    Args:
        obj: Model instance
        
    Returns:
        Dictionary with model attributes
    """
    if not hasattr(obj, '__table__'):
        return {}
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

class User(UserMixin, db.Model):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Unique identifier for the user (UUID)
        email: User's email address
        first_name: User's first name
        last_name: User's last name
        password_hash: Hashed password for authentication
        profile_image_url: URL to user's profile image
        created_at: Timestamp when the user was created
        last_login: Timestamp of the user's last login
        account_active: Whether the user's account is active
        is_admin: Whether the user is an administrator
        email_verified: Whether the user's email is verified
        two_factor_enabled: Whether two-factor authentication is enabled
        two_factor_secret: Secret for two-factor authentication
    """
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    account_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Two-factor authentication fields
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    # Relationships
    settings = db.relationship('UserSettings', backref=db.backref('user_account', lazy=True), lazy=True, uselist=False)
    # Renamed backref to avoid conflicts
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Set password hash from plain text password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash"""
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image_url': self.profile_image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def is_administrator(self):
        """Check if user is an administrator"""
        return self.is_admin

class UserSettings(db.Model):
    """
    User settings model to store user preferences.
    
    Attributes:
        id: Unique identifier for the settings
        user_id: Foreign key to the user
        theme: UI theme preference
        ai_name: Custom name for the AI assistant
        ai_personality: Preferred AI assistant personality
        preferred_language: Preferred language for the interface
        enable_voice_responses: Whether to enable voice responses
        conversation_difficulty: Level of conversation difficulty
    """
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    theme = db.Column(db.String(20), default='light')
    ai_name = db.Column(db.String(64), default='NOUS')
    ai_personality = db.Column(db.String(20), default='helpful')
    preferred_language = db.Column(db.String(10), default='en')
    enable_voice_responses = db.Column(db.Boolean, default=True)
    conversation_difficulty = db.Column(db.String(20), default='normal')
    
    def __repr__(self):
        return f'<UserSettings for user {self.user_id}>'
    
    def to_dict(self):
        """Convert settings to dictionary"""
        return {
            'theme': self.theme,
            'ai_name': self.ai_name,
            'ai_personality': self.ai_personality,
            'preferred_language': self.preferred_language,
            'enable_voice_responses': self.enable_voice_responses,
            'conversation_difficulty': self.conversation_difficulty
        }

class Task(db.Model):
    """
    Task model for task management functionality.
    
    Attributes:
        id: Unique identifier for the task
        user_id: Foreign key to the user who owns the task
        title: Task title
        description: Task description
        due_date: When the task is due
        priority: Task priority level
        completed: Whether the task is completed
        created_at: When the task was created
        updated_at: When the task was last updated
    """
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BetaTester(db.Model):
    """
    Beta tester model for managing beta testing program participants.
    
    Attributes:
        id: Unique identifier for the beta tester record
        user_id: Foreign key to the user who is participating as a beta tester
        access_code: Code used to register as a beta tester
        active: Whether the beta tester account is active
        notes: Additional notes or feedback from the beta tester
        created_at: When the beta tester record was created
    """
    __tablename__ = 'beta_testers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    access_code = db.Column(db.String(32))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('beta_tester', lazy=True))
    
    def __repr__(self):
        return f'<BetaTester for user {self.user_id}>'
    
    def to_dict(self):
        """Convert beta tester record to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSettings(db.Model):
    """
    System settings model for storing application-wide configuration.
    
    Attributes:
        id: Unique identifier for the system setting
        key: Setting key name
        value: Setting value as string (will be converted to appropriate type)
        description: Description of what the setting does
        created_at: When the setting was created
        updated_at: When the setting was last updated
    """
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'
    
    def to_dict(self):
        """Convert setting to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ShoppingList(db.Model):
    """
    Shopping list model to store lists of shopping items.
    
    Attributes:
        id: Unique identifier for the shopping list
        name: Name of the shopping list
        description: Description of the shopping list
        store: Specific store this list is for
        is_recurring: Whether this is a recurring purchase list
        frequency_days: Frequency in days for recurring lists
        last_ordered: Date when items on this list were last ordered
        next_order_date: Date when items on this list should be ordered next
        user_id: Foreign key to the user who owns this list
        created_at: When the list was created
        updated_at: When the list was last updated
    """
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    store = db.Column(db.String(100))
    is_recurring = db.Column(db.Boolean, default=False)
    frequency_days = db.Column(db.Integer, default=0)
    last_ordered = db.Column(db.DateTime)
    next_order_date = db.Column(db.DateTime)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('shopping_lists', lazy=True))
    items = db.relationship('ShoppingItem', backref='shopping_list', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ShoppingList {self.name}>'
    
    def to_dict(self):
        """Convert shopping list to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'store': self.store,
            'is_recurring': self.is_recurring,
            'frequency_days': self.frequency_days,
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'item_count': 0,  # Will be populated by the service layer
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ShoppingItem(db.Model):
    """
    Shopping item model for items in shopping lists.
    
    Attributes:
        id: Unique identifier for the shopping item
        name: Name of the item
        category: Category of the item (e.g., produce, dairy, etc.)
        quantity: Quantity of the item
        unit: Unit of measure (e.g., oz, lb, etc.)
        is_checked: Whether the item has been checked off
        notes: Additional notes about the item
        estimated_price: Estimated price of the item
        shopping_list_id: Foreign key to the shopping list this item belongs to
        created_at: When the item was created
    """
    __tablename__ = 'shopping_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(20))
    is_checked = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    estimated_price = db.Column(db.Float)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShoppingItem {self.name}>'
    
    def to_dict(self):
        """Convert shopping item to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'is_checked': self.is_checked,
            'notes': self.notes,
            'estimated_price': self.estimated_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    """
    Product model for tracking products from various sources.
    
    Attributes:
        id: Unique identifier for the product
        name: Product name
        description: Product description
        url: URL to the product page
        image_url: URL to the product image
        price: Current price of the product
        source: Source of the product (e.g., Amazon, Walmart)
        is_recurring: Whether this is a recurring purchase
        frequency_days: Frequency in days for recurring purchases
        last_ordered: Date when this product was last ordered
        next_order_date: Date when this product should be ordered next
        user_id: Foreign key to the user who is tracking this product
        created_at: When the product tracking was created
        updated_at: When the product tracking was last updated
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(1024))
    image_url = db.Column(db.String(1024))
    price = db.Column(db.Float)
    source = db.Column(db.String(50))  # Amazon, Walmart, etc.
    is_recurring = db.Column(db.Boolean, default=False)
    frequency_days = db.Column(db.Integer, default=0)
    last_ordered = db.Column(db.DateTime)
    next_order_date = db.Column(db.DateTime)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('products', lazy=True))
    price_history = db.relationship('PriceHistory', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """Convert product to dictionary"""
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
            'last_ordered': self.last_ordered.isoformat() if self.last_ordered else None,
            'next_order_date': self.next_order_date.isoformat() if self.next_order_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PriceHistory(db.Model):
    """
    Price history model for tracking price changes over time.
    
    Attributes:
        id: Unique identifier for the price history record
        product_id: Foreign key to the product
        price: Recorded price at this point in time
        date_recorded: When this price was recorded
        source: Source of the price data (e.g., Amazon, Walmart, manual entry)
        is_deal: Whether this price represents a special deal
        created_at: When the price history record was created
    """
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50))  # Amazon, Walmart, manual entry, etc.
    is_deal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceHistory ${self.price} for product_id {self.product_id}>'
    
    def to_dict(self):
        """Convert price history to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'price': self.price,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None,
            'source': self.source,
            'is_deal': self.is_deal,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PriceAlert(db.Model):
    """
    Price alert model for notifications when a product's price drops below a threshold.
    
    Attributes:
        id: Unique identifier for the price alert
        product_id: Foreign key to the product
        user_id: Foreign key to the user who created the alert
        target_price: Price threshold that triggers the alert
        percentage_drop: Alternative percentage drop that triggers the alert
        is_active: Whether the alert is active
        last_triggered: When the alert was last triggered
        notification_method: How to notify the user (email, app, etc.)
        created_at: When the price alert was created
    """
    __tablename__ = 'price_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_price = db.Column(db.Float)
    percentage_drop = db.Column(db.Float)  # e.g., 20.0 for 20% drop
    is_active = db.Column(db.Boolean, default=True)
    last_triggered = db.Column(db.DateTime)
    notification_method = db.Column(db.String(20), default='app')  # app, email, sms
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product')
    user = db.relationship('User', backref=db.backref('price_alerts', lazy=True))
    
    def __repr__(self):
        return f'<PriceAlert for product_id {self.product_id}>'
    
    def to_dict(self):
        """Convert price alert to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'target_price': self.target_price,
            'percentage_drop': self.percentage_drop,
            'is_active': self.is_active,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'notification_method': self.notification_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Deal(db.Model):
    """
    Deal model for tracking special deals and promotions.
    
    Attributes:
        id: Unique identifier for the deal
        product_id: Foreign key to the product (optional, can be a general deal)
        name: Name/title of the deal
        description: Description of the deal
        url: URL to the deal page
        source: Source of the deal (e.g., Amazon, Walmart)
        original_price: Original price before the deal
        deal_price: Price with the deal applied
        discount_percentage: Percentage discount
        start_date: When the deal starts
        end_date: When the deal ends
        user_id: Foreign key to the user who added the deal
        rating: User-assigned rating of the deal (1-5)
        is_verified: Whether the deal has been verified
        created_at: When the deal was created
    """
    __tablename__ = 'deals'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(1024))
    source = db.Column(db.String(50))
    original_price = db.Column(db.Float)
    deal_price = db.Column(db.Float)
    discount_percentage = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer)  # 1-5 rating
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('deals', lazy=True))
    user = db.relationship('User', backref=db.backref('deals', lazy=True))
    
    def __repr__(self):
        return f'<Deal {self.name}>'
    
    def to_dict(self):
        """Convert deal to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'original_price': self.original_price,
            'deal_price': self.deal_price,
            'discount_percentage': self.discount_percentage,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'user_id': self.user_id,
            'rating': self.rating,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Medication(db.Model):
    """
    Medication model for tracking user medications.
    
    Attributes:
        id: Unique identifier for the medication
        name: Medication name
        dosage: Medication dosage (e.g., 10mg)
        frequency: How often the medication is taken (e.g., twice daily)
        remaining_quantity: Current quantity remaining
        refill_threshold: Quantity at which to refill
        refill_amount: Standard amount to refill
        pharmacy: Preferred pharmacy for refills
        notes: Additional notes or instructions
        next_refill_date: Next estimated refill date
        user_id: Foreign key to the user who takes this medication
        created_at: When the medication tracking was created
        updated_at: When the medication tracking was last updated
    """
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(100))
    remaining_quantity = db.Column(db.Float, default=0)
    refill_threshold = db.Column(db.Float, default=5)
    refill_amount = db.Column(db.Float, default=30)
    pharmacy = db.Column(db.String(100))
    needs_prescription = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    next_refill_date = db.Column(db.DateTime)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('medications', lazy=True))
    
    def __repr__(self):
        return f'<Medication {self.name} {self.dosage}>'
    
    def to_dict(self):
        """Convert medication to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'remaining_quantity': self.remaining_quantity,
            'refill_threshold': self.refill_threshold,
            'refill_amount': self.refill_amount,
            'pharmacy': self.pharmacy,
            'needs_prescription': self.needs_prescription,
            'notes': self.notes,
            'next_refill_date': self.next_refill_date.isoformat() if self.next_refill_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# AA Recovery Models
class AASettings(db.Model):
    """User settings for AA recovery features"""
    __tablename__ = 'aa_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    sponsor_name = db.Column(db.String(100))
    sponsor_phone = db.Column(db.String(20))
    backup_contact_name = db.Column(db.String(100))
    backup_contact_phone = db.Column(db.String(20))
    home_group = db.Column(db.String(100))
    sober_date = db.Column(db.DateTime)
    show_sober_days = db.Column(db.Boolean, default=True)
    track_honesty_streaks = db.Column(db.Boolean, default=True)
    track_pain_flares = db.Column(db.Boolean, default=False)
    daily_reflection_time = db.Column(db.String(5), default="07:00")
    nightly_inventory_time = db.Column(db.String(5), default="21:00")
    spot_checks_per_day = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_settings', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sponsor_name': self.sponsor_name,
            'sponsor_phone': self.sponsor_phone,
            'backup_contact_name': self.backup_contact_name,
            'backup_contact_phone': self.backup_contact_phone,
            'home_group': self.home_group,
            'sober_date': self.sober_date.isoformat() if self.sober_date else None,
            'show_sober_days': self.show_sober_days,
            'track_honesty_streaks': self.track_honesty_streaks,
            'track_pain_flares': self.track_pain_flares,
            'daily_reflection_time': self.daily_reflection_time,
            'nightly_inventory_time': self.nightly_inventory_time,
            'spot_checks_per_day': self.spot_checks_per_day,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AARecoveryLog(db.Model):
    """Log of recovery activities and entries"""
    __tablename__ = 'aa_recovery_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    log_type = db.Column(db.String(50))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    is_honest_admit = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_recovery_logs', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'log_type': self.log_type,
            'content': self.content,
            'category': self.category,
            'is_honest_admit': self.is_honest_admit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMeetingLog(db.Model):
    """Log of AA meetings attended"""
    __tablename__ = 'aa_meeting_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    meeting_name = db.Column(db.String(100))
    meeting_type = db.Column(db.String(50))
    meeting_id = db.Column(db.String(100))
    date_attended = db.Column(db.DateTime)
    pre_meeting_reflection = db.Column(db.Text)
    post_meeting_reflection = db.Column(db.Text)
    post_meeting_honest_admit = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_meeting_logs', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meeting_name': self.meeting_name,
            'meeting_type': self.meeting_type,
            'meeting_id': self.meeting_id,
            'date_attended': self.date_attended.isoformat() if self.date_attended else None,
            'pre_meeting_reflection': self.pre_meeting_reflection,
            'post_meeting_reflection': self.post_meeting_reflection,
            'post_meeting_honest_admit': self.post_meeting_honest_admit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AANightlyInventory(db.Model):
    """Nightly 10th Step inventory entries"""
    __tablename__ = 'aa_nightly_inventories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    resentful = db.Column(db.Text)
    selfish = db.Column(db.Text)
    dishonest = db.Column(db.Text)
    afraid = db.Column(db.Text)
    secrets = db.Column(db.Text)
    apologies_needed = db.Column(db.Text)
    gratitude = db.Column(db.Text)
    surrender = db.Column(db.Text)
    wrong_actions = db.Column(db.Text)
    amends_owed = db.Column(db.Text)
    help_plan = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_nightly_inventories', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'resentful': self.resentful,
            'selfish': self.selfish,
            'dishonest': self.dishonest,
            'afraid': self.afraid,
            'secrets': self.secrets,
            'apologies_needed': self.apologies_needed,
            'gratitude': self.gratitude,
            'surrender': self.surrender,
            'wrong_actions': self.wrong_actions,
            'amends_owed': self.amends_owed,
            'help_plan': self.help_plan,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AASpotCheck(db.Model):
    """Spot-check inventory responses"""
    __tablename__ = 'aa_spot_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    check_type = db.Column(db.String(50))
    question = db.Column(db.Text)
    response = db.Column(db.Text)
    rating = db.Column(db.Integer)
    trigger = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_spot_checks', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'check_type': self.check_type,
            'question': self.question,
            'response': self.response,
            'rating': self.rating,
            'trigger': self.trigger,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AASponsorCall(db.Model):
    """Log of calls to sponsor or backup contact"""
    __tablename__ = 'aa_sponsor_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    contact_type = db.Column(db.String(50))
    pre_call_admission = db.Column(db.Text)
    post_call_admission = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_sponsor_calls', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_type': self.contact_type,
            'pre_call_admission': self.pre_call_admission,
            'post_call_admission': self.post_call_admission,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMindfulnessLog(db.Model):
    """Log of mindfulness exercises completed"""
    __tablename__ = 'aa_mindfulness_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    exercise_type = db.Column(db.String(50))
    exercise_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_mindfulness_logs', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'exercise_name': self.exercise_name,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAAchievement(db.Model):
    """Achievement badges for AA recovery progress"""
    __tablename__ = 'aa_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.String(50))
    badge_name = db.Column(db.String(100))
    badge_description = db.Column(db.Text)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('aa_achievements', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None
        }

# DBT Models
class DBTSkillLog(db.Model):
    """Log of DBT skills used"""
    __tablename__ = 'dbt_skill_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    situation = db.Column(db.Text)
    effectiveness = db.Column(db.Integer)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_logs', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'situation': self.situation,
            'effectiveness': self.effectiveness,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class DBTDiaryCard(db.Model):
    """DBT diary card entries"""
    __tablename__ = 'dbt_diary_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    mood_rating = db.Column(db.Integer)
    triggers = db.Column(db.Text)
    urges = db.Column(db.Text)
    skills_used = db.Column(db.Text)
    reflection = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_diary_cards', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'mood_rating': self.mood_rating,
            'triggers': self.triggers,
            'urges': self.urges,
            'skills_used': self.skills_used,
            'reflection': self.reflection,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillCategory(db.Model):
    """Categories for DBT skills"""
    __tablename__ = 'dbt_skill_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class DBTSkillRecommendation(db.Model):
    """Recommended DBT skills for specific situations"""
    __tablename__ = 'dbt_skill_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    situation_type = db.Column(db.String(100))
    skill_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    effectiveness_score = db.Column(db.Float, default=0.0)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_recommendations', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'situation_type': self.situation_type,
            'skill_name': self.skill_name,
            'description': self.description,
            'effectiveness_score': self.effectiveness_score,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillChallenge(db.Model):
    """DBT skill practice challenges"""
    __tablename__ = 'dbt_skill_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.Integer, default=1)
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_challenges', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTCrisisResource(db.Model):
    """Crisis resources for DBT users"""
    __tablename__ = 'dbt_crisis_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100))
    contact_info = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_crisis_resources', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'contact_info': self.contact_info,
            'resource_type': self.resource_type,
            'notes': self.notes,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTEmotionTrack(db.Model):
    """Emotion tracking for DBT users"""
    __tablename__ = 'dbt_emotion_tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    emotion_name = db.Column(db.String(50))
    intensity = db.Column(db.Integer)
    trigger = db.Column(db.Text)
    response = db.Column(db.Text)
    skill_used = db.Column(db.String(100))
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_emotion_tracks', lazy=True))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_name': self.emotion_name,
            'intensity': self.intensity,
            'trigger': self.trigger,
            'response': self.response,
            'skill_used': self.skill_used,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }