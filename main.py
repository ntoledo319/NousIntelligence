"""
NOUS Personal Assistant - Main Entry Point

This file serves as the primary entry point for the NOUS application.
It creates and runs the Flask application using our application factory.
"""

import os
from app_factory import create_app

# Create application
app = create_app()

# Run the application when executed directly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)