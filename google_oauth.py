"""
Google OAuth implementation for authentication. 
This version is streamlined to use the exact redirect URI registered in Google Cloud.
"""
import os
import json
import requests
from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient

# Configuration - loading from client_secret.json directly
with open('client_secret.json', 'r') as f:
    client_config = json.load(f)['web']

GOOGLE_CLIENT_ID = client_config['client_id']
GOOGLE_CLIENT_SECRET = client_config['client_secret']
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
# Get current domain dynamically
import os
# Use the exact URI from client_secret.json for production
REDIRECT_URI = "https://toledonick981.repl.co/callback/google"  

# Print information about domains for debugging
import logging
logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN')}")
logging.info(f"Using REDIRECT_URI: {REDIRECT_URI}")

# Initialize OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint
google_oauth = Blueprint('google_oauth', __name__)

@google_oauth.route('/login/google')
def login():
    """Start Google OAuth flow"""
    # Get Google provider configuration
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Use the exact redirect URI from client_secret.json
        print(f"Using redirect URI: {REDIRECT_URI}")
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"],
        )
        
        # Print the full authorization URI for debugging
        print(f"Authorization URI: {request_uri}")
        
        return redirect(request_uri)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error starting Google login: {str(e)}", "danger")
        return redirect(url_for('login_page'))

@google_oauth.route('/callback/google')
def callback():
    """Handle Google OAuth callback"""
    try:
        print(f"Received callback at URL: {request.url}")
        print(f"Expected redirect URI: {REDIRECT_URI}")
        
        # Get auth code
        code = request.args.get("code")
        if not code:
            flash("Authentication failed - no authorization code received", "danger")
            return redirect(url_for('login_page'))
            
        # Get token endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Exchange code for token
        token_response = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=REDIRECT_URI,
            code=code
        )
        
        token_response = requests.post(
            token_endpoint,
            headers=token_response[1],
            data=token_response[2],
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Parse token response
        client.parse_request_body_response(token_response.text)
        
        # Get user info
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        # Verify user email
        user_data = userinfo_response.json()
        if not user_data.get("email_verified"):
            flash("Google account email not verified", "danger")
            return redirect(url_for('login_page'))
        
        # Extract user info
        user_id = user_data["sub"]
        user_email = user_data["email"]
        user_name = user_data.get("given_name", "User")
        user_picture = user_data.get("picture")
        
        # Import DB models (here to avoid circular imports)
        from models import User, db
        
        # Find or create user
        user = User.query.filter_by(id=user_id).first()
        if not user:
            # Create new user
            user = User()
            user.id = user_id
            user.email = user_email
            user.first_name = user_name 
            user.profile_image_url = user_picture
            # Special case for admin user
            user.is_admin = (user_email == "toledonick98@gmail.com")
            db.session.add(user)
        else:
            # Update existing user info
            user.email = user_email
            user.first_name = user_name
            user.profile_image_url = user_picture
            if user_email == "toledonick98@gmail.com" and not user.is_admin:
                user.is_admin = True
            
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        # Store token in session
        session['google_token'] = token_response.json().get('access_token')
        
        flash("Login successful", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Authentication error: {str(e)}", "danger")
        return redirect(url_for('login_page'))

@google_oauth.route('/logout')
def logout():
    """Log user out"""
    logout_user()
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('index'))