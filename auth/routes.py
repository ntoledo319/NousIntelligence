"""
Authentication Routes

This module implements the core authentication routes for the application.

@module auth.routes
@description Core authentication routes
"""

import logging
import uuid
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime

from auth import auth_bp
from models import User, UserSettings, db

logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Validate input
        if not email or not password:
            flash('Please fill in all fields.', 'warning')
            return render_template('login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Create a default admin user if none exists
        if not user and email == 'admin@example.com' and password == 'admin123':
            try:
                # Create a new admin user
                user = User()
                user.id = str(uuid.uuid4())
                user.email = 'admin@example.com'
                user.username = 'admin'
                user.first_name = 'Admin'
                user.last_name = 'User'
                user.active = True
                
                # Set password
                user.set_password('admin123')
                
                # Add user to database
                db.session.add(user)
                db.session.commit()
                
                # Create settings for the user
                settings = UserSettings()
                settings.user_id = user.id
                settings.theme = 'light'
                settings.language = 'en'
                settings.timezone = 'UTC'
                settings.notifications_enabled = True
                
                # Add settings to database
                db.session.add(settings)
                db.session.commit()
                
                logger.info("Default admin user created during login attempt")
                flash('Default admin account created. Welcome!', 'success')
            except Exception as e:
                logger.error(f"Error creating default user: {str(e)}")
                db.session.rollback()
                flash('Error creating default user. Please try again.', 'danger')
                return render_template('login.html')
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('login.html')
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log in user
        login_user(user, remember=remember)
        logger.info(f"User {email} logged in successfully")
        
        # Redirect to dashboard
        return redirect(url_for('dashboard.dashboard'))
    
    # GET request - show login form
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        # Validate input
        if not email or not first_name or not password or not confirm:
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('index.index'))
            
        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('index.index'))
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'warning')
            return redirect(url_for('index.index'))
        
        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        new_user.set_password(password)
        
        # Create default settings for the user
        settings = UserSettings(user_id=new_user.id)
        
        # Add user and settings to the database
        db.session.add(new_user)
        db.session.add(settings)
        db.session.commit()
        
        logger.info(f"New user registered: {email}")
        
        # Log in the new user
        login_user(new_user)
        
        # Redirect to welcome page
        return redirect(url_for('welcome'))
    
    # GET request - redirect to index page
    return redirect(url_for('index.index')) 