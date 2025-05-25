"""
NOUS Personal Assistant - Main Entry Point (Public Access)

This script runs the public version of the NOUS application
without requiring Replit login while maintaining Google authentication.
"""
from app_public_final import app

if __name__ == "__main__":
    # Start the application
    app.run(host="0.0.0.0", port=8080)