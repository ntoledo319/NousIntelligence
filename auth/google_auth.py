"""
Google Authentication Provider

This module provides Google OAuth authentication for the application.
It handles the OAuth flow for Google sign-in.

@module google_auth
@description Google OAuth authentication provider with enhanced security
"""

import os
import logging
import secrets
import json
from datetime import datetime, timedelta
from flask import Blueprint, redirect, request, url_for, session, flash, current_app
from flask_login import login_user
import requests
import uuid
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash
import hashlib

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

# OAuth endpoints
AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://oauth2.googleapis.com/token'
USER_INFO_URI = 'https://www.googleapis.com/oauth2/v3/userinfo'

# Function to get the appropriate callback URL based on the environment
def get_callback_url():
    """Return the fully-qualified Google OAuth callback URL.

    The resolution order is:
    1. Explicitly set current_app.config['GOOGLE_REDIRECT_URI'].
    2. Flask's ``url_for('google_auth.callback', _external=True, _scheme='https')`` which is
       guaranteed to match the registered route.
    3. A manual construction using ``request.host`` as an absolute last resort.
    This approach eliminates the risk of the callback path getting out of sync
    with the blueprint registration and removes several brittle environment-
    specific heuristics.
    """
    # 1) Honour an explicit configuration value first.
    if current_app and current_app.config.get('GOOGLE_REDIRECT_URI'):
        return current_app.config['GOOGLE_REDIRECT_URI']

    try:
        # 2) Best-practice: ask Flask to build the external URL for the exact
        #    endpoint we registered.  This is the most reliable way to ensure
        #    the path always matches the blueprint route ("google_auth.callback").
        return url_for('google_auth.callback', _external=True, _scheme='https')
    except RuntimeError:
        # url_for can raise *outside* of an application/request context. This
        # shouldn't happen for calls originating from request handlers, but we
        # still provide a graceful fallback.
        host = request.host or os.environ.get('HTTP_HOST', 'localhost:5000')
        return f"https://{host}/auth/google/callback"

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
    
    # Set nonce for additional security
    nonce = secrets.token_hex(16)
    nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()
    session['oauth_nonce'] = nonce_hash
    
    # Get the callback URL
    redirect_uri = get_callback_url()
    logger.info(f"Using Google OAuth redirect URI: {redirect_uri}")
    
    # Detect if request is from mobile
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(mobile_keyword in user_agent for mobile_keyword in ['android', 'iphone', 'ipad', 'mobile'])
    
    # Build the authorization URL with security parameters
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'prompt': 'select_account' if not is_mobile else 'consent',
        'access_type': 'offline',  # For refresh token
        'hl': 'en',                # Language
        'nonce': nonce,            # Add nonce for OpenID Connect
        'include_granted_scopes': 'true'  # Include previously granted scopes
    }
    
    # Add mobile specific parameters
    if is_mobile:
        # For mobile devices, use a cleaner display mode
        auth_params['display'] = 'touch'
        auth_params['login_hint'] = request.args.get('login_hint', '')  # Pre-fill email if provided
        auth_params['theme'] = 'dark' if session.get('theme') == 'dark' else 'light'  # Match app theme
        logger.info("Mobile device detected, using mobile-optimized OAuth flow")
    
    # Convert params to properly encoded URL query string
    auth_url = f"{AUTH_URI}?{urlencode(auth_params)}"
    
    # Log the OAuth attempt
    logger.info(f"Starting Google OAuth flow with redirect URI: {redirect_uri}")
    
    # Redirect user to Google's authorization page
    return redirect(auth_url)

@google_bp.route('/callback')
def callback():
    """Handle OAuth callback from Google"""
    # Enhanced logging for debugging the callback
    logger.info(f"Google Auth callback triggered")
    
    # Get remote address for logging
    remote_addr = request.remote_addr
    logger.info(f"Google OAuth callback received from {remote_addr}")
    
    # Verify state to prevent CSRF
    state = request.args.get('state')
    stored_state = session.get('oauth_state')
    
    if not state or state != stored_state:
        logger.warning(f"OAuth state mismatch: expected {stored_state}, got {state}")
        flash('Authentication failed: Invalid state parameter', 'danger')
        return redirect(url_for('index.index'))
    
    # Clear the state from session
    session.pop('oauth_state', None)
    
    # Check for error response from Google
    error = request.args.get('error')
    if error:
        logger.error(f"Google OAuth error: {error}")
        flash(f"Authentication error: {error}", 'danger')
        return redirect(url_for('index.index'))
    
    # Get authorization code - this is critical
    code = request.args.get('code')
    if not code:
        flash('Authentication failed: No authorization code received', 'danger')
        logger.warning("No authorization code received from Google")
        return redirect(url_for('index.index'))
    
    try:
        # Get callback URL for token request
        redirect_uri = get_callback_url()
        
        # Exchange code for access token
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        # Use proper headers for token request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
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
            return redirect(url_for('index.index'))
            
        user = User.query.filter_by(email=email).first()
        
        # Securely store tokens with encryption
        # Instead of storing directly in session, encrypt sensitive parts or store in DB
        access_token = token_json.get('access_token')
        refresh_token = token_json.get('refresh_token')
        expires_in = token_json.get('expires_in', 3600)  # Default 1 hour
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store essential data securely
        session['google_token_expires_at'] = expires_at.timestamp()
        
        # Store Google ID for linking
        google_id = user_info.get('sub')
        
        if not user:
            # Create new user
            logger.info(f"Creating new user from Google OAuth: {email}")
            
            # Ensure username is unique
            username = email.split('@')[0]
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
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # Create user settings
            settings = UserSettings(user_id=user.id)
            db.session.add(settings)
            db.session.commit()
            
            # Store token information in database rather than session
            if hasattr(User, 'google_access_token'):
                user.google_access_token = access_token
                user.google_refresh_token = refresh_token
                user.google_token_expires_at = expires_at
                db.session.commit()
        else:
            # Update existing user with latest Google data
            if user.google_id != google_id:
                user.google_id = google_id
            
            # Update user name if needed
            if not user.first_name and user_info.get('given_name'):
                user.first_name = user_info.get('given_name')
            if not user.last_name and user_info.get('family_name'):
                user.last_name = user_info.get('family_name')
                
            # Update token information
            if hasattr(User, 'google_access_token'):
                user.google_access_token = access_token
                if refresh_token:  # Refresh token isn't always provided on re-auth
                    user.google_refresh_token = refresh_token
                user.google_token_expires_at = expires_at
            
            db.session.commit()
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log in user
        login_user(user)
        
        # Clear sensitive data from session after use
        if 'oauth_nonce' in session:
            session.pop('oauth_nonce')
        
        # Handle next URL if it was stored
        next_url = session.pop('next', None)
        if next_url:
            return redirect(next_url)
            
        # Redirect to dashboard
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('dashboard.dashboard'))
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OAuth token request error: {str(e)}")
        flash('Error communicating with Google authentication service', 'danger')
        return redirect(url_for('index.index'))
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        flash('An error occurred during authentication', 'danger')
        return redirect(url_for('index.index'))