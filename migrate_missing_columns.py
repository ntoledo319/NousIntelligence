import os
import logging
from app import app, db
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_migrations():
    """Add any missing columns to database tables."""
    logger.info("Starting database migration for missing columns")
    
    try:
        with app.app_context():
            # Check if is_admin column exists in users table
            conn = db.engine.connect()
            
            # Check if is_admin column exists
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='is_admin'"
            ))
            
            has_is_admin = result.scalar() > 0
            
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
            
            has_account_active = result.scalar() > 0
            
            if not has_account_active:
                logger.info("Adding missing account_active column to users table")
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN account_active BOOLEAN DEFAULT TRUE"
                ))
                conn.commit()
                logger.info("Added account_active column successfully")
            else:
                logger.info("account_active column already exists")
                
            conn.close()
            
            logger.info("Database migration completed successfully")
            
    except Exception as e:
        logger.error(f"Error in database migration: {str(e)}")
        raise

if __name__ == "__main__":
    apply_migrations()