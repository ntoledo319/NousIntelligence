"""
Deal Models

This module contains deal and product-related database models for the NOUS application.
These models are used for tracking deals, products, and related information.
"""

from datetime import datetime
from app_factory import db

class Product(db.Model):
    """
    Product model for tracking products in the system.

    Attributes:
        id: Unique identifier for the product
        name: Name of the product
        description: Description of the product
        category: Category of the product
        brand: Brand of the product
        image_url: URL to an image of the product
        msrp: Manufacturer's suggested retail price
        user_id: Foreign key to the user who added the product
        created_at: When the product was created
        updated_at: When the product was last updated
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    image_url = db.Column(db.String(1024))
    msrp = db.Column(db.Float)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deals = db.relationship('Deal', backref='product', lazy=True)
    user = db.relationship('User', backref=db.backref('products', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'image_url': self.image_url,
            'msrp': self.msrp,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
    rating = db.Column(db.Integer, default=0)  # 0-5
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('deals', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
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