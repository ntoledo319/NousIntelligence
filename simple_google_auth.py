"""
Simple Google OAuth implementation for Flask applications
"""
import os
import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient

from models import User, db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Google OAuth credentials from environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

# Google's OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for routes
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login")
def login():
    """Start Google OAuth flow"""
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use the current domain for the redirect URI
    domain = request.host
    redirect_uri = f"https://{domain}/callback/google"
    logger.info(f"Using redirect URI: {redirect_uri}")

    # Request access to user's profile info
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)

@google_auth.route("/callback/google")
def callback():
    """Process the Google OAuth callback"""
    try:
        # Get authorization code from Google
        code = request.args.get("code")
        if not code:
            flash("Authentication failed. Please try again.", "error")
            return redirect(url_for("index"))

        # Get token endpoint from Google
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare token request
        domain = request.host
        redirect_uri = f"https://{domain}/callback/google"
        
        # Ensure URL has https protocol for security
        auth_response = request.url
        if auth_response.startswith('http:'):
            auth_response = auth_response.replace('http:', 'https:', 1)

        # Exchange code for tokens
        token_url, headers, body = client.prepare_token_request(
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

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info with token
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()

        # Verify user email
        if not userinfo.get("email_verified", False):
            flash("Email not verified with Google. Please verify your email first.", "warning")
            return redirect(url_for("index"))

        # Get user data
        email = userinfo["email"]
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user
            user = User()
            user.id = str(uuid.uuid4())  # Generate a UUID string for user ID
            user.email = email
            user.first_name = userinfo.get("given_name", "User")
            user.last_name = userinfo.get("family_name", "")
            user.profile_image_url = userinfo.get("picture", "")
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {email}")
            
            # Check beta access if in beta mode
            if current_app.config.get('BETA_MODE', False):
                from utils.beta_test_helper import is_beta_tester, auto_register_beta_tester
                
                # Auto-register users from approved domains
                beta_domains = os.environ.get("BETA_EMAIL_DOMAINS", "").split(",")
                is_beta_domain = any(email.lower().endswith(f"@{domain.lower()}") for domain in beta_domains if domain)
                
                if is_beta_domain:
                    try:
                        auto_register_beta_tester(user.id, f"Auto-registered from {email}")
                        flash("You've been automatically registered for our beta program!", "success")
                    except Exception as e:
                        logger.error(f"Error auto-registering beta tester: {str(e)}")
                
                # If not auto-registered and beta access required, redirect to request page
                elif not is_beta_tester(email):
                    session['pending_email'] = email
                    flash("You need beta access to use this application", "warning")
                    return redirect(url_for('beta.request_access'))

        # Log the user in
        login_user(user)
        session['user_id'] = str(user.id)
        
        # Redirect to dashboard
        flash(f"Welcome, {user.first_name}!", "success")
        return redirect(url_for("dashboard"))
        
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("index"))

@google_auth.route("/logout")
@login_required
def logout():
    """Log the user out"""
    logout_user()
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("index"))