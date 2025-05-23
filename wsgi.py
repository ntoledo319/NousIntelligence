"""
NOUS Personal Assistant - WSGI Entry Point

This file serves as the WSGI entry point for Gunicorn and other WSGI servers.
It includes application initialization and configuration for production deployment.
"""

import os
from app_factory import create_app

# Create the Flask application with production configuration
app = create_app()

# Configure for production
app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "nous-secure-key-2025")),
    PREFERRED_URL_SCHEME="https"
)

# Add any production-specific setup here
if os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)