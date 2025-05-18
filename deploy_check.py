#!/usr/bin/env python3
"""
NOUS Simplified Deployment Check

This script checks the essential requirements for deploying the NOUS application
without running the full deployment process.
"""

import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

def check_database_connection():
    """Check if database connection works"""
    logger.info("Checking database connection...")
    
    try:
        # Create a minimal app to test database connection
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db = SQLAlchemy(app)
        
        # Test the connection with proper SQL text
        from sqlalchemy import text
        with app.app_context():
            result = db.session.execute(text("SELECT 1")).scalar()
            if result == 1:
                logger.info("✓ Database connection successful")
                return True
            else:
                logger.error("✗ Database connection test failed")
                return False
    except Exception as e:
        logger.error(f"✗ Database connection error: {str(e)}")
        return False

def check_application():
    """Check if the application can be imported"""
    logger.info("Checking application imports...")
    
    try:
        # Try to import the app module
        import app
        logger.info("✓ Application module imported successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Application import error: {str(e)}")
        return False

def main():
    """Run all deployment checks"""
    logger.info("Starting NOUS deployment check...")
    
    env_check = check_environment()
    if not env_check:
        logger.error("Environment check failed")
        return False
    
    db_check = check_database_connection()
    if not db_check:
        logger.error("Database check failed")
        return False
    
    app_check = check_application()
    if not app_check:
        logger.error("Application check failed")
        return False
    
    logger.info("All deployment checks passed successfully!")
    logger.info("The application is ready for deployment.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)