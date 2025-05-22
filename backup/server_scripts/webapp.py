"""
Simple Flask Wrapper for Replit

This file serves as a simple entry point for launching the Flask application
on Replit. It imports the main application instance and runs it with the
correct host and port settings for Replit.
"""

import os
from main import app

if __name__ == "__main__":
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Run with host 0.0.0.0 to make it accessible outside localhost
    app.run(host='0.0.0.0', port=port)