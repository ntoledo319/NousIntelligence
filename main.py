"""
Main Application Entry Point

This is the single entry point for the NOUS personal assistant application.
The application is created using the factory pattern defined in app_factory.py.
"""

from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)