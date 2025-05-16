#!/usr/bin/env python3
"""
NOUS Deployment Script

This script manages the deployment process for the NOUS application.
It checks environment variables, runs database migrations, and validates the configuration.

Usage:
  python deploy.py [--no-migrations] [--check-only]

@module: deploy
@author: NOUS Development Team
"""

import os
import sys
import time
import logging
import subprocess
import argparse
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Required environment variables
REQUIRED_ENV_VARS = [
    {
        "name": "DATABASE_URL",
        "description": "PostgreSQL database connection string",
        "example": "postgresql://username:password@localhost:5432/nousdb",
        "required": True
    },
    {
        "name": "FLASK_SECRET",
        "description": "Secret key for Flask sessions",
        "example": "generate-a-secure-random-secret",
        "required": True
    },
    {
        "name": "GOOGLE_CLIENT_ID",
        "description": "Google OAuth client ID",
        "example": "your-google-client-id.apps.googleusercontent.com",
        "required": False
    },
    {
        "name": "GOOGLE_CLIENT_SECRET",
        "description": "Google OAuth client secret",
        "example": "your-google-client-secret",
        "required": False
    },
    {
        "name": "REDIS_URL",
        "description": "Redis connection string for caching",
        "example": "redis://localhost:6379/0",
        "required": False
    }
]

def check_environment() -> bool:
    """
    Check if all required environment variables are set
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    logger.info("Checking environment variables...")
    
    all_required_present = True
    missing_required = []
    
    for var in REQUIRED_ENV_VARS:
        name = var["name"]
        required = var.get("required", False)
        value = os.environ.get(name)
        
        if value:
            logger.info(f"✓ {name} is set")
        else:
            if required:
                logger.error(f"✗ Required variable {name} is not set")
                missing_required.append(name)
                all_required_present = False
            else:
                logger.warning(f"⚠ Optional variable {name} is not set")
    
    if not all_required_present:
        logger.error("Missing required environment variables:")
        for name in missing_required:
            var_info = next(var for var in REQUIRED_ENV_VARS if var["name"] == name)
            logger.error(f"  {name}: {var_info['description']}")
            logger.error(f"  Example: {var_info['example']}")
    
    return all_required_present

def generate_secret_key() -> str:
    """
    Generate a secure random secret key
    
    Returns:
        str: A random secret key
    """
    import secrets
    return secrets.token_hex(32)

def run_migrations() -> bool:
    """
    Run database migrations
    
    Returns:
        bool: True if migrations were successful, False otherwise
    """
    logger.info("Running database migrations...")
    
    try:
        # Check if the migration script exists
        if not os.path.exists("run_migrations.py"):
            logger.error("Migration script not found: run_migrations.py")
            return False
        
        # Run migrations
        result = subprocess.run([sys.executable, "run_migrations.py"], 
                               capture_output=True, text=True)
        
        # Log output
        for line in result.stdout.splitlines():
            logger.info(f"  {line}")
        
        for line in result.stderr.splitlines():
            logger.error(f"  {line}")
        
        if result.returncode != 0:
            logger.error(f"Migrations failed with exit code {result.returncode}")
            return False
        
        logger.info("Database migrations completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False

def validate_api_keys() -> bool:
    """
    Validate API keys
    
    Returns:
        bool: True if all API keys are valid, False otherwise
    """
    logger.info("Validating API keys...")
    
    try:
        # Check if the key validation script exists
        if not os.path.exists("utils/key_config.py"):
            logger.error("Key validation module not found: utils/key_config.py")
            return False
        
        # Run key validation
        from utils.key_config import validate_keys
        keys_valid = validate_keys()
        
        # Check result
        if not keys_valid:
            logger.warning("No valid API keys found")
            return False
        
        # Check if at least one AI service is available
        ai_services = []
        if keys_valid.get("huggingface", False):
            ai_services.append("Hugging Face")
        if keys_valid.get("openrouter", False):
            ai_services.append("OpenRouter")
        if keys_valid.get("openai", False):
            ai_services.append("OpenAI")
        
        if ai_services:
            logger.info(f"Available AI services: {', '.join(ai_services)}")
            return True
        else:
            logger.warning("No AI services are available")
            return False
    
    except Exception as e:
        logger.error(f"Error validating API keys: {str(e)}")
        return False

def check_for_updates() -> bool:
    """
    Check for application updates
    
    Returns:
        bool: True if updates were found, False otherwise
    """
    logger.info("Checking for updates...")
    
    try:
        # If in a git repository, check for updates
        result = subprocess.run(["git", "status"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            # Try to fetch updates
            fetch_result = subprocess.run(["git", "fetch"], 
                                        capture_output=True, text=True)
            
            if fetch_result.returncode == 0:
                # Check if we're behind the remote
                status_result = subprocess.run(
                    ["git", "status", "-uno"], 
                    capture_output=True, text=True
                )
                
                if "Your branch is behind" in status_result.stdout:
                    logger.info("Updates are available. Run 'git pull' to update.")
                    return True
                else:
                    logger.info("No updates available.")
                    return False
            else:
                logger.warning("Unable to fetch updates")
                return False
        else:
            logger.info("Not in a git repository, skipping update check")
            return False
    
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        return False

def create_deployment_report() -> Dict:
    """
    Create a deployment report
    
    Returns:
        dict: A report of the deployment status
    """
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "checks": {
            "environment_variables": check_environment(),
            "api_keys": validate_api_keys()
        },
        "updates_available": check_for_updates()
    }
    
    return report

def run_deployment(args: argparse.Namespace) -> int:
    """
    Run the deployment process
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    logger.info("Starting NOUS deployment process...")
    
    # Check environment variables
    if not check_environment():
        if not args.ignore_env:
            logger.error("Environment check failed. Use --ignore-env to continue anyway.")
            return 1
        else:
            logger.warning("Continuing despite environment check failure")
    
    # Run migrations if not disabled
    if not args.no_migrations:
        if not run_migrations():
            logger.error("Migrations failed. Fix the issues and try again.")
            return 1
    else:
        logger.info("Migrations skipped due to --no-migrations flag")
    
    # Just check only if requested
    if args.check_only:
        logger.info("Check-only mode, not performing full deployment")
        return 0
    
    # Create deployment report
    report = create_deployment_report()
    
    # Print summary
    logger.info("Deployment Summary:")
    logger.info(f"  Environment: {report['environment']}")
    logger.info(f"  Environment Variables Check: {'✓' if report['checks']['environment_variables'] else '✗'}")
    logger.info(f"  API Keys Check: {'✓' if report['checks']['api_keys'] else '⚠'}")
    logger.info(f"  Updates Available: {'Yes' if report['updates_available'] else 'No'}")
    
    # Print next steps
    logger.info("")
    logger.info("Next Steps:")
    
    if report["environment"] == "production":
        logger.info("  1. Restart the application using your process manager")
        logger.info("     Example: sudo systemctl restart nous")
    else:
        logger.info("  1. Start the application:")
        logger.info("     python main.py")
    
    logger.info("  2. Access the application at your configured URL")
    logger.info("  3. Monitor the logs for any errors")
    
    return 0

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="NOUS Deployment Script")
    parser.add_argument("--no-migrations", action="store_true", 
                        help="Skip running database migrations")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check the environment, don't run full deployment")
    parser.add_argument("--ignore-env", action="store_true",
                        help="Continue even if environment variables are missing")
    args = parser.parse_args()
    
    # Run deployment
    sys.exit(run_deployment(args)) 