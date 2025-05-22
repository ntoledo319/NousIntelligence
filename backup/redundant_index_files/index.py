"""
NOUS Personal Assistant - Main Entry Point

This file serves as the primary entry point for Replit to run the application.
"""

# Import our fixed app that handles all routes properly
import sys
import os

# Use our fixed app version with proper routing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app_fixed import app

# This ensures Replit uses our app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)