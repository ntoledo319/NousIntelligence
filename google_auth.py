"""
Simple Google OAuth implementation for Flask
"""
import os
import json
import logging
from datetime import datetime
import uuid

import requests
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
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
    REDIRECT_URIS = client_config['redirect_uris']
    logger.info(f"Loaded Google OAuth configuration from client_secret.json")
    logger.info(f"Registered redirect URIs: {REDIRECT_URIS}")
except Exception as e:
    logger.error(f"Error loading client_secret.json: {str(e)}")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    REDIRECT_URIS = [os.environ.get("GOOGLE_REDIRECT_URI", "")]
    logger.info("Using Google OAuth configuration from environment variables")

# Google's OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for routes
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login")
def login():
    """Start Google OAuth flow - simplest possible version"""
    try:
        # Get Google's OAuth endpoints
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Find an appropriate redirect URI that matches our domain
        callback_uri = url_for('google_auth.callback', _external=True).replace('http://', 'https://')
        
        # Log for debugging
        logger.info(f"Callback URI: {callback_uri}")
        
        # If our callback doesn't match any registered URI, find the best match
        matching_uri = None
        for uri in REDIRECT_URIS:
            if uri.endswith('/callback/google'):
                matching_uri = uri
                break
        
        if matching_uri:
            logger.info(f"Using registered callback URI: {matching_uri}")
            
        # Create OAuth request URL with basic scopes only
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=matching_uri or callback_uri,
            scope=["openid", "email", "profile"],  # Minimal scopes
        )
        
        # Redirect to Google's authorization server
        return redirect(request_uri)
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        flash("An error occurred during authentication. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/callback/google")
def callback():
    """Process the Google OAuth callback - simplest possible version"""
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
        
        # Prepare the token request
        # Use the exact same URI as in the authorization request
        matching_uri = None
        for uri in REDIRECT_URIS:
            if uri.endswith('/callback/google'):
                matching_uri = uri
                break
        
        callback_uri = url_for('google_auth.callback', _external=True).replace('http://', 'https://')
        redirect_uri = matching_uri or callback_uri
        
        # Create the token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=redirect_uri,
            code=code
        )
        
        # Send the request to get tokens
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Parse the response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        # Make sure their email is verified
        if not userinfo.get("email_verified"):
            logger.error("User email not verified by Google")
            flash("Email not verified. Please verify your email with Google.", "error")
            return redirect(url_for('index'))
        
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
            user.created_at = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {email}")
        
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

@google_auth.route("/logout")
@login_required
def logout():
    """Log the user out"""
    logout_user()
    
    # Clear session data
    for key in list(session.keys()):
        session.pop(key, None)
    
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))