"""
NOUS - Personal Assistant Application
Main application entry point

This module serves as the unified entry point for the NOUS application.
It initializes the Flask application using the application factory pattern
and starts the development server.

@module main
@description Core application initialization and configuration
@context_boundary Application Core
"""

import os
import logging

# Set up logging before importing app modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Import the application factory
from app_factory import create_app

# Create the application using the factory
app = create_app()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Determine debug mode (should be False in production)
    debug = os.environ.get("FLASK_ENV") == "development"
    
    # Additional startup logging
    logging.info(f"Starting NOUS application on port {port}")
    logging.info(f"Debug mode: {debug}")
    
    # Start the server
    app.run(host="0.0.0.0", port=port, debug=debug)
