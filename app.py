"""
NOUS Application Instance

This module provides a singleton Flask application instance for use by scripts
that need to access the Flask app outside of the main application run context.
It uses the application factory pattern to ensure consistency.

Note: This approach maintains backward compatibility with scripts that
import directly from app while using the more flexible factory pattern.
"""

import os
import logging
from app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the application instance using the factory
app = create_app()

# Make sure to import models after app is created to avoid circular imports
with app.app_context():
    from models import db
    
    # This is redundant with app_factory but kept for backward compatibility
    try:
        db.create_all()
        logger.info("Database tables created (if they didn't exist already)")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")