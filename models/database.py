"""
Database Configuration Module

This module configures the database connection and provides
utility functions for database operations.
"""

from app import db
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