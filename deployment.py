"""
NOUS Personal Assistant - Deployment Helper

This script configures the application for deployment and runs it.
It's designed to work with the Replit deploy button.
"""
import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def setup_deployment():
    """Configure the environment for deployment"""
    logger.info("Setting up NOUS Personal Assistant for deployment")
    
    # Set environment variables for deployment
    os.environ["PORT"] = "8080"
    os.environ["PUBLIC_ACCESS"] = "true"
    
    # Create required directories if they don't exist
    dirs = ['static', 'templates', 'logs', 'flask_session', 'instance']
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    # Set appropriate file permissions
    logger.info("Setting appropriate file permissions")
    try:
        subprocess.run(["chmod", "+x", "run_nous.py"], check=True)
        logger.info("Permissions set successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting permissions: {e}")
    
    # Check for required files
    required_files = ['app_public_final.py', 'run_nous.py']
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"Missing required file: {file}")
            return False
    
    logger.info("Deployment setup completed successfully")
    return True

def run_application():
    """Run the NOUS application"""
    logger.info("Starting NOUS Personal Assistant")
    
    try:
        # Run the application using the run_nous.py script
        logger.info("Executing run_nous.py")
        import run_nous
        
        # Special deployment message
        logger.info("NOUS Personal Assistant is being deployed")
        logger.info("Public access is enabled (no Replit login required)")
        logger.info("Google authentication is maintained for protected routes")
        
        # Start the application using the main function
        run_nous.main()
        
    except Exception as e:
        logger.error(f"Error running application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Setup the deployment
    if setup_deployment():
        # Run the application
        run_application()
    else:
        logger.error("Failed to set up deployment")
        sys.exit(1)