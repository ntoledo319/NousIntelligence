"""
Authentication Module for NOUS Application

This module provides OAuth2 authentication with Google.
It handles user registration, login, and session management.

@module: fixed_auth
@author: NOUS Development Team
"""

import os
import json
import datetime
from flask import Blueprint, session, redirect, url_for
from flask import current_app, request, flash, render_template
from flask_login import login_user, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import db, User, OAuth, UserSettings, ConversationDifficulty, BetaTester
from utils.security_helper import generate_csrf_token, log_security_event, sanitize_input

# Create a Blueprint for Google OAuth
google_auth = Blueprint('google_auth', __name__)

# Configure Google OAuth Blueprint
def create_blueprint():
    """Create and configure the Google OAuth blueprint dynamically"""
    # Get credentials from environment variables
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    # Fallback to file if environment variables not set (for development only)
    if not (client_id and client_secret):
        client_secrets_file = os.environ.get("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
        try:
            with open(client_secrets_file, "r") as f:
                client_info = json.load(f)["web"]
                client_id = client_info.get("client_id")
                client_secret = client_info.get("client_secret")
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load Google OAuth credentials: {str(e)}")
    
    # Get redirect URI from environment or construct from request
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
    if not redirect_uri and request:
        redirect_uri = request.url_root.rstrip('/') + "/callback/google"
    
    # Create the blueprint with the obtained credentials
    blueprint = make_google_blueprint(
        client_id=client_id,
        client_secret=client_secret,
        scope=["openid", "email", "profile"],
        redirect_url=redirect_uri,
        storage=SQLAlchemyStorage(
            OAuth,
            db.session,
            user=current_user,
            user_required=False,
            cache=True
        )
    )
    
    return blueprint

# Create routes outside of blueprint creation since it needs app context
@google_auth.route("/login")
def login():
    """Route for initiating Google OAuth login"""
    # Generate CSRF token for session
    csrf_token = generate_csrf_token()
    session['oauth_state'] = csrf_token
    
    # Redirect to Google for authorization
    return redirect(url_for("google.login"))

@google_auth.route("/logout")
def logout():
    """Log out the current user"""
    # Clear the user's session
    logout_user()
    session.clear()
    
    # Flash a message confirming logout
    flash("You have been logged out successfully.", "success")
    
    # Redirect to the home page
    return redirect(url_for("index"))

@oauth_authorized.connect_via(create_blueprint())
def google_logged_in(blueprint, token):
    """Handle OAuth response from Google"""
    if not token:
        flash("Failed to log in with Google.", "error")
        log_security_event("login_failed", "No token received from Google")
        return False
    
    # Store the authentication metrics
    session['auth_time'] = datetime.datetime.utcnow().timestamp()
    session['auth_source'] = 'google'
    
    # Get user info from Google
    try:
        resp = google.get("/oauth2/v1/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", "error")
            log_security_event("login_failed", f"Failed to fetch user info: {resp.text}")
            return False
        
        user_info = resp.json()
        user_id = user_info["id"]
        user_email = sanitize_input(user_info.get("email", ""))
        
        # Create browser session key for multi-session support
        browser_session_key = request.headers.get('User-Agent', 'unknown') + request.remote_addr
        
        # Check if this OAuth token already exists
        try:
            oauth = OAuth.query.filter_by(
                provider="google",
                provider_user_id=user_id,
                browser_session_key=browser_session_key
            ).first()
        except SQLAlchemyError as e:
            flash("Database error during login.", "error")
            log_security_event("database_error", str(e))
            return False
        
        if oauth:
            # OAuth token exists, log in the associated user
            login_user(oauth.user)
            flash("Successfully signed in with Google.", "success")
            log_security_event("login_success", f"User {oauth.user.id} logged in")
            
            # Update last activity timestamp
            session['last_activity'] = datetime.datetime.utcnow().timestamp()
            return False  # Don't create a new OAuth token
        
        # No OAuth token exists yet for this user
        # Check if user exists by email
        user = User.query.filter_by(email=user_email).first()
        if not user:
            # Create a new user
            user = User(
                id=user_id,
                email=user_email,
                first_name=sanitize_input(user_info.get("given_name", "")),
                last_name=sanitize_input(user_info.get("family_name", "")),
                profile_image_url=user_info.get("picture", ""),
                is_admin=False,
                account_active=True
            )
            
            # Create user settings with defaults
            settings = UserSettings(
                user=user,
                conversation_difficulty=ConversationDifficulty.INTERMEDIATE.value
            )
            
            # Add to database
            db.session.add(user)
            db.session.add(settings)
            
            # If beta mode is enabled, register as beta tester
            if current_app.config.get('ENABLE_BETA_MODE', False):
                beta_tester = BetaTester(user=user, status='active')
                db.session.add(beta_tester)
            
            # Commit to database
            try:
                db.session.commit()
                log_security_event("user_created", f"New user {user.id} created")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash("Failed to create new user account.", "error")
                log_security_event("database_error", str(e))
                return False
        
        # Create a new OAuth token for the user
        oauth = OAuth(
            provider="google",
            provider_user_id=user_id,
            token=token,
            browser_session_key=browser_session_key,
            user=user
        )
        
        # Add and commit
        try:
            db.session.add(oauth)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Failed to save authentication token.", "error")
            log_security_event("database_error", str(e))
            return False
        
        # Log in the user
        login_user(user)
        flash("Successfully signed in with Google.", "success")
        log_security_event("login_success", f"User {user.id} logged in")
        
        # Update last activity timestamp
        session['last_activity'] = datetime.datetime.utcnow().timestamp()
        
        # Signal that we have processed this OAuth response
        return False
    
    except Exception as e:
        flash("An error occurred during sign in.", "error")
        log_security_event("login_error", str(e))
        return False

def register_auth_blueprint(app):
    """Register the Google OAuth blueprint with the Flask app"""
    # Create the blueprint
    blueprint = create_blueprint()
    
    # Register the blueprint with the app
    app.register_blueprint(blueprint, url_prefix="/login")
    
    # Register the google_auth blueprint with the app
    app.register_blueprint(google_auth)