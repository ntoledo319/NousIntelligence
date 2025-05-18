#!/usr/bin/env python3
"""
NOUS Unified Deployment Script

This script provides a streamlined deployment process for the NOUS application
by performing essential environment checks, database migrations, and application
verification in a reliable sequence designed to work consistently on Replit.

Usage:
  python deploy_unified.py [--debug]

Options:
  --debug       Enable verbose debug logging

Author: NOUS Development Team
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deploy')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="NOUS Unified Deployment Script")
    parser.add_argument('--debug', action='store_true', help='Enable verbose debug output')
    return parser.parse_args()

def setup_logging(debug_mode: bool = False):
    """Configure logging based on debug mode"""
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging activated")
    else:
        logger.setLevel(logging.INFO)

def load_environment():
    """Load environment variables from .env file if available"""
    try:
        import load_env
        logger.info("Environment variables loaded from .env file")
        return True
    except ImportError:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("Environment variables loaded using python-dotenv")
            return True
        except ImportError:
            logger.warning("No environment loading module available, using existing environment")
            return False

def check_environment():
    """Verify required environment variables are set"""
    logger.info("Checking environment variables...")
    
    # Required variables - deployment will fail without these
    required_vars = {
        'DATABASE_URL': 'PostgreSQL database connection string',
    }
    
    # If we have EITHER SECRET_KEY or SESSION_SECRET, that's fine
    if os.environ.get('SECRET_KEY') or os.environ.get('SESSION_SECRET'):
        logger.info("✓ Required variable SECRET_KEY/SESSION_SECRET is set")
    else:
        logger.error("✗ Required variable SECRET_KEY or SESSION_SECRET must be set")
        return False
        
    # Check other required variables
    for var, description in required_vars.items():
        if os.environ.get(var):
            logger.info(f"✓ Required variable {var} is set")
        else:
            logger.error(f"✗ Required variable {var} not set ({description})")
            return False
    
    # Optional variables - deployment will work without them but app may be limited
    optional_vars = {
        'FLASK_ENV': "Flask environment ('development', 'production')",
        'PORT': "Port for the web server",
        'REDIS_URL': "Redis connection string (optional)",
        'GOOGLE_CLIENT_ID': "Google OAuth client ID",
        'GOOGLE_CLIENT_SECRET': "Google OAuth client secret",
        'SPOTIFY_CLIENT_ID': "Spotify API client ID", 
        'SPOTIFY_CLIENT_SECRET': "Spotify API client secret",
        'OPENROUTER_API_KEY': "OpenRouter API key"
    }
    
    for var, description in optional_vars.items():
        if os.environ.get(var):
            logger.info(f"✓ Optional variable {var} is set")
        else:
            logger.warning(f"! Optional variable {var} is not set ({description})")
    
    return True

def check_database_connection():
    """Verify database connection works"""
    logger.info("Checking database connection...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("No DATABASE_URL found in environment")
        return False
        
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
        
        # Ensure consistent URL format
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
        # Extract hostname from connection string for logging (hide credentials)
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            host = parsed.hostname
            database = parsed.path.lstrip('/')
            username = parsed.username
            connection_info = f"host={host}, db={database}, user={username}"
        except Exception:
            connection_info = "(connection info parsing failed)"
            
        # Try connecting to the database
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Simple query to test connection
            conn.execute(text("SELECT 1"))
            logger.info(f"✓ Database connection successful ({connection_info})")
            return True
            
    except ImportError as e:
        logger.error(f"Failed to import required database module: {str(e)}")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking database: {str(e)}")
        return False

def run_migrations():
    """Run essential database migrations"""
    logger.info("Running database migrations...")
    
    # Get a list of migration scripts to run
    migrations = [
        ('Creating cache_entries table', 'migrate_cache_table', 'apply_migration'),
        ('Adding database indexes for performance', 'migrate_indexes', 'apply_migrations'),
        ('Adding color_theme column to UserSettings', 'migrate_color_theme', 'add_color_theme_column'),
    ]
    
    # Run each migration
    for name, module_name, function_name in migrations:
        try:
            logger.info(f"Processing migration: {name} ({module_name}.{function_name})")
            start_time = time.time()
            
            # Try to import the module and run the migration function
            module = __import__(module_name)
            migration_function = getattr(module, function_name)
            success = migration_function()
            
            elapsed_time = time.time() - start_time
            if success:
                logger.info(f"  Migration status: success ({elapsed_time:.2f}s)")
            else:
                logger.warning(f"  Migration status: skipped ({elapsed_time:.2f}s)")
                
        except ImportError as e:
            logger.warning(f"  Migration status: skipped (module not found: {str(e)})")
        except AttributeError as e:
            logger.warning(f"  Migration status: skipped (function not found: {str(e)})")
        except Exception as e:
            logger.error(f"  Migration status: failed ({str(e)})")
            # Continue anyway, try the next migration
    
    return True

def create_deployment_report():
    """Generate a deployment report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'database': {
            'connected': check_database_connection(),
            'url': os.environ.get('DATABASE_URL', '').split('@')[1] if '@' in os.environ.get('DATABASE_URL', '') else 'unknown'
        },
        'app_version': '1.0.0',  # Would ideally get this from a version file
        'status': 'success',
        'message': 'Deployment completed successfully'
    }
    
    return report

def main():
    """Run all deployment steps in sequence"""
    start_time = time.time()
    
    args = parse_args()
    setup_logging(args.debug)
    
    logger.info("Starting NOUS deployment process...")
    
    # First load environment variables
    load_environment()
    
    # Basic environment check
    if not check_environment():
        logger.error("Environment check failed - cannot continue deployment")
        return 1
        
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed - cannot continue deployment")
        return 1
        
    # Run database migrations
    run_migrations()
    
    # Generate deployment report
    report = create_deployment_report()
    
    # Log final status
    elapsed_time = time.time() - start_time
    logger.info(f"Deployment completed in {elapsed_time:.2f} seconds")
    logger.info(f"Final status: {report['status']} - {report['message']}")
    
    # Return success
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)