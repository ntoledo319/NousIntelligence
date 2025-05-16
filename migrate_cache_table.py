"""
Cache Table Migration Script

This script creates the cache_entries table in the database if it doesn't already exist.
Run this script after deploying the updated cache_helper.py to ensure proper caching.

@module: migrate_cache_table
@author: NOUS Development Team
"""

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database connection string
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy model for cache_entries table
Base = declarative_base()

class CacheEntry(Base):
    """Model for storing cache entries in the database"""
    __tablename__ = 'cache_entries'
    
    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def apply_migration():
    """Create the cache_entries table if it doesn't exist"""
    if not database_url:
        logger.error("No DATABASE_URL found in environment variables")
        return False
    
    try:
        logger.info(f"Connecting to database: {database_url}")
        engine = create_engine(database_url)
        
        # Check if table already exists
        with engine.connect() as connection:
            result = connection.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cache_entries')"
            ))
            table_exists = result.scalar()
        
        if table_exists:
            logger.info("cache_entries table already exists, skipping creation")
            return True
        
        # Create table
        logger.info("Creating cache_entries table")
        Base.metadata.create_all(engine, tables=[CacheEntry.__table__])
        
        # Create index on expires_at column for faster cleanup
        with engine.connect() as connection:
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_cache_entries_expires_at ON cache_entries(expires_at)"
            ))
            connection.commit()
        
        logger.info("Cache table migration completed successfully")
        return True
    
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting cache table migration")
    if apply_migration():
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed") 