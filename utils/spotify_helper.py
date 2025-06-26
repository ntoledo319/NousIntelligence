"""
Spotify Helper

This module provides helper functions for working with the Spotify API.
It handles authentication, client creation, and basic API operations.

@module utils.spotify_helper
@description Helper functions for Spotify API integration
"""

import os
import logging
import base64
import requests
import json
from time import time
from flask import session, redirect, url_for, request

logger = logging.getLogger(__name__)

def get_spotify_client(session=None, client_id=None, client_secret=None, redirect_uri=None, user_id=None):
    """
    Get an authenticated Spotify client

    Args:
        session: Flask session object
        client_id: Spotify API client ID (or from env vars)
        client_secret: Spotify API client secret (or from env vars)
        redirect_uri: OAuth redirect URI (or from env vars)
        user_id: Optional user ID for database storage

    Returns:
        tuple: (spotify_client, spotify_auth) or (None, None) if not authenticated
    """
    # Ensure credentials are set
    client_id = client_id or os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = client_secret or os.environ.get('SPOTIFY_CLIENT_SECRET')
    redirect_uri = redirect_uri or os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8080/callback')

    if not client_id or not client_secret:
        logger.warning('Spotify credentials not found')
        return None, None

    # Create a SpotifyClient instance
    from utils.spotify_client import SpotifyClient
    spotify_client = SpotifyClient(client_id, client_secret, redirect_uri)

    # Check if we have stored auth
    if session and 'spotify_token_info' in session:
        token_info = session['spotify_token_info']

        # Check if token is expired
        now = int(time())
        is_expired = token_info.get('expires_at', 0) - now < 60

        if is_expired:
            # Try to refresh token
            try:
                token_info = refresh_spotify_token(spotify_client, token_info.get('refresh_token'))
                session['spotify_token_info'] = token_info
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return None, None

        # Set access token on client
        spotify_client.set_access_token(token_info.get('access_token'))
        return spotify_client, token_info

    # No auth found
    return None, None

def refresh_spotify_token(spotify_client, refresh_token):
    """
    Refresh an expired Spotify access token

    Args:
        spotify_client: SpotifyClient instance
        refresh_token: The refresh token to use

    Returns:
        dict: New token info
    """
    if not refresh_token:
        raise ValueError("No refresh token available")

    auth_header = base64.b64encode(
        f"{spotify_client.client_id}:{spotify_client.client_secret}".encode()
    ).decode()

    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=payload
    )

    if response.status_code != 200:
        logger.error(f"Token refresh failed: {response.text}")
        raise Exception(f"Token refresh failed: {response.status_code}")

    token_info = response.json()

    # Calculate expiration time
    token_info['expires_at'] = int(time()) + token_info.get('expires_in', 3600)

    # Keep the refresh token if not provided
    if 'refresh_token' not in token_info:
        token_info['refresh_token'] = refresh_token

    return token_info

def get_auth_url(spotify_client, state=None, scope=None):
    """
    Get the Spotify authorization URL

    Args:
        spotify_client: SpotifyClient instance
        state: Optional state parameter for security
        scope: Optional scopes to request

    Returns:
        str: Authorization URL
    """
    if scope is None:
        scope = [
            'user-read-private',
            'user-read-email',
            'user-top-read',
            'user-read-recently-played',
            'user-library-read',
            'playlist-read-private',
            'playlist-modify-public',
            'playlist-modify-private'
        ]

    return spotify_client.get_authorize_url(scope, state)

def handle_oauth_callback(spotify_client, session):
    """
    Handle the OAuth callback from Spotify

    Args:
        spotify_client: SpotifyClient instance
        session: Flask session object

    Returns:
        tuple: (success, message)
    """
    try:
        code = request.args.get('code')
        state = request.args.get('state')

        # Check for error or missing code
        if 'error' in request.args:
            return False, f"Authorization failed: {request.args.get('error')}"

        if not code:
            return False, "Authorization code missing"

        # Exchange code for token
        token_info = spotify_client.exchange_code(code)

        # Calculate expiration time
        token_info['expires_at'] = int(time()) + token_info.get('expires_in', 3600)

        # Store in session
        session['spotify_token_info'] = token_info

        # Set access token on client
        spotify_client.set_access_token(token_info.get('access_token'))

        return True, "Successfully authenticated with Spotify"

    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        return False, f"Error processing Spotify callback: {str(e)}"

def save_token_to_db(user_id, token_info):
    """
    Save Spotify token information to the database for a user

    Args:
        user_id: User ID to associate with the token
        token_info: Token information to save

    Returns:
        bool: Success status
    """
    try:
        from models import db, SpotifyToken

        # Check if token already exists
        existing = SpotifyToken.query.filter_by(user_id=user_id).first()

        if existing:
            # Update existing token
            existing.access_token = token_info.get('access_token')
            existing.refresh_token = token_info.get('refresh_token')
            existing.expires_at = token_info.get('expires_at')
            existing.scope = token_info.get('scope')
        else:
            # Create new token record
            token = SpotifyToken(
                user_id=user_id,
                access_token=token_info.get('access_token'),
                refresh_token=token_info.get('refresh_token'),
                expires_at=token_info.get('expires_at'),
                scope=token_info.get('scope')
            )
            db.session.add(token)

        db.session.commit()
        return True

    except Exception as e:
        logger.error(f"Error saving token to database: {str(e)}")
        return False

def load_token_from_db(user_id):
    """
    Load Spotify token information from the database

    Args:
        user_id: User ID to retrieve token for

    Returns:
        dict: Token information or None
    """
    try:
        from models import SpotifyToken

        token = SpotifyToken.query.filter_by(user_id=user_id).first()

        if not token:
            return None

        return {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token,
            'expires_at': token.expires_at,
            'scope': token.scope
        }

    except Exception as e:
        logger.error(f"Error loading token from database: {str(e)}")
        return None
