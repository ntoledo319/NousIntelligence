"""
Migration to ensure all necessary columns exist in the database

This script checks for required columns and adds them if they're missing.
It's compatible with both the direct app instance and factory pattern.
"""

import os
import logging
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a database connection directly from the DATABASE_URL
    
    This avoids importing the Flask app, making the migration more robust
    """
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return None
    
    # Ensure proper SQLAlchemy URI format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        connection = engine.connect()
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return None

def apply_migration():
    """Add any missing columns to database tables."""
    logger.info("Starting database migration for missing columns")
    
    conn = get_db_connection()
    if not conn:
        logger.error("Could not establish database connection")
        return False
    
    try:
        # Check if is_admin column exists in users table
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_name='users' AND column_name='is_admin'"
        ))
        
        scalar_value = result.scalar()
        has_is_admin = scalar_value is not None and scalar_value > 0
        
        if not has_is_admin:
            logger.info("Adding missing is_admin column to users table")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"
            ))
            conn.commit()
            logger.info("Added is_admin column successfully")
        else:
            logger.info("is_admin column already exists")
        
        # Check if account_active column exists
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_name='users' AND column_name='account_active'"
        ))
        
        scalar_value = result.scalar()
        has_account_active = scalar_value is not None and scalar_value > 0
        
        if not has_account_active:
            logger.info("Adding missing account_active column to users table")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN account_active BOOLEAN DEFAULT TRUE"
            ))
            conn.commit()
            logger.info("Added account_active column successfully")
        else:
            logger.info("account_active column already exists")
        
        # Add color_theme column if it doesn't exist
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_name='user_settings' AND column_name='color_theme'"
        ))
        
        scalar_value = result.scalar()
        has_color_theme = scalar_value is not None and scalar_value > 0
        
        if not has_color_theme:
            logger.info("Adding missing color_theme column to user_settings table")
            conn.execute(text(
                "ALTER TABLE user_settings ADD COLUMN color_theme VARCHAR(20) DEFAULT 'default'"
            ))
            conn.commit()
            logger.info("Added color_theme column successfully")
        else:
            logger.info("color_theme column already exists")
            
        conn.close()
        logger.info("Database migration completed successfully")
        return True
            
    except Exception as e:
        logger.error(f"Error in database migration: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    apply_migrations()