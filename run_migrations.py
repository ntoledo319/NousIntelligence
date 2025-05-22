"""
Database Migration Script

This script handles database migrations for the NOUS application.
It creates the necessary tables and applies any needed schema updates.
"""

import logging
from app_factory import create_app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations
    
    This function creates or updates database tables based on the current models.
    """
    logger.info("Starting database migration...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from models.user import User
        
        # Create tables
        db.create_all()
        logger.info("Database migration completed successfully")

if __name__ == "__main__":
    run_migrations()