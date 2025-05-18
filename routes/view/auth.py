"""
Authentication View Routes

This module contains view routes for user authentication,
including login, logout and registration.

@module routes.view.auth
@author NOUS Development Team
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logger
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Display login page with authentication options
    
    Returns:
        Rendered login template with available authentication providers
    """
    # Get the next URL if it exists
    next_url = request.args.get('next', '')
    
    # Store next URL in session for post-login redirect
    if next_url:
        session['next'] = next_url
    
    # Log access to login page
    client_ip = request.remote_addr
    logger.info(f"Login page accessed from IP: {client_ip}")
    
    # Render the login template
    return render_template("login.html", next=next_url)