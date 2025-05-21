"""
Main Application Entry Point

This is the single entry point for the NOUS personal assistant application.
The application is created using the factory pattern defined in app_factory.py.
"""

import os
import logging
from flask import redirect, request, url_for
from app_factory import create_app

logger = logging.getLogger(__name__)

app = create_app()

# Initialize database tables
with app.app_context():
    db.create_all()

@app.route('/callback/google')
def root_google_callback():
    """Root-level Google OAuth callback handler"""
    logger.info("Root-level Google OAuth callback received")
    logger.info(f"Callback arguments: {request.args}")
    
    # Redirect to the proper handler in google_bp blueprint
    return redirect(url_for('google_auth.callback', **request.args))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)