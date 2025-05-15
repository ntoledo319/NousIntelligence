import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

def get_spotify_client(session, client_id, client_secret, redirect_uri, user_id=None):
    """Create and return a Spotify client
    
    Tries first to get token from session, then from the database if user_id is provided.
    """
    from utils.auth_helper import get_spotify_token
    
    scope = "user-modify-playback-state user-read-playback-state playlist-modify-public"
    
    try:
        if not client_id or not client_secret:
            logging.error("Missing Spotify credentials")
            return None, None
        
        # First create the auth object    
        auth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".cache-" + session.get('spotify_user', '')
        )
        
        # Try to get token_info from session cache first
        token_info = auth.get_cached_token()
        
        # If not in session cache, try the database if user_id provided
        if not token_info and user_id:
            token_info = get_spotify_token(user_id)
            if token_info:
                # Refresh token if needed
                if 'expires_in' in token_info and token_info['expires_in'] < 60:
                    token_info = auth.refresh_access_token(token_info['refresh_token'])
        
        # No valid token found
        if not token_info:
            return None, auth
            
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp, auth
    except Exception as e:
        logging.error(f"Error creating Spotify client: {str(e)}")
        return None, None

def play_track(spotify, query):
    """Search for and play a track/artist on Spotify"""
    try:
        # Check if devices are available
        devices = spotify.devices()
        if not devices or not devices.get('devices'):
            return "No active Spotify devices found. Please open Spotify on a device first."
            
        # Search for the track
        results = spotify.search(q=query, type='track', limit=1)
        if not results['tracks']['items']:
            return f"No tracks found for '{query}'"
            
        track = results['tracks']['items'][0]
        spotify.start_playback(uris=[track['uri']])
        return f"▶️ Playing '{track['name']}' by {track['artists'][0]['name']}"
    except Exception as e:
        logging.error(f"Error playing track: {str(e)}")
        return f"Error playing music: {str(e)}"

def create_playlist(spotify, name, tracks=None, description=None):
    """Create a new Spotify playlist"""
    try:
        user_info = spotify.current_user()
        user_id = user_info['id']
        
        playlist = spotify.user_playlist_create(
            user=user_id,
            name=name,
            public=True,
            description=description
        )
        
        if tracks:
            spotify.playlist_add_items(playlist['id'], tracks)
            
        return f"Created playlist '{name}' - {playlist['external_urls']['spotify']}"
    except Exception as e:
        logging.error(f"Error creating playlist: {str(e)}")
        return f"Error creating playlist: {str(e)}"
