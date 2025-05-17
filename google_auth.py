"""
Minimal Google OAuth implementation for Flask
"""
import os
import json
import logging
from datetime import datetime
import uuid

import requests
from flask import Blueprint, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient

from models import User, db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Google OAuth credentials from environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

# Construct the redirect URI based on the request domain
def get_redirect_uri():
    # Use a fixed value for Flask context outside of request
    try:
        if request:
            base_url = request.url_root.rstrip('/')
            if base_url.startswith('http://'):
                base_url = base_url.replace('http://', 'https://', 1)
            return f"{base_url}/auth/callback/google"
    except RuntimeError:
        # This happens when called outside of a request context
        pass
    
    # Use environment variable or fallback
    return os.environ.get("GOOGLE_REDIRECT_URI", "https://mynous.replit.app/auth/callback/google")

if GOOGLE_CLIENT_ID:
    logger.info(f"Using Google OAuth credentials from environment variables")
    logger.info(f"Client ID: {GOOGLE_CLIENT_ID[:10]}..." if GOOGLE_CLIENT_ID else "Not set")
else:
    logger.warning("Google OAuth credentials not found in environment variables!")

# Google's OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for routes
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/auth/login")
def login():
    """Start Google OAuth flow with minimal scopes"""
    try:
        # Get Google's OAuth endpoints
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Get current host and dynamic redirect URI
        redirect_uri = get_redirect_uri()
        current_host = request.host
        logger.info(f"Current host: {current_host}")
        logger.info(f"Using dynamic redirect URI: {redirect_uri}")
        
        # Create OAuth request URL with minimal scopes
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],  # Minimal scopes
        )
        
        logger.info(f"Authorization request URI: {request_uri}")
        
        # Redirect to Google's authorization server
        return redirect(request_uri)
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        flash("An error occurred during authentication. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/auth/callback/google")
def callback():
    """Process the Google OAuth callback"""
    try:
        # Get the authorization code from the callback
        code = request.args.get("code")
        if not code:
            logger.error("No authorization code received")
            flash("Authentication failed. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Get token endpoint from Google's discovery document
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Get current request URL and dynamic redirect URI
        current_url = request.url
        redirect_uri = get_redirect_uri()
        logger.info(f"Current callback URL: {current_url}")
        logger.info(f"Using redirect URI: {redirect_uri}")
        
        # Create the token request with dynamic redirect URI
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=redirect_uri,
            code=code
        )
        
        logger.info(f"Token request URL: {token_url}")
        
        # Send the request to get tokens (explicitly cast to str to satisfy type checker)
        client_id = str(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else ""
        client_secret = str(GOOGLE_CLIENT_SECRET) if GOOGLE_CLIENT_SECRET else ""
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(client_id, client_secret)
        )
        
        # Check for token errors
        if 'error' in token_response.json():
            error = token_response.json().get('error')
            logger.error(f"Token error: {error}")
            flash(f"Authentication error: {error}", "error")
            return redirect(url_for('index'))
        
        # Parse the response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        # Get user information
        email = userinfo["email"]
        name = userinfo.get("given_name", "User")
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        # Create a new user if needed
        if not user:
            user = User()
            user.id = str(uuid.uuid4())
            user.email = email
            user.first_name = name
            user.last_name = userinfo.get("family_name", "")
            user.profile_image_url = userinfo.get("picture", None)
            user.created_at = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {email}")
            
            # Check if this is a known beta email domain
            from utils.beta_test_helper import auto_register_beta_tester
            beta_domains = os.environ.get("BETA_EMAIL_DOMAINS", "replit.com,gmail.com").split(",")
            is_beta_domain = any(email.lower().endswith(f"@{domain.lower()}") for domain in beta_domains)
            
            # Auto-register as beta tester if from approved domain
            if is_beta_domain:
                try:
                    auto_register_beta_tester(user.id, f"Auto-registered from {email}")
                    logger.info(f"Auto-registered beta tester: {email}")
                except Exception as e:
                    logger.error(f"Error auto-registering beta tester: {str(e)}")
        
        # Log in the user
        login_user(user)
        
        # Save basic user info in session
        session['user_id'] = user.id
        session['user_email'] = email
        session['user_name'] = name
        
        # Save access token
        session['access_token'] = token_response.json().get('access_token')
        
        # Redirect to home page
        flash(f"Welcome, {name}!", "success")
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        flash("An error occurred during authentication. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/auth/logout")
@login_required
def logout():
    """Log the user out"""
    logout_user()
    
    # Clear session data
    for key in list(session.keys()):
        session.pop(key, None)
    
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))