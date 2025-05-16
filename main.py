"""
NOUS Application Entry Point

This module serves as the entry point for the NOUS application.
It initializes the Flask application and starts the development server.

@module: main
@author: NOUS Development Team
"""
import os
from flask import Flask
from app import app
import logging
import routes  # Import routes to register authentication routes
from utils.key_config import validate_keys
from dotenv import load_dotenv
from api_documentation import register_openapi_blueprint
from utils.monitoring_middleware import init_monitoring
from utils.jwt_auth import init_token_cleanup
from utils.security_headers import init_security_headers
from utils.api_key_manager import init_api_key_cleanup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Validate API keys on startup
validate_keys()

# Set environment-specific configurations
app.config['DEBUG'] = os.environ.get('FLASK_ENV', 'production') != 'production'

# Initialize monitoring
init_monitoring(app)

# Initialize JWT token cleanup
init_token_cleanup(app)

# Initialize security headers
init_security_headers(app)

# Initialize API key cleanup
init_api_key_cleanup(app)

# Register OpenAPI documentation blueprint
register_openapi_blueprint(app)

if __name__ == "__main__":
    # Get port from environment or use default 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Start the development server
    app.run(host="0.0.0.0", port=port, debug=True)
