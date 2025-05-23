"""
WSGI entry point for the NOUS Personal Assistant

This file serves as the WSGI entry point for production deployments.
"""

from app import app

# This variable is used by WSGI servers to find the application
application = app

if __name__ == "__main__":
    app.run()