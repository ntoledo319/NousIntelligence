import json
import os

import requests
from flask import Blueprint, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from models import User, db

# Configure Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize Google OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for Google authentication
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login/google")
def login():
    """Start Google OAuth flow"""
    # Get Google's OAuth 2.0 provider configuration
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Create the redirect URI to Google's OAuth 2.0 server
    redirect_uri = request.base_url.replace("http://", "https://") + "/callback"
    
    # Use the library to create an authorization URL
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    
    # Redirect to Google's OAuth 2.0 server
    return redirect(request_uri)

@google_auth.route("/login/google/callback")
def callback():
    """Handle Google OAuth callback"""
    # Get the authorization code from the callback
    code = request.args.get("code")
    
    # Get Google's OAuth 2.0 provider configuration
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Use the authorization code to request an access token
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code
    )
    
    # Request the token using the client ID and client secret
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    
    # Parse the token response
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    # Now that we have a token, retrieve the user's profile
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    # Verify the user's email is verified by Google
    if userinfo_response.json().get("email_verified"):
        user_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        user_name = userinfo_response.json().get("given_name", "User")
        user_picture = userinfo_response.json().get("picture", None)
    else:
        flash("Email not verified by Google", "danger")
        return redirect(url_for("index"))
    
    # Create or update the user in the database
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        # Create new user
        user = User(
            id=user_id,
            email=user_email,
            first_name=user_name,
            profile_image_url=user_picture
        )
        db.session.add(user)
    else:
        # Update existing user
        user.email = user_email
        user.first_name = user_name
        user.profile_image_url = user_picture
    
    db.session.commit()
    
    # Log in the user
    login_user(user)
    
    # Store OAuth token in the session for API connections
    # (this is separate from user login)
    access_token = token_response.json().get('access_token')
    if access_token:
        from utils.auth_helper import save_google_credentials
        from google.oauth2.credentials import Credentials
        
        # Create credentials object for Google APIs
        creds = Credentials(
            token=access_token,
            refresh_token=token_response.json().get('refresh_token'),
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/calendar.events",
                    "https://www.googleapis.com/auth/tasks",
                    "https://www.googleapis.com/auth/keep"]
        )
        
        # Save to database
        save_google_credentials(user.id, creds)
        
        # Also save to session for current browser session
        creds_dict = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'token_uri': creds.token_uri
        }
        session['google_creds'] = creds_dict
        
        flash("Google account connected successfully!", "success")
    else:
        flash("You've logged in, but we couldn't connect to Google services", "warning")

    # Redirect user to home page
    return redirect(url_for("index"))