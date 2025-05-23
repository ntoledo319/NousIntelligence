"""
NOUS Personal Assistant - Main Entry Point

This file serves as the primary entry point for the NOUS application.
It creates and runs the Flask application using our application factory.
"""

import os
from app import app

# Run the application when executed directly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)