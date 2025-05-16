import json
import os
import logging

import requests
from flask import Blueprint, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient

# Load client secrets from file
try:
    with open('client_secret.json', 'r') as f:
        client_config = json.load(f)['web']
    GOOGLE_CLIENT_ID = client_config['client_id']
    GOOGLE_CLIENT_SECRET = client_config['client_secret']
    logging.info(f"Successfully loaded Google OAuth credentials from client_secret.json")
except Exception as e:
    # Fall back to environment variables if file can't be loaded
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    logging.info(f"Using Google OAuth credentials from environment variables")

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Log configuration information (without secrets)
logging.info(f"Google client ID configured: {'Yes' if GOOGLE_CLIENT_ID else 'No'}")
logging.info(f"Google client secret configured: {'Yes' if GOOGLE_CLIENT_SECRET else 'No'}")

# Initialize Google OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint for Google authentication
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/login/google")
def login():
    """Start Google OAuth flow"""
    try:
        # Get Google's OAuth 2.0 provider configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Get the redirect URIs from client_secret.json to ensure they match
        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)['web']
            registered_redirect_uris = client_config.get('redirect_uris', [])
        
        # Create the redirect URI based on the current domain
        base_url = request.url_root.rstrip('/').replace("http://", "https://")
        redirect_uri = f"{base_url}/callback/google"
        
        # Log the URIs for debugging
        logging.info(f"Current URL root: {request.url_root}")
        logging.info(f"Constructed redirect URI: {redirect_uri}")
        logging.info(f"Registered redirect URIs: {registered_redirect_uris}")
        
        # Use the library to create an authorization URL with expanded scopes
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=[
                # Basic identity scopes
                "openid", "email", "profile",
                
                # Google Calendar scopes
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
                
                # Google Tasks and Keep scopes
                "https://www.googleapis.com/auth/tasks",
                "https://www.googleapis.com/auth/keep",
                
                # Gmail scopes
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.labels",
                
                # Google Drive scopes
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.file",
                
                # Google Maps Platform scopes
                "https://www.googleapis.com/auth/maps.platform",
                
                # Google Photos scopes
                "https://www.googleapis.com/auth/photoslibrary.readonly",
                
                # Google Docs/Sheets scopes
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                
                # YouTube scopes
                "https://www.googleapis.com/auth/youtube.readonly"
            ],
        )
        
        # Log the authorization URI
        logging.info(f"Authorization URI: {request_uri}")
        
        # Redirect to Google's OAuth 2.0 server
        return redirect(request_uri)
    except Exception as e:
        logging.error(f"Error in Google login: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Unable to start Google authentication: {str(e)}", "danger")
        return redirect(url_for("index"))

@google_auth.route("/callback/google")
def callback():
    """Handle Google OAuth callback"""
    # Get the authorization code from the callback
    code = request.args.get("code")
    
    # Get Google's OAuth 2.0 provider configuration
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Use the authorization code to request an access token
    # Make sure we use the same redirect URI as registered with Google
    base_url = request.url_root.rstrip('/').replace("http://", "https://")
    redirect_uri = f"{base_url}/callback/google"
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=redirect_uri,
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
    
    # Import here to avoid circular imports
    from models import User, db
    
    # Create or update the user in the database
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        # Create new user with required fields from the User model
        user = User()
        user.id = user_id
        user.email = user_email
        user.first_name = user_name
        user.profile_image_url = user_picture
        # Make toldeonick98@gmail.com an admin automatically
        user.is_admin = (user_email == "toldeonick98@gmail.com")
        db.session.add(user)
    else:
        # Update existing user
        user.email = user_email
        user.first_name = user_name
        user.profile_image_url = user_picture
        # Make sure toldeonick98@gmail.com is always an admin
        if user_email == "toldeonick98@gmail.com" and not user.is_admin:
            user.is_admin = True
    
    db.session.commit()
    
    # Log in the user
    login_user(user)
    
    # Store OAuth token in the session for API connections
    # (this is separate from user login)
    access_token = token_response.json().get('access_token')
    if access_token:
        try:
            from utils.auth_helper import save_google_credentials
            from google.oauth2.credentials import Credentials
            
            # Create credentials object for Google APIs
            token_scopes = [
                # Google Calendar scopes
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
                
                # Google Tasks and Keep scopes
                "https://www.googleapis.com/auth/tasks",
                "https://www.googleapis.com/auth/keep",
                
                # Gmail scopes
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.labels",
                
                # Google Drive scopes
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.file",
                
                # Google Maps Platform scopes
                "https://www.googleapis.com/auth/maps.platform",
                
                # Google Photos scopes
                "https://www.googleapis.com/auth/photoslibrary.readonly",
                
                # Google Docs/Sheets scopes
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                
                # YouTube scopes
                "https://www.googleapis.com/auth/youtube.readonly"
            ]
            
            google_creds = Credentials(
                token=access_token,
                refresh_token=token_response.json().get('refresh_token'),
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=token_scopes
            )
            
            # Save to database
            save_google_credentials(user.id, google_creds)
            
            # Also save to session for current browser session
            creds_dict = {
                'token': google_creds.token,
                'refresh_token': google_creds.refresh_token,
                'client_id': google_creds.client_id,
                'client_secret': google_creds.client_secret,
                'scopes': google_creds.scopes,
                'token_uri': google_creds.token_uri
            }
            session['google_creds'] = creds_dict
            
            flash("Google account connected successfully!", "success")
        except ImportError:
            # If auth_helper isn't available, log a warning
            import logging
            logging.warning("utils.auth_helper not available, skipping credential storage")
            flash("You've logged in, but we couldn't connect to all Google services", "warning")
    else:
        flash("You've logged in, but we couldn't connect to Google services", "warning")

    # Redirect user to home page
    return redirect(url_for("index"))