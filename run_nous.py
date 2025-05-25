"""
NOUS Personal Assistant - Launcher

This script runs the NOUS application with public access
It's designed to be executed directly or called from deployment.py
"""
import os
import sys
import logging
from app_public_final import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the application"""
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8080))
    
    # Log startup information
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    logger.info("Public access enabled (no Replit login required)")
    logger.info("Google authentication maintained for protected routes")
    
    try:
        # Run the application
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error running application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()