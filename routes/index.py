"""
Index Routes Module

This module defines routes for the main pages of the application.

@module routes.index
@description Main application routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from datetime import datetime
from models import User, db

# Create blueprint
index_bp = Blueprint('index', __name__)
logger = logging.getLogger(__name__)

@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    """Render the index page with integrated login functionality"""
    # If user is already logged in, just show the index page
    if current_user.is_authenticated:
        return render_template('index.html')
        
    # Handle login form submission if this is a POST request
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Validate input
        if not email or not password:
            flash('Please fill in all fields.', 'warning')
            return render_template('index.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('index.html')
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log in user
        login_user(user, remember=remember)
        logger.info(f"User {email} logged in successfully from index page")
        
        # Redirect to dashboard
        return redirect(url_for('dashboard.dashboard'))
    
    # GET request - show index page with login form
    return render_template('index.html')

@index_bp.route('/help')
def help_page():
    """Render the help page"""
    return render_template('help.html') 