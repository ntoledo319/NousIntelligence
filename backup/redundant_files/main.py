"""
NOUS Personal Assistant - Main Entry Point

This file serves as the entry point for the NOUS application,
importing the Flask app from app.py.
"""
from app import app

# This allows the application to be imported by WSGI servers
if __name__ == '__main__':
    app.run(host='0.0.0.0')