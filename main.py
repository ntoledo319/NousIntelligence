"""
NOUS Personal Assistant - Main Entry Point

This file serves as the main entry point for the application.
It directly runs the deployment script.
"""
import os
import sys
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("NOUS Personal Assistant starting...")
    
    try:
        # Import and run the app from deployment.py
        from deployment import app
        
        # Run the application on port 8080
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)