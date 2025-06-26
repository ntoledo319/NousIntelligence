"""
NOUS Personal Assistant - Health Check Script

This script monitors the application and restarts it if necessary.
It helps ensure high availability in deployment environments.
"""

import os
import time
import logging
import subprocess
import requests
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f"logs/health_check_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_check")

# Configuration
APP_URL = "http://localhost:8080/health"  # Health check endpoint
CHECK_INTERVAL = 60  # Check every 60 seconds
MAX_RETRIES = 3      # Number of retries before restarting
RESTART_COMMAND = ["bash", "public_start.sh"]  # Command to restart the app

def check_application_health():
    """Check if the application is healthy by making a request to the health endpoint"""
    try:
        response = requests.get(APP_URL, timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Health check failed: {e}")
        return False

def restart_application():
    """Restart the application"""
    logger.warning("Restarting application due to failed health checks")
    
    try:
        # Kill any existing processes
        subprocess.run(["pkill", "-f", "gunicorn"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "python.*main.py"], stderr=subprocess.DEVNULL)
        
        # Give processes time to shut down
        time.sleep(2)
        
        # Start the application using the restart command
        process = subprocess.Popen(
            RESTART_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Log the restart with the process ID
        logger.info(f"Application restarted with PID {process.pid}")
        
        # Give the application time to start
        time.sleep(10)
        
        # Check if the restart was successful
        if check_application_health():
            logger.info("Application successfully restarted and is healthy")
            return True
        else:
            logger.error("Application failed to restart properly")
            return False
            
    except Exception as e:
        logger.error(f"Error restarting application: {e}")
        return False

def main():
    """Main health check loop"""
    logger.info("Starting health check monitoring")
    
    consecutive_failures = 0
    
    while True:
        if check_application_health():
            # Application is healthy, reset failure counter
            if consecutive_failures > 0:
                logger.info("Application is now healthy")
            consecutive_failures = 0
        else:
            # Application is unhealthy
            consecutive_failures += 1
            logger.warning(f"Health check failed ({consecutive_failures}/{MAX_RETRIES})")
            
            # If we've reached the maximum number of retries, restart the application
            if consecutive_failures >= MAX_RETRIES:
                if restart_application():
                    consecutive_failures = 0
                else:
                    # If restart failed, wait longer before trying again
                    logger.error("Application restart failed, waiting before next attempt")
                    time.sleep(CHECK_INTERVAL * 2)
        
        # Wait for the next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Health check monitoring stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        sys.exit(1)