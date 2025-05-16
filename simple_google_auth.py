"""
Ultra-minimalist Google OAuth implementation for Flask
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

# Load client configuration from client_secret.json
try:
    with open('client_secret.json', 'r') as f:
        client_config = json.load(f)['web']
    GOOGLE_CLIENT_ID = client_config['client_id']
    GOOGLE_CLIENT_SECRET = client_config['client_secret']
    # Get registered redirect URIs
    REGISTERED_REDIRECT_URIS = client_config['redirect_uris']
    logger.info(f"Loaded Google OAuth configuration")
    logger.info(f"Registered redirect URIs: {REGISTERED_REDIRECT_URIS}")
except Exception as e:
    logger.error(f"Error loading client_secret.json: {str(e)}")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    REGISTERED_REDIRECT_URIS = []
    logger.info("Using Google OAuth configuration from environment variables")

# Google's OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Create blueprint
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login")
def login():
    """Start Google OAuth flow with minimal approach"""
    # Get current domain
    current_domain = request.host

    # Find a matching redirect URI based on current domain
    redirect_uri = None
    for uri in REGISTERED_REDIRECT_URIS:
        if current_domain in uri and "/callback/google" in uri:
            redirect_uri = uri
            break
    
    # If no matching domain found, use the first one
    if not redirect_uri and REGISTERED_REDIRECT_URIS:
        redirect_uri = REGISTERED_REDIRECT_URIS[0]
    
    if not redirect_uri:
        logger.error("No valid redirect URI found")
        flash("Authentication configuration error", "error")
        return redirect(url_for('index'))
    
    logger.info(f"Using redirect URI: {redirect_uri}")
    
    # Store the redirect URI in session for callback verification
    session['google_oauth_redirect_uri'] = redirect_uri
    
    try:
        # Get Google's authorization endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Initialize OAuth client
        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        
        # Create OAuth request URL with basic scopes
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        
        logger.info(f"Auth request: {request_uri}")
        
        # Redirect to Google's authorization page
        return redirect(request_uri)
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        flash("Authentication error. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/callback/google")
def callback():
    """Process Google OAuth callback"""
    # Retrieve the redirect URI from session
    redirect_uri = session.get('google_oauth_redirect_uri')
    if not redirect_uri:
        logger.error("No redirect URI found in session")
        flash("Authentication session expired. Please try again.", "error")
        return redirect(url_for('index'))
    
    try:
        # Get the authorization code
        code = request.args.get("code")
        if not code:
            logger.error("No authorization code received")
            flash("Authentication failed. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Initialize OAuth client
        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        
        # Get token endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Get token
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=redirect_uri,
            code=code
        )
        
        logger.info(f"Token request: {token_url}")
        
        # Exchange code for token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Check for token errors
        if token_response.status_code != 200:
            logger.error(f"Token error: {token_response.text}")
            flash("Authentication failed. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Parse token response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        # Get user data
        email = userinfo.get("email")
        if not email:
            logger.error("No email in user info")
            flash("Could not get email from Google. Please try again.", "error")
            return redirect(url_for('index'))
            
        name = userinfo.get("given_name", "User")
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        # Create new user if needed
        if not user:
            user = User()
            user.id = str(uuid.uuid4())
            user.email = email
            user.first_name = name
            user.created_at = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {email}")
        
        # Log in user
        login_user(user)
        
        # Save user info to session
        session['user_id'] = user.id
        session['user_email'] = email
        session['user_name'] = name
        
        # Clear OAuth session data
        session.pop('google_oauth_redirect_uri', None)
        
        # Success!
        flash(f"Welcome, {name}!", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        flash("Authentication error. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/logout")
@login_required
def logout():
    """Log user out"""
    logout_user()
    
    # Clear all session data
    session.clear()
    
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))