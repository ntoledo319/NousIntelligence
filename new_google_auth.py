"""
Google authentication implementation using the official Google auth library.
"""
import os
import json
import secrets
import flask
from flask import Blueprint, redirect, session, url_for, request, flash
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from flask_login import login_user, current_user

# Load client config from client_secret.json
with open('client_secret.json', 'r') as f:
    client_config = json.load(f)

# Create the blueprint
google_auth = Blueprint('google_auth', __name__)

# Define SCOPES for Google authentication - only include valid scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/keep',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/maps.platform'
]

@google_auth.route('/login')
def login():
    """Start the Google OAuth login flow."""
    # Print diagnostic information
    print("===== GOOGLE AUTH DIAGNOSTIC INFO =====")
    print(f"Registered redirect URI: {client_config['web']['redirect_uris'][0]}")
    print(f"Current request URL: {request.url}")
    print(f"Current app URL root: {request.url_root}")
    print("=======================================")
    
    # Create a flow instance with client credentials and scopes
    # Use the specific domain for this app
    redirect_uri = "https://mynous.replit.app/callback/google"
    print(f"Using specific redirect URI: {redirect_uri}")
    
    # Create a modified client config with the current domain
    modified_config = dict(client_config)
    modified_config['web'] = dict(client_config['web'])
    modified_config['web']['redirect_uris'] = [redirect_uri]
    
    flow = Flow.from_client_config(
        modified_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    # Generate a secure state token for CSRF protection
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    
    # Get the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state,
        prompt='consent'
    )
    
    # Redirect to the authorization URL
    return redirect(authorization_url)

@google_auth.route('/callback/google')
def callback():
    """Handle the Google OAuth callback."""
    # Print diagnostic information
    print("===== GOOGLE AUTH CALLBACK DIAGNOSTIC INFO =====")
    print(f"Callback URL: {request.url}")
    print(f"State parameter: {request.args.get('state')}")
    print("==============================================")
    
    # Check state token for CSRF protection
    state = session.get('oauth_state')
    if not state or request.args.get('state') != state:
        flash("Authentication error: Invalid state parameter.", "danger")
        return redirect(url_for('login_page'))
    
    try:
        # Use the specific domain for this app
        redirect_uri = "https://mynous.replit.app/callback/google"
        
        # Create a modified client config with the current domain
        modified_config = dict(client_config)
        modified_config['web'] = dict(client_config['web'])
        modified_config['web']['redirect_uris'] = [redirect_uri]
        
        flow = Flow.from_client_config(
            modified_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Use the authorization response to get credentials
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Get user info from the Google API
        import requests
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        response = requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {credentials.token}"}
        )
        
        if response.status_code != 200:
            flash("Failed to get user information from Google.", "danger")
            return redirect(url_for('login_page'))
        
        # Process user info
        user_info = response.json()
        user_id = user_info['sub']
        email = user_info.get('email')
        name = user_info.get('given_name', 'User')
        picture = user_info.get('picture')
        
        # Import database models
        from models import User, db
        
        # Find or create the user
        user = User.query.filter_by(id=user_id).first()
        if not user:
            # Create a new user
            user = User()
            user.id = user_id
            user.email = email
            user.first_name = name
            user.profile_image_url = picture
            # Special case for admin user
            user.is_admin = (email == "toledonick98@gmail.com")
            db.session.add(user)
        else:
            # Update existing user info
            user.email = email
            user.first_name = name
            user.profile_image_url = picture
            if email == "toledonick98@gmail.com" and not user.is_admin:
                user.is_admin = True
                
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        # Store credentials in session for future API calls
        session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        flash(f"Welcome, {name}! You've successfully logged in with Google.", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Authentication error: {str(e)}", "danger")
        return redirect(url_for('login_page'))

@google_auth.route('/logout')
def logout():
    """Log the user out of Google."""
    # Clear the user's session
    session.clear()
    
    # Import Flask-Login logout
    from flask_login import logout_user
    logout_user()
    
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login_page'))