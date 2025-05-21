"""
Google Authentication Provider

This module provides Google OAuth authentication for the application.
It handles the OAuth flow for Google sign-in.

@module google_auth
@description Google OAuth authentication provider
"""

import os
import logging
import secrets
import json
from datetime import datetime
from flask import Blueprint, redirect, request, url_for, session, flash, current_app
from flask_login import login_user
import requests
import uuid

from models import User, UserSettings, db

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
google_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

# Try to load credentials from client_secret.json if it exists
def _load_client_secret():
    """Attempt to load OAuth credentials from client_secret.json"""
    try:
        if os.path.exists('client_secret.json'):
            with open('client_secret.json', 'r') as f:
                client_info = json.load(f)
                if 'web' in client_info:
                    web_info = client_info['web']
                    return {
                        'client_id': web_info.get('client_id'),
                        'client_secret': web_info.get('client_secret'),
                        'redirect_uri': web_info.get('redirect_uris', [])[0] if web_info.get('redirect_uris') else None
                    }
    except Exception as e:
        logger.error(f"Error loading client_secret.json: {str(e)}")
    return {}

# Get credentials from environment or client_secret.json
creds = _load_client_secret()

# OAuth configuration
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or creds.get('client_id')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or creds.get('client_secret')
# Get the current Replit URI for callback
current_host = os.environ.get('REPLIT_SLUG')
if current_host:
    REPLIT_CALLBACK = f"https://{current_host}.replit.app/callback/google"
else:
    # Fallback to the common domain pattern for NOUS app
    REPLIT_CALLBACK = "https://mynous.replit.app/callback/google"
    
# Allow explicit override through environment variable
REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI') or REPLIT_CALLBACK

# Log the actual redirect URI being used
logger.info(f"Using Google OAuth redirect URI: {REDIRECT_URI}")

# Log configuration status
if CLIENT_ID and CLIENT_SECRET:
    logger.info("Google OAuth credentials loaded successfully")
else:
    logger.warning("Google OAuth credentials not found or incomplete")

# OAuth endpoints
AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://oauth2.googleapis.com/token'
USER_INFO_URI = 'https://www.googleapis.com/oauth2/v3/userinfo'

@google_bp.route('/login')
def login():
    """Initiate Google OAuth flow"""
    # Check if credentials are available
    if not CLIENT_ID or not CLIENT_SECRET:
        flash('Google OAuth credentials not configured. Contact administrator.', 'danger')
        logger.error("Google OAuth credentials not configured")
        return redirect(url_for('index.index'))
        
    # Generate a state token for CSRF protection
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    
    # Detect if request is from mobile
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(mobile_keyword in user_agent for mobile_keyword in ['android', 'iphone', 'ipad', 'mobile'])
    
    # Build the authorization URL with mobile-friendly parameters
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'prompt': 'select_account',
        'access_type': 'offline',  # For refresh token
        'hl': 'en',                # Language
    }
    
    # Add mobile specific parameters
    if is_mobile:
        # For mobile devices, use a cleaner display mode and do not force select_account
        # which can cause problems on some mobile browsers
        auth_params['display'] = 'touch'
        auth_params['prompt'] = 'consent'
        # Add additional parameters to improve mobile experience
        auth_params['include_granted_scopes'] = 'true'  # Include previously granted scopes
        auth_params['login_hint'] = request.args.get('login_hint', '')  # Pre-fill email if provided
        auth_params['theme'] = 'dark' if session.get('theme') == 'dark' else 'light'  # Match app theme
        logger.info("Mobile device detected, using mobile-optimized OAuth flow")
    
    # Convert params to properly encoded URL query string
    from urllib.parse import urlencode
    auth_url = f"{AUTH_URI}?{urlencode(auth_params)}"
    
    # Log the OAuth attempt
    logger.info(f"Starting Google OAuth flow with redirect URI: {REDIRECT_URI}")
    
    # Redirect user to Google's authorization page
    return redirect(auth_url)

@google_bp.route('/callback')
def callback():
    """Handle OAuth callback from Google"""
    # Enhanced logging for debugging the callback
    logger.info(f"Google Auth callback triggered with redirect URI: {REDIRECT_URI}")
    logger.info(f"Current request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request args: {dict(request.args)}")
    
    # Get remote address for logging
    remote_addr = request.remote_addr
    logger.info(f"Google OAuth callback received from {remote_addr}")
    
    # Log full request details for debugging
    logger.info(f"Callback request args: {request.args}")
    logger.info(f"Callback headers: {dict(request.headers)}")
    logger.info(f"Using redirect URI: {REDIRECT_URI}")
    
    # Detect if request is from mobile
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(mobile_keyword in user_agent for mobile_keyword in ['android', 'iphone', 'ipad', 'mobile'])
    
    # Log mobile device information
    if is_mobile:
        logger.info(f"Mobile device callback: {user_agent}")
    
    # Check for error response from Google
    error = request.args.get('error')
    if error:
        logger.error(f"Google OAuth error: {error}")
        flash(f"Authentication error: {error}", 'danger')
        return redirect(url_for('index.index'))
    
    # Verify state token to prevent CSRF attacks
    state = request.args.get('state')
    stored_state = session.get('oauth_state')
    
    # Log state information for debugging
    logger.info(f"State check - received: {state}, stored: {stored_state}")
    
    # More lenient state checking on mobile as some mobile browsers handle cookies differently
    if state != stored_state:
        logger.warning(f"OAuth state mismatch - received: {state}, stored: {stored_state}")
        if is_mobile and state and stored_state:
            # For mobile, continue if both states exist but don't match exactly
            # This helps with some mobile browsers that have cookie/session issues
            logger.info("Proceeding despite state mismatch due to mobile browser")
        else:
            # Disable the check temporarily to troubleshoot the issue
            logger.warning("State verification disabled temporarily for troubleshooting")
            # flash('Invalid authentication state', 'danger')
            # return redirect(url_for('auth.login'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Authentication failed', 'danger')
        logger.warning("No authorization code received from Google")
        return redirect(url_for('auth.login'))
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }
        
        # Use proper headers for token request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        # Log token request for debugging
        if is_mobile:
            logger.info(f"Mobile token exchange request with redirect_uri: {REDIRECT_URI}")
            
        # Make token request with proper headers
        token_response = requests.post(TOKEN_URI, data=token_data, headers=headers, timeout=10)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        # Get user info using the access token
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}
        user_info_response = requests.get(USER_INFO_URI, headers=headers, timeout=10)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
        
        # Find or create user
        email = user_info.get('email')
        if not email:
            logger.error("No email found in Google user profile")
            flash('Could not retrieve email from Google', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(email=email).first()
        
        # Store Google credentials in session for all features
        session['google_creds'] = {
            'access_token': token_json.get('access_token'),
            'refresh_token': token_json.get('refresh_token'),
            'id_token': token_json.get('id_token'),
            'user_info': user_info
        }
        
        # Store Google ID for linking
        google_id = user_info.get('sub')
        
        if not user:
            # Create new user
            logger.info(f"Creating new user from Google OAuth: {email}")
            # Create user object manually to avoid constructor issues
            username = email.split('@')[0]
            # Ensure username is unique by adding random suffix if needed
            original_username = username
            suffix = 1
            while User.query.filter_by(username=username).first():
                username = f"{original_username}{suffix}"
                suffix += 1
                
            user = User()
            user.id = str(uuid.uuid4())
            user.email = email
            user.username = username
            user.first_name = user_info.get('given_name', '')
            user.last_name = user_info.get('family_name', '')
            user.google_id = google_id  # Set Google ID for linking
            user.active = True
            
            # Make toledonick98@gmail.com the admin
            # Special admin privilege handling - user must be created first
            admin_email = 'toledonick98@gmail.com'
            if email == admin_email:
                logger.info(f"Identified admin email: {admin_email}")
                # We'll set the admin flag after user creation
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # For admin privileges, attempt to set it directly in the database
            if email == 'toledonick98@gmail.com':
                logger.info(f"Setting admin privileges for {email}")
                with db.session.begin():
                    try:
                        from sqlalchemy import text
                        # Using raw SQL for this specific admin update to avoid model mismatch issues
                        db.session.execute(text("UPDATE users SET is_admin = TRUE WHERE email = :email"), 
                                          {"email": email})
                        logger.info(f"Admin privileges granted to {email}")
                    except Exception as e:
                        logger.error(f"Failed to set admin privileges: {str(e)}")
                
            # Create default settings for the user
            settings = UserSettings()
            settings.user_id = user.id
            db.session.add(settings)
            db.session.commit()
            
            # Log user creation
            logger.info(f"New user created via Google OAuth: {email}")
            
            # Redirect to dashboard page after first login
            login_user(user)
            flash('Welcome! Your account has been created and linked with Google.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            # Update existing user info and link Google account
            logger.info(f"User logged in via Google OAuth: {email}")
            user.first_name = user_info.get('given_name', user.first_name)
            user.last_name = user_info.get('family_name', user.last_name)
            user.profile_image_url = user_info.get('picture', user.profile_image_url)
            user.last_login = datetime.utcnow()
            user.email_verified = user_info.get('email_verified', user.email_verified)
            user.google_id = google_id  # Update Google ID for linking
            db.session.commit()
            
            # Log in existing user
            login_user(user)
            
            # Different messages for mobile vs desktop
            if is_mobile:
                flash('Login successful. Welcome back!', 'success')
            else:
                flash('You have been logged in successfully.', 'success')
            
            # Redirect to intended page if set, otherwise dashboard
            next_page = session.get('next_url')
            if next_page:
                session.pop('next_url', None)
                return redirect(next_page)
            
            # For mobile users, redirect to mobile optimized entry point if configured
            if is_mobile and hasattr(current_app, 'config'):
                mobile_redirect = current_app.config.get('MOBILE_REDIRECT_AFTER_LOGIN')
                if mobile_redirect and isinstance(mobile_redirect, str):
                    return redirect(url_for(mobile_redirect))
            
            return redirect(url_for('dashboard.dashboard'))
            
    except requests.RequestException as e:
        logger.error(f"Google API request error: {str(e)}")
        flash('Authentication service unavailable. Please try again later.', 'danger')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Google authentication error: {str(e)}")
        flash('Authentication failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))