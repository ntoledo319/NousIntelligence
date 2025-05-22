"""
NOUS Personal Assistant - Main Entry Point

This file serves as the primary entry point for Replit to run the application.
It imports and runs the Flask application from app.py
"""

# Simply import and run the app from our dedicated app file
from app import app

# This will make the app run when executed by Replit
if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)