"""
Spotify Client

This module provides a custom Spotify API client implementation.
It handles authentication and provides methods for interacting with the Spotify API.

@module utils.spotify_client
@description Custom Spotify API client implementation
"""

import os
import logging
import requests
import base64
import json
import urllib.parse
from time import time

logger = logging.getLogger(__name__)

class SpotifyClient:
    """
    Custom Spotify API client

    This class provides methods for authenticating with the Spotify API
    and making requests to various Spotify API endpoints.
    """

    def __init__(self, client_id, client_secret, redirect_uri):
        """
        Initialize the Spotify client

        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.token_expiry = 0
        self.api_base_url = "https://api.spotify.com/v1"

    def is_authenticated(self):
        """
        Check if the client is authenticated with a valid token

        Returns:
            bool: Whether the client has a valid token
        """
        return self.access_token is not None and time() < self.token_expiry

    def set_access_token(self, access_token, expires_in=3600):
        """
        Set the access token manually

        Args:
            access_token: The Spotify access token
            expires_in: Token expiry time in seconds
        """
        self.access_token = access_token
        self.token_expiry = time() + expires_in

    def get_authorize_url(self, scope=None, state=None):
        """
        Get the Spotify authorization URL

        Args:
            scope: List of permission scopes to request
            state: Optional state parameter for security

        Returns:
            str: Authorization URL
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
        }

        if scope:
            if isinstance(scope, list):
                params['scope'] = ' '.join(scope)
            else:
                params['scope'] = scope

        if state:
            params['state'] = state

        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.spotify.com/authorize?{query_string}"

    def exchange_code(self, code):
        """
        Exchange an authorization code for an access token

        Args:
            code: The authorization code from Spotify

        Returns:
            dict: Token information
        """
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=payload
        )

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise Exception(f"Token exchange failed: {response.status_code}")

        token_info = response.json()
        self.access_token = token_info.get('access_token')
        self.token_expiry = time() + token_info.get('expires_in', 3600)

        return token_info

    def _make_api_request(self, method, endpoint, params=None, data=None):
        """
        Make a request to the Spotify API

        Args:
            method: HTTP method to use
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            data: Request body data

        Returns:
            dict: API response
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated with Spotify")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        url = f"{self.api_base_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, params=params, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle common error responses
            if response.status_code == 401:
                # Token expired or invalid
                raise Exception("Spotify authentication error")
            elif response.status_code == 429:
                # Rate limiting
                retry_after = int(response.headers.get('Retry-After', 1))
                raise Exception(f"Spotify rate limit exceeded. Retry after {retry_after} seconds")
            elif response.status_code >= 400:
                # Other errors
                error_msg = response.text
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        if isinstance(error_data['error'], dict) and 'message' in error_data['error']:
                            error_msg = error_data['error']['message']
                        else:
                            error_msg = str(error_data['error'])
                except:
                    pass
                raise Exception(f"Spotify API error: {error_msg}")

            # Parse response
            if response.text:
                return response.json()
            return {}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")

    # User profile methods
    def current_user(self):
        """
        Get information about the current user

        Returns:
            dict: User information
        """
        return self._make_api_request('GET', '/me')

    def current_user_playlists(self, limit=50, offset=0):
        """
        Get the current user's playlists

        Args:
            limit: Maximum number of playlists to return
            offset: Offset for pagination

        Returns:
            dict: User's playlists
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_api_request('GET', '/me/playlists', params=params)

    def current_user_top_tracks(self, limit=20, offset=0, time_range='medium_term'):
        """
        Get the user's top tracks

        Args:
            limit: Maximum number of tracks to return
            offset: Offset for pagination
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), or 'long_term' (years)

        Returns:
            dict: User's top tracks
        """
        params = {
            'limit': limit,
            'offset': offset,
            'time_range': time_range
        }
        return self._make_api_request('GET', '/me/top/tracks', params=params)

    def current_user_top_artists(self, limit=20, offset=0, time_range='medium_term'):
        """
        Get the user's top artists

        Args:
            limit: Maximum number of artists to return
            offset: Offset for pagination
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), or 'long_term' (years)

        Returns:
            dict: User's top artists
        """
        params = {
            'limit': limit,
            'offset': offset,
            'time_range': time_range
        }
        return self._make_api_request('GET', '/me/top/artists', params=params)

    def current_user_recently_played(self, limit=50, after=None, before=None):
        """
        Get the user's recently played tracks

        Args:
            limit: Maximum number of tracks to return
            after: Return items after this timestamp (Unix timestamp in ms)
            before: Return items before this timestamp (Unix timestamp in ms)

        Returns:
            dict: Recently played tracks
        """
        params = {'limit': limit}
        if after:
            params['after'] = after
        if before:
            params['before'] = before

        return self._make_api_request('GET', '/me/player/recently-played', params=params)

    def current_user_saved_tracks(self, limit=50, offset=0):
        """
        Get the user's saved tracks

        Args:
            limit: Maximum number of tracks to return
            offset: Offset for pagination

        Returns:
            dict: Saved tracks
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_api_request('GET', '/me/tracks', params=params)

    def current_user_saved_albums(self, limit=50, offset=0):
        """
        Get the user's saved albums

        Args:
            limit: Maximum number of albums to return
            offset: Offset for pagination

        Returns:
            dict: Saved albums
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_api_request('GET', '/me/albums', params=params)

    def current_user_followed_artists(self, limit=50, after=None):
        """
        Get the user's followed artists

        Args:
            limit: Maximum number of artists to return
            after: ID of the last artist from previous request

        Returns:
            dict: Followed artists
        """
        params = {
            'type': 'artist',
            'limit': limit
        }
        if after:
            params['after'] = after

        return self._make_api_request('GET', '/me/following', params=params)

    # Search methods
    def search(self, query, type='track', limit=20, offset=0, market=None):
        """
        Search for items on Spotify

        Args:
            query: Search query
            type: Item type to search for ('album', 'artist', 'playlist', 'track')
            limit: Maximum number of results to return
            offset: Offset for pagination
            market: Market to search in (ISO 3166-1 alpha-2 country code)

        Returns:
            dict: Search results
        """
        params = {
            'q': query,
            'type': type,
            'limit': limit,
            'offset': offset
        }
        if market:
            params['market'] = market

        return self._make_api_request('GET', '/search', params=params)

    def search_tracks(self, query, limit=20, offset=0, market=None):
        """
        Search for tracks

        Args:
            query: Search query
            limit: Maximum number of results to return
            offset: Offset for pagination
            market: Market to search in (ISO 3166-1 alpha-2 country code)

        Returns:
            list: Tracks
        """
        results = self.search(query, type='track', limit=limit, offset=offset, market=market)
        return results.get('tracks', {}).get('items', [])

    def search_artists(self, query, limit=20, offset=0, market=None):
        """
        Search for artists

        Args:
            query: Search query
            limit: Maximum number of results to return
            offset: Offset for pagination
            market: Market to search in (ISO 3166-1 alpha-2 country code)

        Returns:
            list: Artists
        """
        results = self.search(query, type='artist', limit=limit, offset=offset, market=market)
        return results.get('artists', {}).get('items', [])

    def search_albums(self, query, limit=20, offset=0, market=None):
        """
        Search for albums

        Args:
            query: Search query
            limit: Maximum number of results to return
            offset: Offset for pagination
            market: Market to search in (ISO 3166-1 alpha-2 country code)

        Returns:
            list: Albums
        """
        results = self.search(query, type='album', limit=limit, offset=offset, market=market)
        return results.get('albums', {}).get('items', [])

    def search_playlists(self, query, limit=20, offset=0, market=None):
        """
        Search for playlists

        Args:
            query: Search query
            limit: Maximum number of results to return
            offset: Offset for pagination
            market: Market to search in (ISO 3166-1 alpha-2 country code)

        Returns:
            list: Playlists
        """
        results = self.search(query, type='playlist', limit=limit, offset=offset, market=market)
        return results.get('playlists', {}).get('items', [])

    # Playlist methods
    def user_playlist_create(self, user_id, name, public=True, description=None):
        """
        Create a new playlist

        Args:
            user_id: ID of the user
            name: Name of the playlist
            public: Whether the playlist should be public
            description: Description of the playlist

        Returns:
            dict: Created playlist
        """
        data = {
            'name': name,
            'public': public
        }
        if description:
            data['description'] = description

        return self._make_api_request('POST', f'/users/{user_id}/playlists', data=data)

    def user_playlist_add_tracks(self, user_id, playlist_id, tracks, position=None):
        """
        Add tracks to a playlist

        Args:
            user_id: ID of the user
            playlist_id: ID of the playlist
            tracks: List of track URIs
            position: Position to insert tracks

        Returns:
            dict: API response
        """
        data = {'uris': tracks}
        if position is not None:
            data['position'] = position

        return self._make_api_request('POST', f'/playlists/{playlist_id}/tracks', data=data)

    def playlist_add_items(self, playlist_id, items, position=None):
        """
        Add items to a playlist

        Args:
            playlist_id: ID of the playlist
            items: List of track URIs
            position: Position to insert tracks

        Returns:
            dict: API response
        """
        data = {'uris': items}
        if position is not None:
            data['position'] = position

        return self._make_api_request('POST', f'/playlists/{playlist_id}/tracks', data=data)

    # Track methods
    def track(self, track_id, market=None):
        """
        Get information about a track

        Args:
            track_id: ID of the track
            market: Market to get track from

        Returns:
            dict: Track information
        """
        params = {}
        if market:
            params['market'] = market

        return self._make_api_request('GET', f'/tracks/{track_id}', params=params)

    def audio_features(self, track_ids):
        """
        Get audio features for tracks

        Args:
            track_ids: List of track IDs or single track ID

        Returns:
            list or dict: Audio features
        """
        if isinstance(track_ids, list):
            # Multiple tracks
            if len(track_ids) > 100:
                # Spotify API limit is 100 tracks per request
                track_ids = track_ids[:100]

            params = {'ids': ','.join(track_ids)}
            results = self._make_api_request('GET', '/audio-features', params=params)
            return results.get('audio_features', [])
        else:
            # Single track
            return self._make_api_request('GET', f'/audio-features/{track_ids}')

    # Artist methods
    def artist(self, artist_id):
        """
        Get information about an artist

        Args:
            artist_id: ID of the artist

        Returns:
            dict: Artist information
        """
        return self._make_api_request('GET', f'/artists/{artist_id}')

    def artist_top_tracks(self, artist_id, country='US'):
        """
        Get an artist's top tracks

        Args:
            artist_id: ID of the artist
            country: Country to get top tracks for (ISO 3166-1 alpha-2 country code)

        Returns:
            dict: Top tracks
        """
        params = {'country': country}
        return self._make_api_request('GET', f'/artists/{artist_id}/top-tracks', params=params)

    def artist_related_artists(self, artist_id):
        """
        Get artists related to an artist

        Args:
            artist_id: ID of the artist

        Returns:
            dict: Related artists
        """
        return self._make_api_request('GET', f'/artists/{artist_id}/related-artists')

    # Recommendations methods
    def get_available_genre_seeds(self):
        """
        Get a list of available genre seeds for recommendations

        Returns:
            list: Available genre seeds
        """
        results = self._make_api_request('GET', '/recommendations/available-genre-seeds')
        return results.get('genres', [])

    def get_recommendations(self, **kwargs):
        """
        Get track recommendations

        Args:
            kwargs: Various recommendation parameters
                - seed_artists: List of artist IDs (max 5)
                - seed_tracks: List of track IDs (max 5)
                - seed_genres: List of genre names (max 5)
                - limit: Maximum number of tracks to return
                - Various audio feature targets/minimums/maximums

        Returns:
            dict: Recommendations
        """
        params = {}

        # Handle seed parameters
        for seed_type in ['seed_artists', 'seed_tracks', 'seed_genres']:
            if seed_type in kwargs and kwargs[seed_type]:
                if isinstance(kwargs[seed_type], list):
                    params[seed_type] = ','.join(kwargs[seed_type])
                else:
                    params[seed_type] = kwargs[seed_type]

        # Add other parameters directly
        for key, value in kwargs.items():
            if key not in params and key != 'seed_artists' and key != 'seed_tracks' and key != 'seed_genres':
                params[key] = value

        return self._make_api_request('GET', '/recommendations', params=params)

    # Playback methods
    def current_playback(self):
        """
        Get information about the user's current playback

        Returns:
            dict: Current playback state
        """
        return self._make_api_request('GET', '/me/player')

    def devices(self):
        """
        Get the user's available devices

        Returns:
            dict: Available devices
        """
        return self._make_api_request('GET', '/me/player/devices')

    def start_playback(self, device_id=None, context_uri=None, uris=None, offset=None, position_ms=None):
        """
        Start playback

        Args:
            device_id: ID of the device to play on
            context_uri: URI of the context to play
            uris: List of track URIs to play
            offset: Offset into the context
            position_ms: Position to start playback from

        Returns:
            dict: API response
        """
        params = {}
        if device_id:
            params['device_id'] = device_id

        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        if uris:
            data['uris'] = uris
        if offset:
            data['offset'] = offset
        if position_ms:
            data['position_ms'] = position_ms

        return self._make_api_request('PUT', '/me/player/play', params=params, data=data)

    def pause_playback(self, device_id=None):
        """
        Pause playback

        Args:
            device_id: ID of the device to pause on

        Returns:
            dict: API response
        """
        params = {}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('PUT', '/me/player/pause', params=params)

    def next_track(self, device_id=None):
        """
        Skip to the next track

        Args:
            device_id: ID of the device to control

        Returns:
            dict: API response
        """
        params = {}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('POST', '/me/player/next', params=params)

    def previous_track(self, device_id=None):
        """
        Skip to the previous track

        Args:
            device_id: ID of the device to control

        Returns:
            dict: API response
        """
        params = {}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('POST', '/me/player/previous', params=params)

    def volume(self, volume_percent, device_id=None):
        """
        Set the volume

        Args:
            volume_percent: Volume level (0-100)
            device_id: ID of the device to control

        Returns:
            dict: API response
        """
        params = {'volume_percent': volume_percent}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('PUT', '/me/player/volume', params=params)

    def shuffle(self, state, device_id=None):
        """
        Set shuffle mode

        Args:
            state: Shuffle state (True/False)
            device_id: ID of the device to control

        Returns:
            dict: API response
        """
        params = {'state': 'true' if state else 'false'}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('PUT', '/me/player/shuffle', params=params)

    def repeat(self, state, device_id=None):
        """
        Set repeat mode

        Args:
            state: Repeat state ('track', 'context', or 'off')
            device_id: ID of the device to control

        Returns:
            dict: API response
        """
        params = {'state': state}
        if device_id:
            params['device_id'] = device_id

        return self._make_api_request('PUT', '/me/player/repeat', params=params)

    # Browse methods
    def categories(self, country=None, locale=None, limit=20, offset=0):
        """
        Get a list of categories

        Args:
            country: Country code
            locale: Locale
            limit: Maximum number of categories to return
            offset: Offset for pagination

        Returns:
            dict: Categories
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if country:
            params['country'] = country
        if locale:
            params['locale'] = locale

        return self._make_api_request('GET', '/browse/categories', params=params)

    def category_playlists(self, category_id, country=None, limit=20, offset=0):
        """
        Get a category's playlists

        Args:
            category_id: ID of the category
            country: Country code
            limit: Maximum number of playlists to return
            offset: Offset for pagination

        Returns:
            dict: Category playlists
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if country:
            params['country'] = country

        return self._make_api_request('GET', f'/browse/categories/{category_id}/playlists', params=params)

    def featured_playlists(self, country=None, locale=None, timestamp=None, limit=20, offset=0):
        """
        Get a list of featured playlists

        Args:
            country: Country code
            locale: Locale
            timestamp: Timestamp to get featured playlists for
            limit: Maximum number of playlists to return
            offset: Offset for pagination

        Returns:
            dict: Featured playlists
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if country:
            params['country'] = country
        if locale:
            params['locale'] = locale
        if timestamp:
            params['timestamp'] = timestamp

        return self._make_api_request('GET', '/browse/featured-playlists', params=params)

    def new_releases(self, country=None, limit=20, offset=0):
        """
        Get a list of new releases

        Args:
            country: Country code
            limit: Maximum number of albums to return
            offset: Offset for pagination

        Returns:
            dict: New releases
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if country:
            params['country'] = country

        return self._make_api_request('GET', '/browse/new-releases', params=params)

    def recommendations(self, seed_artists=None, seed_genres=None, seed_tracks=None, limit=20, **kwargs):
        """
        Get track recommendations

        Args:
            seed_artists: List of artist IDs
            seed_genres: List of genre names
            seed_tracks: List of track IDs
            limit: Maximum number of tracks to return
            kwargs: Additional audio feature parameters

        Returns:
            dict: Recommendations
        """
        return self.get_recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            limit=limit,
            **kwargs
        )