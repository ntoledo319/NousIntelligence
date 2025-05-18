"""
Google OAuth Authentication Module

This module provides Google OAuth authentication using the recommended
oauthlib and requests approach for better compatibility and security.

@module auth.google_auth
@author NOUS Development Team
"""

import os
import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Blueprint, redirect, request, url_for, flash, session, current_app, render_template
from flask_login import login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient

from models import User, db, UserSettings, ConversationDifficulty, BetaTester

# Set up logger
logger = logging.getLogger(__name__)

# Google OAuth credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

# Google OAuth discovery document URL
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Create blueprint
google_bp = Blueprint("google_auth", __name__)

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@google_bp.route("/login")
def login():
    """
    Initiate Google OAuth login flow
    
    This starts the OAuth process by redirecting the user to Google's authentication page
    """
    logger.info("Starting Google OAuth login flow")
    
    # Check if we have Google credentials
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        logger.error("Google OAuth credentials not configured")
        
        # For development only - create a test user and login
        if current_app.config.get('DEBUG', False):
            try:
                # Check if our test user exists
                test_user = User.query.filter_by(email="test@example.com").first()
                
                if not test_user:
                    # Create a test user for development
                    test_user = User(
                        id=str(uuid.uuid4()),
                        email="test@example.com",
                        first_name="Test",
                        last_name="User",
                        profile_image_url="https://ui-avatars.com/api/?name=Test+User",
                        account_active=True
                    )
                    
                    # Create default settings
                    settings = UserSettings(
                        user_id=test_user.id,
                        theme="light",
                        conversation_difficulty=ConversationDifficulty.INTERMEDIATE,
                        enable_notifications=True,
                        default_location=None
                    )
                    
                    # Save to database
                    db.session.add(test_user)
                    db.session.add(settings)
                    db.session.commit()
                    
                    logger.info("Created test user for development")
                
                # Log the test user in
                login_user(test_user)
                flash("Logged in with test account (Google credentials not configured)", "warning")
                return redirect("/dashboard")
            
            except Exception as e:
                logger.error(f"Failed to create test user: {str(e)}")
                
        # Show proper error for production environment
        flash("Google authentication is not properly configured. Please contact the administrator.", "danger")
        return redirect(url_for("index.index"))
    
    # Get Google's OAuth endpoints from discovery document
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    except Exception as e:
        logger.error(f"Failed to fetch Google discovery document: {str(e)}")
        flash("Could not connect to Google authentication service. Please try again later.", "danger")
        return redirect(url_for("index.index"))
    
    # Build the redirect URI
    # First check if we're in a Replit environment
    if 'REPLIT_SLUG' in os.environ:
        # Use the Replit domain
        replit_domain = os.environ.get("REPLIT_SLUG", "mynous") + ".replit.app"
        redirect_uri = f"https://{replit_domain}/auth/callback/google"
    else:
        # Fall back to constructing from the request
        base_url = request.url_root.rstrip('/')
        redirect_uri = f"{base_url}/auth/callback/google"
    
    logger.info(f"Using redirect URI: {redirect_uri}")
    
    # Create the OAuth request URI
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    
    return redirect(request_uri)

@google_bp.route("/callback/google")
def callback():
    """
    Handle OAuth callback from Google
    
    This processes the response from Google's authentication server
    """
    logger.info("Received Google OAuth callback")
    
    # Check for error in callback
    if request.args.get("error"):
        error = request.args.get("error")
        logger.error(f"Google OAuth error: {error}")
        flash(f"Authentication error: {error}", "danger")
        return redirect(url_for("index.index"))
    
    # Get authorization code from callback
    code = request.args.get("code")
    if not code:
        logger.error("No OAuth code received in callback")
        flash("Authentication failed: No authorization code received", "danger")
        return redirect(url_for("auth.login"))
    
    # Get token endpoint from discovery document
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
    except Exception as e:
        logger.error(f"Failed to fetch Google discovery document: {str(e)}")
        flash("Authentication error: Could not connect to Google service", "danger")
        return redirect(url_for("index.index"))
    
    # Build the redirect URI (must match the one used in the login route)
    if 'REPLIT_SLUG' in os.environ:
        replit_domain = os.environ.get("REPLIT_SLUG", "mynous") + ".replit.app"
        redirect_uri = f"https://{replit_domain}/auth/callback/google"
    else:
        base_url = request.url_root.rstrip('/')
        redirect_uri = f"{base_url}/auth/callback/google"
    
    # Prepare the token request
    try:
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        
        # Send the token request to Google
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Parse the token response
        client.parse_request_body_response(json.dumps(token_response.json()))
    except Exception as e:
        logger.error(f"Token exchange failed: {str(e)}")
        flash("Authentication failed: Could not exchange token", "danger")
        return redirect(url_for("auth.login"))
    
    # Get user info from Google
    try:
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
    except Exception as e:
        logger.error(f"Could not get user info from Google: {str(e)}")
        flash("Authentication failed: Could not retrieve user information", "danger")
        return redirect(url_for("auth.login"))
    
    # Verify the user's email is confirmed by Google
    if not userinfo.get("email_verified", False):
        logger.warning(f"User tried to log in with unverified email: {userinfo.get('email')}")
        flash("Authentication failed: Email not verified by Google", "danger")
        return redirect(url_for("auth.login"))
    
    # Get user information
    email = userinfo["email"]
    first_name = userinfo.get("given_name", "")
    last_name = userinfo.get("family_name", "")
    profile_image = userinfo.get("picture", "")
    
    # Find or create user
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create a new user record
        logger.info(f"Creating new user account for: {email}")
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image,
            account_active=True
        )
        
        # Create default user settings
        settings = UserSettings(
            user_id=user.id,
            theme="light",
            conversation_difficulty=ConversationDifficulty.INTERMEDIATE,
            enable_notifications=True,
            default_location=None
        )
        
        # Add to beta testers if beta mode is enabled
        if current_app.config.get('BETA_MODE', False):
            max_testers = current_app.config.get('MAX_BETA_TESTERS', 30)
            current_tester_count = BetaTester.query.count()
            
            if current_tester_count < max_testers:
                beta_tester = BetaTester(
                    user_id=user.id,
                    access_granted=True,
                    invite_code=None,
                    granted_at=datetime.utcnow()
                )
                db.session.add(beta_tester)
                logger.info(f"Added {email} to beta testers (automatic enrollment)")
        
        # Save the user and settings
        db.session.add(user)
        db.session.add(settings)
        
        try:
            db.session.commit()
            logger.info(f"New user account created for: {email}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create new user: {str(e)}")
            flash("Account creation failed. Please try again later.", "danger")
            return redirect(url_for("auth.login"))
    else:
        # Update existing user's profile information
        user.first_name = first_name
        user.last_name = last_name
        user.profile_image_url = profile_image
        user.last_login = datetime.utcnow()
        
        try:
            db.session.commit()
            logger.info(f"Updated existing user profile for: {email}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update user profile: {str(e)}")
    
    # Log the user in
    login_user(user)
    logger.info(f"User logged in successfully: {email}")
    
    # Get the next URL if it was stored in the session
    next_url = session.pop('next', None)
    
    # Redirect to dashboard or next URL
    try:
        if user.first_name:
            welcome_message = f"Welcome back, {user.first_name}!"
        else:
            welcome_message = "Welcome back!"
        
        flash(welcome_message, "success")
        logger.info(f"User successfully authenticated: {user.email}")
        
        if next_url:
            # Make sure next_url is a valid relative URL
            if next_url.startswith('/'):
                logger.info(f"Redirecting to: {next_url}")
                return redirect(next_url)
            else:
                logger.warning(f"Invalid next_url: {next_url}")
                return redirect('/')
        else:
            # Use absolute URL to avoid routing issues
            logger.info("Redirecting to dashboard")
            return redirect('/dashboard')
    except Exception as e:
        logger.error(f"Error during post-authentication redirect: {str(e)}")
        # Fall back to home page on any error
        return redirect('/')

@google_bp.route("/logout")
@login_required
def logout():
    """
    Log the user out
    
    Clears the session and redirects to the home page
    """
    # Log the user out
    logout_user()
    
    # Clear the session
    session.clear()
    
    # Flash a message
    flash("You have been logged out successfully.", "success")
    
    # Redirect to the home page
    return redirect(url_for("index.index"))

def init_app(app):
    """
    Register the Google auth blueprint with the app
    
    Args:
        app: Flask application instance
    """
    # Register the blueprint with correct URL prefix
    app.register_blueprint(google_bp, url_prefix="/auth")
    
    # Add a root-level callback route for better compatibility
    @app.route("/auth/callback")
    def google_callback_root():
        """Root-level handler for Google OAuth callback"""
        return redirect(url_for("google_auth.callback"))
    
    logger.info("Google authentication configured successfully")