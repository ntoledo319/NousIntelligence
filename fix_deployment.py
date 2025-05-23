"""
Deployment Troubleshooting Script

This script checks for common deployment issues and 
attempts to fix them automatically.
"""

import os
import sys
import logging
import importlib
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment_fix.log')
    ]
)
logger = logging.getLogger(__name__)

def check_file_exists(filepath):
    """Check if a file exists and log the result"""
    exists = Path(filepath).exists()
    if exists:
        logger.info(f"✅ File exists: {filepath}")
    else:
        logger.warning(f"❌ File missing: {filepath}")
    return exists

def check_directory_exists(dirpath):
    """Check if a directory exists and log the result"""
    dir_path = Path(dirpath)
    exists = dir_path.exists() and dir_path.is_dir()
    if exists:
        logger.info(f"✅ Directory exists: {dirpath}")
    else:
        logger.warning(f"❌ Directory missing: {dirpath}")
    return exists

def check_environment_variables():
    """Check for required environment variables"""
    required_vars = ['DATABASE_URL', 'PORT', 'FLASK_APP', 'FLASK_ENV']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
            logger.warning(f"❌ Missing environment variable: {var}")
        else:
            logger.info(f"✅ Environment variable set: {var}")
    
    return missing_vars

def check_application_structure():
    """Check for critical application files"""
    required_files = [
        'main.py',
        'wsgi.py',
        'app.py',
        'app_factory.py',
        'config.py',
        'public_deploy.sh',
        'public_start.sh'
    ]
    
    required_dirs = [
        'static', 
        'templates', 
        'logs', 
        'flask_session',
        'models',
        'routes'
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    missing_dirs = []
    for directory in required_dirs:
        if not check_directory_exists(directory):
            missing_dirs.append(directory)
    
    return missing_files, missing_dirs

def check_database_connection():
    """Check database connection"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
        
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.error("❌ DATABASE_URL not set")
            return False
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def fix_deployment_issues():
    """Attempt to fix common deployment issues"""
    logger.info("🔍 Checking for deployment issues...")
    
    # Create required directories
    for dir_name in ['static', 'templates', 'logs', 'flask_session', 'instance']:
        os.makedirs(dir_name, exist_ok=True)
    
    # Ensure wsgi.py is correctly importing the app
    wsgi_content = """
import os
from app_factory import create_app

# Create the Flask application with production configuration
app = create_app()

# Configure for production
app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "nous-secure-key-2025")),
    PREFERRED_URL_SCHEME="https"
)

# Add any production-specific setup here
if os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
"""
    with open('wsgi.py', 'w') as f:
        f.write(wsgi_content.lstrip())
    logger.info("✅ Fixed wsgi.py")
    
    # Generate a secret key if it doesn't exist
    if not os.path.exists('.secret_key'):
        import secrets
        with open('.secret_key', 'w') as f:
            f.write(secrets.token_hex(24))
        os.chmod('.secret_key', 0o600)
        logger.info("✅ Generated new secret key")
    
    logger.info("✅ Deployment fixes completed!")
    
    return True

if __name__ == "__main__":
    logger.info("🔧 NOUS Deployment Troubleshooter")
    
    # Check for issues
    missing_vars = check_environment_variables()
    missing_files, missing_dirs = check_application_structure()
    
    if not missing_files and not missing_dirs and not missing_vars:
        check_database_connection()
    else:
        logger.warning("⚠️ Issues detected, attempting fixes...")
        fix_deployment_issues()
        
    logger.info("✅ Troubleshooting completed")