"""
Simple and reliable authentication system for NOUS application

This module provides Google OAuth authentication with error handling
and simplified user management.
"""
import os
import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient

from models import User, db, UserSettings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load Google OAuth credentials from environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

# Google's OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
google_client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for routes
auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login")
def login():
    """Start Google OAuth flow"""
    try:
        # Log the state before starting
        logger.debug("Starting Google OAuth login process")
        
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            logger.error("Google OAuth credentials not configured")
            flash("Authentication system is not properly configured. Please contact the administrator.", "danger")
            return redirect(url_for("index"))
            
        # Find out what URL to hit for Google login
        try:
            google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        except Exception as e:
            logger.error(f"Error getting Google discovery URL: {str(e)}")
            flash("Could not connect to Google authentication service. Please try again later.", "warning")
            return redirect(url_for("index"))

        # Use the current domain for the redirect URI
        if request.host:
            domain = request.host
            # Force HTTPS for the callback
            redirect_uri = f"https://{domain}/auth/callback"
            logger.debug(f"Using redirect URI: {redirect_uri}")
            
            # Request access to user's profile info
            request_uri = google_client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=redirect_uri,
                scope=["openid", "email", "profile"],
            )
            
            return redirect(request_uri)
        else:
            logger.error("Could not determine host from request")
            flash("Authentication error: Could not determine application URL", "danger")
            return redirect(url_for("index"))
            
    except Exception as e:
        logger.error(f"Unexpected error in login route: {str(e)}")
        flash("Authentication system error. Please try again later.", "danger")
        return redirect(url_for("index"))

@auth_blueprint.route("/callback")
def callback():
    """Process the Google OAuth callback"""
    try:
        logger.debug("Processing Google OAuth callback")
        
        # Get authorization code from Google
        code = request.args.get("code")
        if not code:
            logger.warning("No authorization code received from Google")
            flash("Authentication failed. Please try again.", "warning")
            return redirect(url_for("index"))

        # Get token endpoint from Google
        try:
            google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
            token_endpoint = google_provider_cfg["token_endpoint"]
        except Exception as e:
            logger.error(f"Error getting Google discovery URL: {str(e)}")
            flash("Could not connect to Google authentication service. Please try again later.", "warning")
            return redirect(url_for("index"))

        # Prepare token request
        domain = request.host
        redirect_uri = f"https://{domain}/auth/callback"
        
        # Ensure URL has https protocol for security
        auth_response = request.url
        if auth_response.startswith('http:'):
            auth_response = auth_response.replace('http:', 'https:', 1)

        # Exchange code for tokens
        try:
            token_url, headers, body = google_client.prepare_token_request(
                token_endpoint,
                authorization_response=auth_response,
                redirect_url=redirect_uri,
                code=code
            )
            
            token_response = requests.post(
                token_url,
                headers=headers,
                data=body,
                auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
            )
            
            # Check if token request was successful
            if token_response.status_code != 200:
                logger.error(f"Token request failed with status {token_response.status_code}: {token_response.text}")
                flash("Authentication failed. Could not validate your credentials.", "danger")
                return redirect(url_for("index"))
                
            # Parse the tokens
            token_data = token_response.json()
            google_client.parse_request_body_response(json.dumps(token_data))
        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            flash("Authentication error during token exchange. Please try again.", "danger")
            return redirect(url_for("index"))

        # Get user info with token
        try:
            userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
            uri, headers, body = google_client.add_token(userinfo_endpoint)
            userinfo_response = requests.get(uri, headers=headers, data=body)
            
            # Check if userinfo request was successful
            if userinfo_response.status_code != 200:
                logger.error(f"Userinfo request failed with status {userinfo_response.status_code}: {userinfo_response.text}")
                flash("Could not retrieve your user information. Please try again.", "danger")
                return redirect(url_for("index"))
                
            userinfo = userinfo_response.json()
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            flash("Could not retrieve your profile information. Please try again.", "danger")
            return redirect(url_for("index"))

        # Verify user email
        if not userinfo.get("email_verified", False):
            logger.warning(f"Unverified email: {userinfo.get('email')}")
            flash("Your Google email is not verified. Please verify your email with Google first.", "warning")
            return redirect(url_for("index"))

        # Get user data
        email = userinfo["email"]
        
        # Find or create user in database
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new user
                logger.info(f"Creating new user for email: {email}")
                user = User()
                user.id = str(uuid.uuid4())  # Generate a UUID string for user ID
                user.email = email
                user.first_name = userinfo.get("given_name", "User")
                user.last_name = userinfo.get("family_name", "")
                user.profile_image_url = userinfo.get("picture", "")
                user.account_active = True
                user.created_at = datetime.utcnow()
                user.updated_at = datetime.utcnow()
                
                db.session.add(user)
                
                # Also create default user settings
                settings = UserSettings()
                settings.user_id = user.id
                settings.theme = "light"
                settings.color_theme = "default"
                settings.preferred_language = "en-US"
                settings.enable_voice_responses = False
                db.session.add(settings)
                
                db.session.commit()
                logger.info(f"Created new user with ID: {user.id}")
            else:
                # Update existing user information
                user.first_name = userinfo.get("given_name", user.first_name)
                user.last_name = userinfo.get("family_name", user.last_name)
                user.profile_image_url = userinfo.get("picture", user.profile_image_url)
                user.updated_at = datetime.utcnow()
                db.session.commit()
                logger.debug(f"Updated existing user: {user.id}")
        except Exception as e:
            logger.error(f"Database error handling user: {str(e)}")
            flash("An error occurred while processing your account. Please try again.", "danger")
            return redirect(url_for("index"))

        # Log the user in
        try:
            login_user(user)
            session['user_id'] = str(user.id)
            logger.info(f"User logged in: {user.id}")
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            flash("An error occurred during login. Please try again.", "danger")
            return redirect(url_for("index"))
        
        # Redirect to dashboard
        flash(f"Welcome, {user.first_name}!", "success")
        return redirect(url_for("dashboard"))
        
    except Exception as e:
        logger.error(f"Unhandled error in callback: {str(e)}")
        flash("An unexpected error occurred during authentication. Please try again.", "danger")
        return redirect(url_for("index"))

@auth_blueprint.route("/logout")
def logout():
    """Log the user out"""
    try:
        if current_user.is_authenticated:
            logger.info(f"Logging out user: {current_user.id}")
        logout_user()
        session.clear()
        flash("You have been logged out successfully.", "success")
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        flash("An error occurred during logout.", "warning")
    
    return redirect(url_for("index"))

def init_auth(app):
    """Initialize authentication with the Flask app"""
    app.register_blueprint(auth_blueprint, url_prefix="/auth")