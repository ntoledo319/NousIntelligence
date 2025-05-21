#!/usr/bin/env python3
"""
NOUS Deployment Recovery Tool

This script helps recover from common deployment errors by performing
diagnostic checks and applying fixes. It can be run manually or integrated
into startup scripts to ensure the application starts reliably.

Usage:
  python deployment_recovery.py [--fix-all]

Options:
  --fix-all    Automatically fix all detected issues without prompting
"""

import os
import sys
import logging
import argparse
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deployment_recovery')

def check_directory_permissions():
    """
    Check and fix permissions for critical directories
    
    Returns:
        tuple: (needs_fixing, message)
    """
    critical_dirs = ['flask_session', 'uploads', 'logs', 'instance']
    needs_fixing = False
    issues = []
    
    for directory in critical_dirs:
        dir_path = Path(directory)
        
        # Check if directory exists
        if not dir_path.exists():
            needs_fixing = True
            issues.append(f"Directory {directory} does not exist")
            continue
            
        # Check if directory is writable
        try:
            test_file = dir_path / '.write_test'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()  # Remove test file
        except (IOError, PermissionError):
            needs_fixing = True
            issues.append(f"Directory {directory} is not writable")
    
    if needs_fixing:
        return True, f"Directory permission issues: {', '.join(issues)}"
    return False, "Directory permissions are correct"

def fix_directory_permissions():
    """
    Fix permissions for critical directories
    
    Returns:
        bool: True if successful
    """
    critical_dirs = ['flask_session', 'uploads', 'logs', 'instance']
    
    for directory in critical_dirs:
        dir_path = Path(directory)
        
        # Create directory if it doesn't exist
        if not dir_path.exists():
            logger.info(f"Creating directory {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set permissions to 777 (readable/writable by all)
        try:
            logger.info(f"Setting permissions for {directory}")
            subprocess.run(['chmod', '-R', '777', directory], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set permissions for {directory}: {e}")
            return False
    
    return True

def check_environment_variables():
    """
    Check if critical environment variables are set
    
    Returns:
        tuple: (needs_fixing, message)
    """
    critical_vars = ['DATABASE_URL']
    important_vars = ['SECRET_KEY', 'SESSION_SECRET', 'FLASK_ENV']
    
    missing_critical = [var for var in critical_vars if not os.environ.get(var)]
    missing_important = [var for var in important_vars if not os.environ.get(var)]
    
    if missing_critical:
        return True, f"Missing critical environment variables: {', '.join(missing_critical)}"
    
    if missing_important and not (os.environ.get('SECRET_KEY') or os.environ.get('SESSION_SECRET')):
        return True, "Neither SECRET_KEY nor SESSION_SECRET is set"
    
    return False, "Critical environment variables are set"

def fix_environment_variables():
    """
    Fix environment variables by loading from .env file or generating defaults
    
    Returns:
        bool: True if successful
    """
    # Check for .env file
    env_path = Path('.env')
    if env_path.exists():
        logger.info("Loading environment variables from .env file")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    # Generate secret key if needed
    if not os.environ.get('SECRET_KEY') and not os.environ.get('SESSION_SECRET'):
        import secrets
        secret_key = secrets.token_hex(24)
        
        logger.info("Generating new secret key")
        os.environ['SECRET_KEY'] = secret_key
        os.environ['SESSION_SECRET'] = secret_key
        
        # Save to .secret_key file
        with open('.secret_key', 'w') as f:
            f.write(secret_key)
        os.chmod('.secret_key', 0o600)
    
    # Set default FLASK_ENV if not set
    if not os.environ.get('FLASK_ENV'):
        logger.info("Setting default FLASK_ENV to production")
        os.environ['FLASK_ENV'] = 'production'
    
    # DATABASE_URL can't be auto-fixed, but we'll log a warning
    if not os.environ.get('DATABASE_URL'):
        logger.error("DATABASE_URL is not set. Application will likely fail to start.")
        return False
    
    return True

def check_database_connection():
    """
    Check if database connection is working
    
    Returns:
        tuple: (needs_fixing, message)
    """
    if not os.environ.get('DATABASE_URL'):
        return True, "DATABASE_URL is not set"
    
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.close()
        return False, "Database connection is working"
    except ImportError:
        return True, "psycopg2 is not installed"
    except Exception as e:
        return True, f"Database connection error: {str(e)}"

def fix_database_connection():
    """
    Attempt to fix database connection issues
    
    Returns:
        bool: True if successful
    """
    if not os.environ.get('DATABASE_URL'):
        logger.error("Cannot fix database connection without DATABASE_URL")
        return False
    
    # Try installing psycopg2 if it's missing
    try:
        import psycopg2
    except ImportError:
        logger.info("Installing psycopg2-binary")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], check=True)
            # Re-import after installation
            import psycopg2
        except subprocess.CalledProcessError:
            logger.error("Failed to install psycopg2-binary")
            return False
    
    # Try connecting to the database with retries
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting database connection (try {attempt}/{max_retries})")
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            conn.close()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.warning(f"Database connection failed: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    logger.error("Could not establish database connection after multiple attempts")
    return False

def check_gunicorn_config():
    """
    Check if gunicorn configuration is valid
    
    Returns:
        tuple: (needs_fixing, message)
    """
    config_path = Path('gunicorn_config.py')
    if not config_path.exists():
        return True, "gunicorn_config.py does not exist"
    
    # Check if config file contains critical settings
    with open(config_path) as f:
        content = f.read()
        
    missing = []
    if 'bind =' not in content:
        missing.append('bind setting')
    if 'workers =' not in content:
        missing.append('workers setting')
    
    if missing:
        return True, f"gunicorn_config.py is missing: {', '.join(missing)}"
    
    return False, "gunicorn configuration is valid"

def fix_gunicorn_config():
    """
    Fix or create gunicorn configuration
    
    Returns:
        bool: True if successful
    """
    config_path = Path('gunicorn_config.py')
    
    # If config doesn't exist, create it
    if not config_path.exists():
        logger.info("Creating gunicorn_config.py")
        
        config_content = """# Gunicorn configuration file
import os

# Server socket settings
port = int(os.environ.get("PORT", 8080))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = 2  # Adjust based on available resources
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'nous-app'

# Server mechanics
daemon = False
raw_env = [
    "FLASK_APP=main.py",
    "FLASK_ENV=production"
]

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'

# Server hooks
def on_starting(server):
    print(f"Starting Gunicorn server on port {port}")
    import os
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return True
    
    # Check if config has missing settings and add them
    with open(config_path) as f:
        content = f.read()
    
    needs_update = False
    if 'bind =' not in content:
        content += "\n# Server socket settings\nport = int(os.environ.get('PORT', 8080))\nbind = f'0.0.0.0:{port}'\n"
        needs_update = True
    
    if 'workers =' not in content:
        content += "\n# Worker processes\nworkers = 2  # Adjust based on available resources\n"
        needs_update = True
    
    if needs_update:
        logger.info("Updating gunicorn_config.py with missing settings")
        with open(config_path, 'w') as f:
            f.write(content)
    
    return True

def run_checks_and_fixes(auto_fix=False):
    """
    Run all checks and apply fixes if needed
    
    Args:
        auto_fix: Automatically fix issues without prompting
        
    Returns:
        bool: True if all checks pass or were fixed successfully
    """
    checks = [
        (check_directory_permissions, fix_directory_permissions, "directory permissions"),
        (check_environment_variables, fix_environment_variables, "environment variables"),
        (check_database_connection, fix_database_connection, "database connection"),
        (check_gunicorn_config, fix_gunicorn_config, "Gunicorn configuration")
    ]
    
    all_fixed = True
    
    for check_func, fix_func, description in checks:
        needs_fixing, message = check_func()
        if needs_fixing:
            logger.warning(f"Issue detected with {description}: {message}")
            
            if auto_fix or input(f"Fix {description}? (y/n): ").lower() == 'y':
                logger.info(f"Attempting to fix {description}...")
                if fix_func():
                    logger.info(f"Successfully fixed {description}")
                    # Re-check to confirm fix worked
                    still_needs_fixing, new_message = check_func()
                    if still_needs_fixing:
                        logger.error(f"Fix didn't resolve the issue: {new_message}")
                        all_fixed = False
                else:
                    logger.error(f"Failed to fix {description}")
                    all_fixed = False
            else:
                logger.info(f"Skipping fix for {description}")
                all_fixed = False
        else:
            logger.info(f"Check passed: {message}")
    
    return all_fixed

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="NOUS Deployment Recovery Tool")
    parser.add_argument('--fix-all', action='store_true', 
                        help='Automatically fix all detected issues without prompting')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    logger.info("Starting deployment recovery checks")
    success = run_checks_and_fixes(auto_fix=args.fix_all)
    
    if success:
        logger.info("All checks passed or issues were fixed successfully")
        sys.exit(0)
    else:
        logger.warning("Some issues could not be resolved")
        sys.exit(1)