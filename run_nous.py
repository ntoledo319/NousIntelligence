"""
NOUS Personal Assistant - Launcher

This script runs the NOUS application with public access
"""
import os
import sys
import logging
from app_public_final import app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8080))
    
    # Log startup information
    logging.info(f"Starting NOUS Personal Assistant on port {port}")
    logging.info("Public access enabled (no Replit login required)")
    logging.info("Google authentication maintained for protected routes")
    
    # Run the application
    app.run(host="0.0.0.0", port=port)