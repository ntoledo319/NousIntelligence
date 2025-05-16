"""
Direct implementation of Google OAuth that fixes the redirect issue.
"""
import os
import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Blueprint, redirect, request, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from models import User, db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OAuth configuration
try:
    with open('client_secret.json', 'r') as f:
        client_config = json.load(f)['web']
    client_id = client_config['client_id']
    client_secret = client_config['client_secret']
    redirect_uri = "https://mynous.replit.app/callback/google"
    logger.info(f"Using redirect URI: {redirect_uri}")
except Exception as e:
    logger.error(f"Could not load client_secret.json: {e}")
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "")

# OAuth endpoints
auth_endpoint = "https://accounts.google.com/o/oauth2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"

# Create blueprint
google_auth = Blueprint('google_auth', __name__)

@google_auth.route('/login')
def login():
    """Start the OAuth flow with direct approach."""
    # Log current domain for debugging
    logger.info(f"Current domain: {request.host}")
    
    # Create the OAuth URL directly
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'select_account'
    }
    
    # Convert params to URL query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{auth_endpoint}?{query_string}"
    
    logger.info(f"Auth URL: {auth_url}")
    return redirect(auth_url)

@google_auth.route('/callback/google')
def callback():
    """Handle the OAuth callback."""
    # Get the authorization code
    code = request.args.get('code')
    if not code:
        logger.error("No authorization code received")
        flash("Authentication failed. Please try again.", "error")
        return redirect(url_for('index'))
    
    try:
        # Exchange code for token
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_endpoint, data=token_data)
        token_json = token_response.json()
        
        if 'error' in token_json:
            logger.error(f"Token error: {token_json}")
            flash("Authentication failed. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Get user info using the access token
        access_token = token_json.get('access_token')
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        userinfo = userinfo_response.json()
        
        # Extract user data
        email = userinfo.get('email')
        name = userinfo.get('given_name', 'User')
        
        if not email:
            logger.error("No email in user info")
            flash("Could not get email from Google. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
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
        session['access_token'] = access_token
        
        flash(f"Welcome, {name}!", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        flash("Authentication error. Please try again.", "error")
        return redirect(url_for('index'))

@google_auth.route('/logout')
@login_required
def logout():
    """Log the user out."""
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))