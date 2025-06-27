import json
import datetime
import logging
from google.oauth2.credentials import Credentials
from models import db, UserConnection

def get_user_connection(user_id, service):
    """Get a user's connection to a service from the database"""
    return UserConnection.query.filter_by(user_id=user_id, service=service).first()

def save_google_credentials(user_id, creds):
    """Save Google credentials to the database"""
    connection = get_user_connection(user_id, 'google')

    # Convert scopes to a JSON string
    scopes_json = json.dumps(list(creds.scopes)) if creds.scopes else None

    if connection:
        # Update existing connection
        connection.token = creds.token
        if creds.refresh_token:  # Only update if provided (might be None on refresh)
            connection.refresh_token = creds.refresh_token
        connection.token_uri = creds.token_uri
        connection.client_id = creds.client_id
        connection.client_secret = creds.client_secret
        connection.scopes = scopes_json
        if hasattr(creds, 'expiry'):
            connection.expires_at = creds.expiry
    else:
        # Create new connection
        connection = UserConnection(
            user_id=user_id,
            service='google',
            token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=scopes_json,
            expires_at=creds.expiry if hasattr(creds, 'expiry') else None
        )
        db.session.add(connection)

    db.session.commit()
    return connection

def get_google_credentials(user_id):
    """Get Google credentials from the database"""
    connection = get_user_connection(user_id, 'google')
    if not connection:
        return None

    # Parse scopes from JSON
    scopes = json.loads(connection.scopes) if connection.scopes else []

    # Create credentials object
    return Credentials(
        token=connection.token,
        refresh_token=connection.refresh_token,
        token_uri=connection.token_uri,
        client_id=connection.client_id,
        client_secret=connection.client_secret,
        scopes=scopes
    )

def save_spotify_token(user_id, token_info):
    """Save Spotify token to the database"""
    connection = get_user_connection(user_id, 'spotify')

    # Calculate expires_at
    expires_at = None
    if 'expires_in' in token_info:
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=token_info['expires_in'])

    if connection:
        # Update existing connection
        connection.token = token_info.get('access_token', '')
        connection.refresh_token = token_info.get('refresh_token', '')
        connection.scopes = token_info.get('scope', '')
        connection.expires_at = expires_at
    else:
        # Create new connection
        connection = UserConnection(
            user_id=user_id,
            service='spotify',
            token=token_info.get('access_token', ''),
            refresh_token=token_info.get('refresh_token', ''),
            scopes=token_info.get('scope', ''),
            expires_at=expires_at
        )
        db.session.add(connection)

    db.session.commit()
    return connection

def get_spotify_token(user_id):
    """Get Spotify token from the database"""
    connection = get_user_connection(user_id, 'spotify')
    if not connection:
        return None

    # Convert to token_info format for compatibility with existing code
    token_info = {
        'access_token': connection.token,
        'refresh_token': connection.refresh_token,
        'scope': connection.scopes
    }

    # Add expires_in if we have an expiry
    if connection.expires_at:
        seconds_left = (connection.expires_at - datetime.datetime.now()).total_seconds()
        token_info['expires_in'] = int(max(0, seconds_left))

    return token_info