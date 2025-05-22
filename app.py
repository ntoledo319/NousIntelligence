
"""
NOUS Personal Assistant - Application Entry Point

This module provides the Flask application instance for deployment.
"""

from app_factory import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Run the app with the correct port
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
