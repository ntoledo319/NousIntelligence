"""
NOUS Personal Assistant - Main Entry Point

This file serves as the primary entry point for the NOUS application.
It imports and runs the Flask application.
"""

from app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)