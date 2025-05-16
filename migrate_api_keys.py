"""
Migration to update the api_keys table schema
to match the User model ID type (string instead of integer)
"""
import os
import logging
from app import app, db
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists():
    """Check if the api_keys table exists in the database."""
    with app.app_context():
        conn = db.engine.connect()
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'api_keys')"
        ))
        exists = result.scalar()
        conn.close()
        return exists

def apply_migration():
    """
    Update the api_keys table schema to use string user_id
    to match the User model's ID type.
    """
    logger.info("Starting api_keys migration")
    
    try:
        # First check if the table exists
        table_exists = check_table_exists()
        
        if not table_exists:
            logger.info("Table api_keys doesn't exist, will be created properly by SQLAlchemy")
            return True
            
        # Table exists, we need to drop it and let SQLAlchemy recreate it with the correct schema
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if there's data in the table
            result = conn.execute(text("SELECT COUNT(*) FROM api_keys"))
            count = result.scalar() or 0  # Use 0 if result is None
            
            if count > 0:
                logger.warning(f"Table api_keys has {count} rows of data that will be lost")
                
            # Drop the table and its constraint
            try:
                conn.execute(text("ALTER TABLE api_keys DROP CONSTRAINT api_keys_user_id_fkey"))
                logger.info("Dropped foreign key constraint")
            except Exception as e:
                logger.warning(f"Could not drop constraint: {str(e)}")
            
            conn.execute(text("DROP TABLE IF EXISTS api_keys"))
            conn.commit()
            logger.info("Dropped table api_keys")
            
            conn.close()
            
            logger.info("Migration completed successfully - table will be recreated on app startup")
            return True
            
    except Exception as e:
        logger.error(f"Error in migration: {str(e)}")
        return False

if __name__ == "__main__":
    apply_migration()