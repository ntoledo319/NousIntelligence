"""
NOUS Personal Assistant - Application Factory

This module provides a factory function for creating and configuring
the Flask application with all necessary extensions, blueprints, and middleware.
"""

from app_factory import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Run the app with the correct port
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)