# Use this Flask blueprint for Google authentication

import json
import os
import logging

import requests
from flask import Blueprint, redirect, request, url_for, session, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from models import User, db
from werkzeug.security import generate_password_hash

# Load client configuration from client_secret.json
with open('client_secret.json', 'r') as f:
    client_config = json.load(f)['web']

GOOGLE_CLIENT_ID = client_config['client_id']
GOOGLE_CLIENT_SECRET = client_config['client_secret']
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create Blueprint
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login")
def login():
    """Start Google OAuth flow"""
    try:
        # Get Google's OAuth configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Get the redirect URIs from client configuration
        # Use these exact URIs as registered in Google Cloud console
        registered_redirect_uris = client_config.get('redirect_uris', [])
        
        # Use the exact redirect URI that matches our domain
        # This is critical for the OAuth flow to work correctly
        callback_uri = url_for('google_auth.callback', _external=True).replace('http://', 'https://')
        
        # Log the URL being used (for debugging)
        logger.info(f"Login callback URI: {callback_uri}")
        logger.info(f"Registered URIs: {registered_redirect_uris}")
        
        # If our callback doesn't match registered URIs, try to use a matching one
        if callback_uri not in registered_redirect_uris:
            # Find the best matching URI based on the domain
            current_domain = request.host
            for uri in registered_redirect_uris:
                if current_domain in uri:
                    callback_uri = uri
                    logger.info(f"Using alternate callback URI: {callback_uri}")
                    break
        
        # Create the OAuth request URL with basic scopes only
        # We'll request additional scopes after successful authentication
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=callback_uri,
            scope=["openid", "email", "profile"],
        )
        
        # Redirect to Google's OAuth page
        return redirect(request_uri)
    
    except Exception as e:
        logger.error(f"Error in Google OAuth login: {str(e)}")
        flash("An error occurred during Google authentication. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/callback")
def callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from the callback request
        code = request.args.get("code")
        if not code:
            logger.error("No code received in callback")
            flash("Authentication failed - no authorization code received", "error")
            return redirect(url_for('index'))
        
        # Get Google's token endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Use the same callback URI as in the login function
        callback_uri = url_for('google_auth.callback', _external=True).replace('http://', 'https://')
        
        # Registered URI that matches our domain
        registered_redirect_uris = client_config.get('redirect_uris', [])
        if callback_uri not in registered_redirect_uris:
            current_domain = request.host
            for uri in registered_redirect_uris:
                if current_domain in uri:
                    callback_uri = uri
                    logger.info(f"Using alternate callback URI: {callback_uri}")
                    break
        
        # Prepare and send token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=callback_uri,
            code=code
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Parse the token response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        # Verify user email
        if not userinfo.get("email_verified"):
            logger.error("User email not verified by Google")
            flash("Authentication failed - email not verified", "error")
            return redirect(url_for('index'))
        
        # Get user data
        user_email = userinfo["email"]
        user_name = userinfo.get("given_name", "User")
        
        # Check if user exists, create if new
        user = User.query.filter_by(email=user_email).first()
        if not user:
            # Create a new user
            user = User(
                username=user_name,
                email=user_email
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {user_email}")
        
        # Login the user
        login_user(user)
        
        # Store Google credentials in session
        session['google_user'] = {
            'email': user_email,
            'name': user_name
        }
        
        # Store access token
        session['access_token'] = token_response.json().get('access_token')
        
        # Success message
        flash(f"Welcome, {user_name}!", "success")
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        flash("An error occurred during Google authentication. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route("/logout")
@login_required
def logout():
    """Log user out"""
    logout_user()
    
    # Clear all session data
    for key in list(session.keys()):
        session.pop(key, None)
    
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))