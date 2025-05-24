"""
NOUS Personal Assistant - Entry Point

This module serves as the entry point for the NOUS application.
"""

import os
import logging
from app import app

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get port from environment with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting NOUS application on port {port}")
    
    # Check for Replit environment
    is_replit = "REPLIT_DB_URL" in os.environ
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Log deployment information
    logger.info(f"Environment: {'Replit' if is_replit else 'Standard'}")
    logger.info(f"Debug mode: {'On' if debug_mode else 'Off'}")
    
    # Run the application
    app.run(host="0.0.0.0", port=port, debug=debug_mode)