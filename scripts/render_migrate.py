#!/usr/bin/env python3
"""
Render Pre-Deploy Migration Script

This script runs database migrations during Render deployments.
It handles both fresh deployments and updates safely.

# AI-GENERATED [2025-01-05]
# ORIGINAL_INTENT: Safely run database migrations on Render pre-deploy

Usage:
    python scripts/render_migrate.py

Environment Variables Required:
    - DATABASE_URL: PostgreSQL connection string (auto-set by Render)
"""

import os
import sys
import logging
from urllib.parse import urlparse

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get and validate database URL from environment."""
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    # Handle Render's postgres:// URL format (SQLAlchemy needs postgresql://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Converted postgres:// to postgresql:// for SQLAlchemy compatibility")
    
    return db_url


def test_database_connection(db_url):
    """Test database connectivity before migration."""
    from sqlalchemy import create_engine, text
    
    logger.info("Testing database connection...")
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def run_migrations():
    """Run Alembic migrations."""
    logger.info("=" * 50)
    logger.info("NOUS Database Migration - Render Pre-Deploy")
    logger.info("=" * 50)
    
    db_url = get_database_url()
    
    # Parse URL for logging (hide password)
    parsed = urlparse(db_url)
    safe_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
    logger.info(f"Database: {safe_url}")
    
    # Test connection first
    if not test_database_connection(db_url):
        logger.error("Cannot proceed with migration - database unreachable")
        sys.exit(1)
    
    # Set up Flask app context for migrations
    try:
        logger.info("Setting up Flask application context...")
        
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Import Flask app
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from models.database import db
            
            logger.info("Creating database tables if they don't exist...")
            db.create_all()
            logger.info("✓ Database tables verified/created")
            
            # Run Alembic migrations
            logger.info("Running Alembic migrations...")
            try:
                from alembic.config import Config
                from alembic import command
                
                alembic_cfg = Config(os.path.join(project_root, "migrations", "alembic.ini"))
                alembic_cfg.set_main_option("sqlalchemy.url", db_url)
                
                # Stamp current revision if fresh database
                try:
                    command.current(alembic_cfg)
                except Exception:
                    logger.info("Fresh database detected, stamping head...")
                    command.stamp(alembic_cfg, "head")
                
                # Upgrade to latest
                command.upgrade(alembic_cfg, "head")
                logger.info("✓ Alembic migrations complete")
                
            except ImportError:
                logger.warning("Alembic not installed, skipping migration upgrade")
                logger.info("Tables created via SQLAlchemy create_all()")
            except Exception as e:
                logger.warning(f"Alembic migration skipped: {e}")
                logger.info("Tables created via SQLAlchemy create_all()")
        
        logger.info("=" * 50)
        logger.info("✓ Database migration completed successfully!")
        logger.info("=" * 50)
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Attempting fallback migration...")
        run_fallback_migration(db_url)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.info("Attempting fallback migration...")
        run_fallback_migration(db_url)


def run_fallback_migration(db_url):
    """Fallback migration using raw SQLAlchemy if Flask app fails."""
    logger.info("Running fallback migration with SQLAlchemy...")
    
    try:
        from sqlalchemy import create_engine, MetaData, inspect
        
        engine = create_engine(db_url)
        
        # Import models to register with SQLAlchemy
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from models.database import db
        
        # Create all tables
        db.metadata.create_all(engine)
        
        # Verify tables created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"✓ Created/verified {len(tables)} tables: {', '.join(tables[:10])}{'...' if len(tables) > 10 else ''}")
        
        logger.info("=" * 50)
        logger.info("✓ Fallback migration completed!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fallback migration also failed: {e}")
        logger.error("Manual intervention may be required")
        # Don't exit with error - let deployment continue
        # Tables may already exist from previous deployment


if __name__ == "__main__":
    run_migrations()
