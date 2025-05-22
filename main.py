"""
NOUS Personal Assistant - Application Entry Point

This is the main entry point for the NOUS personal assistant application.
It imports the app object from app.py for use by Python interpreters and WSGI servers.
"""

from app import app

# This file serves as the main entry point for the application
# All functionality is imported from app.py

if __name__ == "__main__":
    # Start the application if this file is run directly
    app.run(host="0.0.0.0", port=int(app.config.get("PORT", 8080)))