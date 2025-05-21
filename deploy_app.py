#!/usr/bin/env python3
"""
NOUS Deployment Script

This script handles the deployment of the NOUS application by:
1. Verifying environment configuration
2. Checking database connectivity
3. Setting up required directories
4. Running database migrations
5. Starting the application with Gunicorn

Usage:
  python deploy_app.py
"""

import os
import sys
import logging
import shutil
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deploy_app')

def check_environment():
    """Check environment variables and set defaults if needed"""
    logger.info("Checking environment variables...")
    
    # Essential environment variables
    env_vars = {
        'FLASK_APP': 'main.py',
        'PORT': '8080',
        'FLASK_ENV': 'production',
        'AUTO_CREATE_TABLES': 'true',
    }
    
    # Set default environment variables if not already set
    for var, default in env_vars.items():
        if not os.environ.get(var):
            os.environ[var] = default
            logger.info(f"Set default for {var}={default}")
    
    # Check for essential variables that we can't set defaults for
    missing_critical = []
    if not os.environ.get('DATABASE_URL'):
        missing_critical.append('DATABASE_URL')
    
    if not os.environ.get('SECRET_KEY') and not os.environ.get('SESSION_SECRET'):
        # Generate a secure random key
        import secrets
        random_key = secrets.token_hex(32)
        os.environ['SECRET_KEY'] = random_key
        os.environ['SESSION_SECRET'] = random_key
        logger.info("Generated new secure secret key")
        
        # Save key for future use
        with open('.secret_key', 'w') as f:
            f.write(random_key)
        os.chmod('.secret_key', 0o600)  # Set secure permissions
    
    if missing_critical:
        logger.error(f"Missing critical environment variables: {', '.join(missing_critical)}")
        return False
    
    logger.info("Environment check passed")
    return True

def setup_directories():
    """Create and set permissions for required directories"""
    logger.info("Setting up required directories...")
    
    # Create directories
    for directory in ['flask_session', 'uploads', 'logs', 'instance']:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Set permissions (only on systems where this is supported)
    try:
        for directory in ['flask_session', 'uploads', 'logs', 'instance']:
            os.chmod(directory, 0o777)
            logger.info(f"Set permissions for {directory}")
    except Exception as e:
        logger.warning(f"Could not set directory permissions: {str(e)}")
    
    return True

def check_database():
    """Verify database connection and run migrations"""
    logger.info("Checking database connection...")
    
    if not os.environ.get('DATABASE_URL'):
        logger.error("Cannot check database connection - DATABASE_URL not set")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if db_version and db_version[0]:
            logger.info(f"Database connection successful: {db_version[0].split(',')[0]}")
        else:
            logger.info("Database connection successful")
        
        # Run migrations if available
        if os.path.exists('run_migrations.py'):
            logger.info("Running database migrations...")
            try:
                subprocess.run([sys.executable, 'run_migrations.py'], check=True)
                logger.info("Database migrations completed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Database migration failed: {str(e)}")
                return False
        
        return True
    except ImportError:
        logger.error("psycopg2 module not installed - required for database connection")
        return False
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def start_application():
    """Start the application using Gunicorn"""
    logger.info("Starting NOUS application...")
    
    # Check if Gunicorn is available
    try:
        import gunicorn
        logger.info("Gunicorn found, using it to start the application")
    except ImportError:
        logger.error("Gunicorn not installed, cannot start application")
        return False
    
    try:
        # Start with Gunicorn
        port = os.environ.get('PORT', '8080')
        cmd = [
            'gunicorn', 
            '--bind', f'0.0.0.0:{port}', 
            '--workers', '2',
            '--threads', '2',
            '--timeout', '120',
            'main:app'
        ]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        # Use exec-style call to replace current process
        os.execvp(cmd[0], cmd)
        
        # Note: code after this point will not execute due to execvp
        return True
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        return False

def main():
    """Run deployment process"""
    logger.info("Starting NOUS deployment process...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Fix the missing variables and try again.")
        return False
    
    # Setup directories
    if not setup_directories():
        logger.error("Failed to set up required directories.")
        return False
    
    # Check database
    if not check_database():
        logger.warning("Database check had issues. The application may still work with limited functionality.")
        # Continue anyway as the app should handle database errors gracefully
    
    # Start application
    if not start_application():
        logger.error("Failed to start the application.")
        return False
    
    # If we get here (unlikely due to execvp), it's successful
    logger.info("Deployment completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)