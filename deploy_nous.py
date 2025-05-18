#!/usr/bin/env python3
"""
NOUS Unified Deployment Script

This script handles the complete deployment process for the NOUS application.
It combines environment checks, database migrations, and application verification
into a single, reliable deployment flow.

Usage:
  python deploy_nous.py [--dry-run] [--no-migrations] [--ignore-errors] [--debug]

Options:
  --dry-run        Only check what would be done without making changes
  --no-migrations  Skip running database migrations
  --ignore-errors  Continue deployment even if non-critical errors occur
  --debug          Enable verbose debug output

Author: NOUS Development Team
"""

import os
import sys
import time
import logging
import argparse
import traceback
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment.log')
    ]
)
logger = logging.getLogger("deploy")

def check_environment(check_optional: bool = False) -> bool:
    """
    Check if required environment variables are set
    
    Args:
        check_optional: Whether to check optional variables
        
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    logger.info("Checking environment variables...")
    
    required_vars = {
        "DATABASE_URL": "Database connection string",
        "SECRET_KEY": "Secret key for the application",
        "SESSION_SECRET": "Secret key for Flask sessions (alternative to SECRET_KEY)",
    }
    
    optional_vars = {
        "FLASK_ENV": "Flask environment ('development', 'production')",
        "PORT": "Port for the web server",
        "REDIS_URL": "Redis connection string (optional)",
        "GOOGLE_CLIENT_ID": "Google OAuth client ID",
        "GOOGLE_CLIENT_SECRET": "Google OAuth client secret",
        "SPOTIFY_CLIENT_ID": "Spotify API client ID",
        "SPOTIFY_CLIENT_SECRET": "Spotify API client secret",
        "OPENROUTER_API_KEY": "OpenRouter API key"
    }
    
    all_required_present = True
    
    # Check required variables with alternatives
    if os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET"):
        logger.info("✓ Required variable SECRET_KEY/SESSION_SECRET is set")
    else:
        logger.error("✗ Required variable SECRET_KEY or SESSION_SECRET is not set")
        all_required_present = False
        
    # Check other required variables
    for var_name, description in [item for item in required_vars.items() if item[0] != "SECRET_KEY" and item[0] != "SESSION_SECRET"]:
        if os.environ.get(var_name):
            logger.info(f"✓ Required variable {var_name} is set")
        else:
            logger.error(f"✗ Required variable {var_name} is not set ({description})")
            all_required_present = False
    
    # Check optional variables if requested
    if check_optional:
        for var_name, description in optional_vars.items():
            if os.environ.get(var_name):
                logger.info(f"✓ Optional variable {var_name} is set")
            else:
                logger.warning(f"! Optional variable {var_name} is not set ({description})")
    
    return all_required_present

def check_database_connection() -> bool:
    """
    Check if the database can be connected to
    
    Returns:
        bool: True if database connection works, False otherwise
    """
    logger.info("Checking database connection...")
    
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    # Ensure proper SQLAlchemy URI format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Create a minimal engine to test the connection
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            
            if value == 1:
                # Get database details for logging
                db_info = urlparse(database_url)
                host = db_info.hostname
                user = db_info.username
                dbname = db_info.path.strip('/')
                
                logger.info(f"✓ Database connection successful (host={host}, db={dbname}, user={user})")
                return True
            else:
                logger.error("✗ Database connection test returned unexpected value")
                return False
    except Exception as e:
        logger.error(f"✗ Database connection error: {str(e)}")
        return False

def run_migrations(dry_run: bool = False, ignore_errors: bool = False) -> bool:
    """
    Run database migrations
    
    Args:
        dry_run: If True, only print what would be done without executing
        ignore_errors: If True, continue even if non-critical errors occur
        
    Returns:
        bool: True if migrations were successful, False otherwise
    """
    logger.info("Running database migrations...")
    
    try:
        import run_migrations
        
        # Run migrations with appropriate args
        flags = []
        if dry_run:
            flags.append("--dry-run")
        if ignore_errors:
            flags.append("--ignore-errors")
        
        logger.info(f"Running migrations with flags: {flags}")
        
        # Modify sys.argv temporarily to pass our flags
        original_argv = sys.argv
        sys.argv = [sys.argv[0]] + flags
        
        try:
            result = run_migrations.run_migrations(dry_run=dry_run)
            
            if result:
                logger.info("✓ Database migrations completed successfully")
            else:
                logger.error("✗ Database migrations failed")
            
            return result
            
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except ImportError:
        logger.error("✗ Could not import run_migrations.py")
        return False
    except Exception as e:
        logger.error(f"✗ Error running migrations: {str(e)}")
        traceback.print_exc()
        return False

def verify_application() -> bool:
    """
    Verify application components are working properly
    
    Returns:
        bool: True if verification was successful, False otherwise
    """
    logger.info("Verifying application components...")
    
    try:
        # Import the app to test initialization
        from app import app
        
        # Try getting version info
        version = getattr(app, 'version', 'unknown')
        
        # Test basic app properties
        logger.info(f"Application version: {version}")
        logger.info(f"Debug mode: {app.debug}")
        logger.info(f"Secret key is set: {'Yes' if app.secret_key else 'No'}")
        
        # Count registered routes
        route_count = len(list(app.url_map.iter_rules()))
        logger.info(f"Application has {route_count} routes registered")
        
        # Check database connection within app context
        with app.app_context():
            from models import db
            db.session.execute(text("SELECT 1")).scalar()
            logger.info("Database connection verified within app context")
        
        logger.info("✓ Application verification successful")
        return True
        
    except Exception as e:
        logger.error(f"✗ Application verification failed: {str(e)}")
        traceback.print_exc()
        return False

def generate_deployment_report() -> dict:
    """
    Generate a report of the deployment status
    
    Returns:
        dict: Deployment status report
    """
    logger.info("Generating deployment report...")
    
    # Use standard variables from environment where possible
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "database": {
            "connected": False,
            "url_present": bool(os.environ.get("DATABASE_URL"))
        },
        "optional_services": {
            "google_auth": os.environ.get("GOOGLE_CLIENT_ID") is not None,
            "redis_cache": os.environ.get("REDIS_URL") is not None,
            "spotify_api": os.environ.get("SPOTIFY_CLIENT_ID") is not None,
            "openrouter_api": os.environ.get("OPENROUTER_API_KEY") is not None
        }
    }
    
    # Try to get database info
    try:
        if check_database_connection():
            report["database"]["connected"] = True
        
        database_url = os.environ.get("DATABASE_URL", "")
        if database_url:
            parsed = urlparse(database_url)
            report["database"]["host"] = parsed.hostname
            report["database"]["dbname"] = parsed.path.strip('/')
    except Exception:
        pass
    
    # Log report summary
    logger.info(f"Deployment report generated at {report['timestamp']}")
    logger.info(f"Environment: {report['environment']}")
    logger.info(f"Database connected: {report['database']['connected']}")
    logger.info("Optional services:")
    for service, enabled in report["optional_services"].items():
        logger.info(f"  {service}: {'Enabled' if enabled else 'Disabled'}")
    
    return report

def run_deployment(args: argparse.Namespace) -> int:
    """
    Run the deployment process
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    start_time = time.time()
    logger.info("Starting NOUS deployment process...")
    
    # Make logs more verbose in debug mode
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging activated")
    
    # Step 1: Check environment
    if not check_environment(check_optional=True):
        logger.error("Environment check failed. Required environment variables are missing.")
        if args.ignore_errors:
            logger.warning("Continuing despite environment check failure (--ignore-errors)")
        else:
            return 1
    
    # Step 2: Check database
    if not check_database_connection():
        logger.error("Database connection check failed. Cannot proceed with deployment.")
        return 1
    
    # Step 3: Run migrations if not disabled
    if not args.no_migrations:
        if not run_migrations(dry_run=args.dry_run, ignore_errors=args.ignore_errors):
            logger.error("Migrations failed. Fix the issues and try again.")
            if not args.ignore_errors:
                return 1
    else:
        logger.info("Migrations skipped (--no-migrations)")
    
    # If dry run, exit here
    if args.dry_run:
        logger.info("Dry run mode - skipping application verification")
        end_time = time.time()
        logger.info(f"Deployment dry run completed in {(end_time - start_time):.2f} seconds")
        return 0
    
    # Step 4: Verify application
    if not verify_application():
        logger.error("Application verification failed. The deployment may not function correctly.")
        if not args.ignore_errors:
            return 1
    
    # Step 5: Generate deployment report
    report = generate_deployment_report()
    
    # Calculate deployment time
    end_time = time.time()
    deployment_time = end_time - start_time
    logger.info(f"Deployment completed in {deployment_time:.2f} seconds")
    
    logger.info(f"NOUS v{getattr(report, 'version', 'unknown')} has been deployed successfully")
    return 0

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="NOUS Deployment Script")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Only check what would be done without making changes")
    parser.add_argument("--no-migrations", action="store_true",
                        help="Skip running database migrations")
    parser.add_argument("--ignore-errors", action="store_true",
                        help="Continue deployment even if non-critical errors occur")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug output")
    args = parser.parse_args()
    
    try:
        # Run deployment
        exit_code = run_deployment(args)
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception in deployment process: {str(e)}")
        traceback.print_exc()
        sys.exit(2)