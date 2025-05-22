"""
NOUS Personal Assistant - WSGI Entry Point

This file serves as the WSGI entry point for Gunicorn and other WSGI servers.
It simply imports the 'app' object from main.py.
"""

from main import app

if __name__ == "__main__":
    app.run()