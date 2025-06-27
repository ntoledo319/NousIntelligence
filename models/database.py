"""
Database Configuration Module

This module configures the database connection and provides
utility functions for database operations.
"""

# Database setup - imported by app.py  
from flask_sqlalchemy import SQLAlchemy

# This will be initialized in app.py
db = None

def get_db():
    """Get database instance"""
    global db
    return db

def set_db(database_instance):
    """Set database instance"""
    global db
    db = database_instance
import logging

logger = logging.getLogger(__name__)

def init_db(app):
    """Initialize the database with the application context

    Args:
        app: Flask application instance
    """
    with app.app_context():
        # Import all models here to ensure they're registered with SQLAlchemy
        from models.user import User

        # Create tables
        db.create_all()
        logger.info("Database tables created successfully")

def get_db():
    """Get the database instance

    Returns:
        SQLAlchemy database instance
    """
    return db