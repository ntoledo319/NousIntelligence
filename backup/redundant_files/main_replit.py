"""
NOUS Personal Assistant - Replit Main Entry Point

This file serves as the primary entry point specifically designed to work with Replit.
"""

# Import the application from our simplified app file
from simple_app import app

# This is required for Replit to properly detect and run the application
if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)