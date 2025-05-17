"""
Standardized Google Authentication Module

This module provides a more standardized approach to Google OAuth authentication
using the oauthlib and WebApplicationClient approach recommended by Google.
It's designed to be more maintainable and adhere to Google's best practices.
"""

import json
import os

import requests
from flask import Blueprint, redirect, request, url_for, current_app
from flask_login import login_required, login_user, logout_user
from models import User, db
from oauthlib.oauth2 import WebApplicationClient

# Load client credentials from the client_secret.json file
# This follows Google's recommended approach
try:
    with open('client_secret.json', 'r') as f:
        client_config = json.load(f)
        GOOGLE_CLIENT_ID = client_config['web']['client_id']
        GOOGLE_CLIENT_SECRET = client_config['web']['client_secret']
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    # Fallback to environment variables if file not found or invalid
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")

# Google's OAuth 2.0 discovery document URL
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint
google_auth = Blueprint("google_auth", __name__)


@google_auth.route("/google_login")
def login():
    """Initiate Google OAuth login flow."""
    # Get discovery document
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Use the current application's domain to construct the callback URL
    # This ensures it matches what's registered in Google Cloud Console
    # Get domain from either environment variable or default to the canonical domain
    domain = request.host
    
    # Make the URL path absolute (for Google's verification)
    base_url = request.url_root.rstrip('/')
    redirect_uri = f"{base_url}/google_login/callback"
    
    # Prepare the OAuth request
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@google_auth.route("/google_login/callback")
def callback():
    """Handle the OAuth callback from Google."""
    # Get the authorization code from the callback request
    code = request.args.get("code")
    if not code:
        return "Authorization code not received", 400
    
    # Get token endpoint from discovery document
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Construct the full callback URL that matches what was used in the request
    base_url = request.url_root.rstrip('/')
    redirect_uri = f"{base_url}/google_login/callback"
    
    # Prepare the token request
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=redirect_uri,
        code=code,
    )
    
    # Send the token request
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
    
    # Verify the user email
    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        return "Email not verified by Google", 400
        
    # Get user info
    email = userinfo["email"]
    name = userinfo.get("given_name", email.split("@")[0])
    
    # Find or create the user in our database
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create a new user
        user = User(
            username=name,
            email=email
        )
        db.session.add(user)
        db.session.commit()
    
    # Log in the user
    login_user(user)
    
    # Redirect to the index page
    return redirect(url_for("index.index"))


@google_auth.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("index.index"))


def init_app(app):
    """Register the blueprint with the app."""
    app.register_blueprint(google_auth, url_prefix='/auth')
    
    # Print information for developers during startup
    print("""
To make Google authentication work:
1. Ensure you have a client_secret.json file from Google Cloud Console
2. Make sure the redirect URI is added in Google Cloud Console:
   - {your-domain}/google_login/callback
""")