"""
NOUS Personal Assistant - Gunicorn App

This file serves as the entry point for gunicorn to run the application.
Using gunicorn helps ensure the app runs properly on Replit.
"""

from nous_solution import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)