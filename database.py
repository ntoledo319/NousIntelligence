"""
Database Configuration Module
Provides centralized database configuration and SQLAlchemy instance
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

# Initialize SQLAlchemy with custom base class
db = SQLAlchemy(model_class=Base)

def init_db(app):
    """Initialize database with Flask app"""
    
    # Configure database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nous.db')
    
    # Configure SQLAlchemy settings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Initialize the database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return db