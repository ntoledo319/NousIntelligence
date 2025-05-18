#!/usr/bin/env python3
"""
NOUS Simplified Deployment Script

This script performs a streamlined deployment process for the NOUS application,
focusing on the essential verification steps without the complex migration process
that was causing timeouts.
"""

import os
import sys
import logging
import importlib
from datetime import datetime
from sqlalchemy import text
from app import app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    logger.info("Checking environment variables...")
    
    required_vars = {
        "DATABASE_URL": "Database connection string",
        "FLASK_SECRET": "Secret key for Flask sessions"
    }
    
    all_present = True
    
    for var_name, description in required_vars.items():
        if os.environ.get(var_name):
            logger.info(f"✓ {var_name} is set")
        else:
            logger.error(f"✗ Required variable {var_name} is not set")
            all_present = False
    
    return all_present

def apply_database_migrations():
    """Apply essential database migrations directly"""
    logger.info("Applying essential database migrations...")
    
    try:
        with app.app_context():
            # Check if cache_entries table exists
            conn = db.engine.connect()
            
            logger.info("Checking cache_entries table...")
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name='cache_entries'"
            ))
            
            has_cache_table = result.scalar() > 0
            
            if not has_cache_table:
                logger.info("Creating cache_entries table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key VARCHAR(255) PRIMARY KEY,
                        value TEXT NOT NULL,
                        expires_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                logger.info("Cache table created successfully")
            else:
                logger.info("Cache table already exists")
            
            # Verify column exists in users table
            logger.info("Checking users table columns...")
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='is_admin'"
            ))
            
            has_is_admin = result.scalar() > 0
            
            if not has_is_admin:
                logger.info("Adding is_admin column to users table...")
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
                logger.info("Adding account_active column to users table...")
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN account_active BOOLEAN DEFAULT TRUE"
                ))
                conn.commit()
                logger.info("Added account_active column successfully")
            else:
                logger.info("account_active column already exists")
            
            conn.close()
            
        logger.info("Database schema has been updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error applying database migrations: {str(e)}")
        return False

def verify_application():
    """Verify application components are working properly"""
    logger.info("Verifying application components...")
    
    try:
        with app.app_context():
            # Check database connection
            db.session.execute(text("SELECT 1")).scalar()
            logger.info("Database connection verified")
            
            # Check application routes are registered
            route_count = len(list(app.url_map.iter_rules()))
            logger.info(f"Application has {route_count} routes registered")
            
            return True
    except Exception as e:
        logger.error(f"Application verification failed: {str(e)}")
        return False

def generate_deployment_report():
    """Generate deployment report"""
    logger.info("Generating deployment report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "database_url": os.environ.get("DATABASE_URL", "").split("@")[-1] if os.environ.get("DATABASE_URL") else "Not set",
        "optional_services": {
            "google_auth": os.environ.get("GOOGLE_CLIENT_ID") is not None,
            "redis_cache": os.environ.get("REDIS_URL") is not None,
        }
    }
    
    logger.info(f"Deployment report: {report}")
    return report

def main():
    """Run deployment process"""
    logger.info("Starting simplified NOUS deployment process...")
    
    # Check environment variables
    if not check_environment():
        logger.error("Environment check failed. Fix the missing variables and try again.")
        return False
    
    # Apply database migrations
    if not apply_database_migrations():
        logger.error("Database migration failed. Check the logs for details.")
        return False
    
    # Verify application
    if not verify_application():
        logger.error("Application verification failed. Check the logs for details.")
        return False
    
    # Generate deployment report
    generate_deployment_report()
    
    logger.info("Deployment process completed successfully!")
    logger.info("The NOUS application is ready to run.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)