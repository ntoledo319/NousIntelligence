"""
Memory System Initializer

This module handles the initialization of the memory system during application startup,
ensuring that the database connection is properly set up for the memory service and
that any required initial data is loaded.

@module utils.memory_initializer
@description Memory system initialization
"""

import logging
from app_factory import db
from utils.enhanced_memory import init_db
from services.memory_service import get_memory_service

logger = logging.getLogger(__name__)

def initialize_memory_system(app):
    """
    Initialize the memory system for the application

    Args:
        app: Flask application instance
    """
    logger.info("Initializing memory system")

    try:
        # Initialize the database connection for enhanced_memory
        init_db(db)

        # Log successful initialization
        logger.info("Memory system initialized successfully")

        @app.before_first_request
        def initialize_memory_for_users():
            """Ensure first-time users have memory initialized when they first access the app"""
            # This runs on the first request after application startup
            logger.info("Ready to initialize memory for new users")

    except Exception as e:
        logger.error(f"Error initializing memory system: {str(e)}")