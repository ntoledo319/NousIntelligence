import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import datetime
import random
from collections import Counter

def get_spotify_client(session, client_id, client_secret, redirect_uri, user_id=None):
    """Create and return a Spotify client
    
    Tries first to get token from session, then from the database if user_id is provided.
    """
    from utils.auth_helper import get_spotify_token
    
    # Extended scope for additional functionality
    scope = (
        "user-modify-playback-state "
        "user-read-playback-state "
        "playlist-modify-public "
        "playlist-modify-private "
        "user-read-recently-played "
        "user-top-read "
        "user-read-email "
        "user-read-private "
        "user-library-read "
        "user-library-modify "
        "user-follow-read "
        "user-follow-modify"
    )
    
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

# ---- Playback Control Functions ----

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

def play_artist(spotify, artist_name):
    """Play top tracks from an artist"""
    try:
        devices = spotify.devices()
        if not devices or not devices.get('devices'):
            return "No active Spotify devices found. Please open Spotify on a device first."

        # Search for the artist
        results = spotify.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'"
            
        artist = results['artists']['items'][0]
        
        # Get artist's top tracks
        top_tracks = spotify.artist_top_tracks(artist['id'])
        if not top_tracks['tracks']:
            return f"No tracks found for artist '{artist['name']}'"
            
        track_uris = [track['uri'] for track in top_tracks['tracks']]
        spotify.start_playback(uris=track_uris)
        
        return f"▶️ Playing top tracks from {artist['name']}"
    except Exception as e:
        logging.error(f"Error playing artist: {str(e)}")
        return f"Error playing artist music: {str(e)}"

def play_album(spotify, album_name):
    """Play an album"""
    try:
        devices = spotify.devices()
        if not devices or not devices.get('devices'):
            return "No active Spotify devices found. Please open Spotify on a device first."

        # Search for the album
        results = spotify.search(q=album_name, type='album', limit=1)
        if not results['albums']['items']:
            return f"No album found for '{album_name}'"
            
        album = results['albums']['items'][0]
        spotify.start_playback(context_uri=album['uri'])
        
        return f"▶️ Playing album '{album['name']}' by {album['artists'][0]['name']}"
    except Exception as e:
        logging.error(f"Error playing album: {str(e)}")
        return f"Error playing album: {str(e)}"

def play_playlist(spotify, playlist_name):
    """Play a playlist by searching for it"""
    try:
        devices = spotify.devices()
        if not devices or not devices.get('devices'):
            return "No active Spotify devices found. Please open Spotify on a device first."

        # Search for the playlist
        results = spotify.search(q=playlist_name, type='playlist', limit=1)
        if not results['playlists']['items']:
            return f"No playlist found for '{playlist_name}'"
            
        playlist = results['playlists']['items'][0]
        spotify.start_playback(context_uri=playlist['uri'])
        
        return f"▶️ Playing playlist '{playlist['name']}' by {playlist['owner']['display_name']}"
    except Exception as e:
        logging.error(f"Error playing playlist: {str(e)}")
        return f"Error playing playlist: {str(e)}"

def pause_playback(spotify):
    """Pause currently playing music"""
    try:
        # Check if something is currently playing
        current = spotify.current_playback()
        if not current or not current.get('is_playing'):
            return "Nothing is currently playing"
            
        spotify.pause_playback()
        return "⏸️ Playback paused"
    except Exception as e:
        logging.error(f"Error pausing playback: {str(e)}")
        return f"Error pausing music: {str(e)}"

def resume_playback(spotify):
    """Resume paused music"""
    try:
        # Check if there's a playback to resume
        current = spotify.current_playback()
        if not current:
            return "No active playback found"
            
        spotify.start_playback()
        return "▶️ Playback resumed"
    except Exception as e:
        logging.error(f"Error resuming playback: {str(e)}")
        return f"Error resuming music: {str(e)}"

def skip_track(spotify):
    """Skip to the next track"""
    try:
        spotify.next_track()
        
        # Get the new current track
        current = spotify.current_playback()
        if current and current.get('item'):
            track = current['item']
            return f"⏭️ Skipped to '{track['name']}' by {track['artists'][0]['name']}"
        else:
            return "⏭️ Skipped to next track"
    except Exception as e:
        logging.error(f"Error skipping track: {str(e)}")
        return f"Error skipping track: {str(e)}"

def previous_track(spotify):
    """Go back to the previous track"""
    try:
        spotify.previous_track()
        
        # Get the new current track
        current = spotify.current_playback()
        if current and current.get('item'):
            track = current['item']
            return f"⏮️ Went back to '{track['name']}' by {track['artists'][0]['name']}"
        else:
            return "⏮️ Went back to previous track"
    except Exception as e:
        logging.error(f"Error going to previous track: {str(e)}")
        return f"Error going to previous track: {str(e)}"

def set_volume(spotify, volume_percent):
    """Set the volume (0-100)"""
    try:
        # Validate volume range
        volume = min(max(0, volume_percent), 100)
        spotify.volume(volume)
        return f"🔊 Volume set to {volume}%"
    except Exception as e:
        logging.error(f"Error setting volume: {str(e)}")
        return f"Error setting volume: {str(e)}"

def toggle_shuffle(spotify):
    """Toggle shuffle mode"""
    try:
        # Get current playback state
        current = spotify.current_playback()
        if not current:
            return "No active playback found"
            
        # Toggle shuffle
        new_state = not current.get('shuffle_state', False)
        spotify.shuffle(new_state)
        
        if new_state:
            return "🔀 Shuffle turned on"
        else:
            return "↩️ Shuffle turned off"
    except Exception as e:
        logging.error(f"Error toggling shuffle: {str(e)}")
        return f"Error toggling shuffle: {str(e)}"

def get_currently_playing(spotify):
    """Get information about the currently playing track"""
    try:
        current = spotify.current_playback()
        if not current or not current.get('item'):
            return "Nothing is currently playing"
            
        track = current['item']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        
        # Format progress/duration
        progress_ms = current.get('progress_ms', 0)
        duration_ms = track.get('duration_ms', 0)
        
        progress_min = int(progress_ms / 60000)
        progress_sec = int((progress_ms % 60000) / 1000)
        
        duration_min = int(duration_ms / 60000)
        duration_sec = int((duration_ms % 60000) / 1000)
        
        time_info = f"{progress_min}:{progress_sec:02d}/{duration_min}:{duration_sec:02d}"
        
        playing_status = "▶️ Playing:" if current.get('is_playing') else "⏸️ Paused:"
        
        return f"{playing_status} '{track['name']}' by {artist}\nAlbum: {album}\nTime: {time_info}"
    except Exception as e:
        logging.error(f"Error getting currently playing: {str(e)}")
        return f"Error getting currently playing track: {str(e)}"

def toggle_repeat(spotify):
    """Toggle repeat mode (off -> context -> track -> off)"""
    try:
        # Get current state
        current = spotify.current_playback()
        if not current:
            return "No active playback found"
            
        # Current repeat state
        current_state = current.get('repeat_state', 'off')
        
        # Determine next state
        next_state = {
            'off': 'context',  # repeat playlist/album
            'context': 'track',  # repeat song
            'track': 'off'  # no repeat
        }.get(current_state, 'off')
        
        spotify.repeat(next_state)
        
        messages = {
            'off': "🔁 Repeat turned off",
            'context': "🔁 Repeating playlist/album",
            'track': "🔂 Repeating this track"
        }
        
        return messages.get(next_state, "Repeat mode changed")
    except Exception as e:
        logging.error(f"Error toggling repeat: {str(e)}")
        return f"Error toggling repeat mode: {str(e)}"

# ---- Playlist Management Functions ----

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
            
        return f"📝 Created playlist '{name}' - {playlist['external_urls']['spotify']}"
    except Exception as e:
        logging.error(f"Error creating playlist: {str(e)}")
        return f"Error creating playlist: {str(e)}"

def search_and_add_to_playlist(spotify, playlist_name, track_query):
    """Search for a track and add it to a specified playlist"""
    try:
        # Find the playlist
        playlists = spotify.current_user_playlists()
        target_playlist = None
        
        for playlist in playlists['items']:
            if playlist['name'].lower() == playlist_name.lower():
                target_playlist = playlist
                break
                
        if not target_playlist:
            return f"Playlist '{playlist_name}' not found in your library"
            
        # Search for the track
        results = spotify.search(q=track_query, type='track', limit=1)
        if not results['tracks']['items']:
            return f"No tracks found for '{track_query}'"
            
        track = results['tracks']['items'][0]
        
        # Add to playlist
        spotify.playlist_add_items(target_playlist['id'], [track['uri']])
        
        return f"➕ Added '{track['name']}' by {track['artists'][0]['name']} to playlist '{target_playlist['name']}'"
    except Exception as e:
        logging.error(f"Error adding to playlist: {str(e)}")
        return f"Error adding track to playlist: {str(e)}"

def get_recommendations(spotify, seed_artists=None, seed_tracks=None, seed_genres=None, limit=10):
    """Get track recommendations based on seeds"""
    try:
        # Prepare seed parameters
        params = {'limit': limit}
        
        if seed_artists:
            # Convert artist names to IDs if needed
            if isinstance(seed_artists[0], str) and not seed_artists[0].startswith('spotify:artist:'):
                artist_ids = []
                for artist_name in seed_artists:
                    results = spotify.search(q=artist_name, type='artist', limit=1)
                    if results['artists']['items']:
                        artist_ids.append(results['artists']['items'][0]['id'])
                seed_artists = artist_ids
                
            params['seed_artists'] = seed_artists[:5]  # Spotify allows max 5 seed values total
        
        if seed_tracks:
            # Convert track names to IDs if needed
            if isinstance(seed_tracks[0], str) and not seed_tracks[0].startswith('spotify:track:'):
                track_ids = []
                for track_name in seed_tracks:
                    results = spotify.search(q=track_name, type='track', limit=1)
                    if results['tracks']['items']:
                        track_ids.append(results['tracks']['items'][0]['id'])
                seed_tracks = track_ids
                
            params['seed_tracks'] = seed_tracks[:5]
        
        if seed_genres:
            params['seed_genres'] = seed_genres[:5]
            
        # Get recommendations
        recommendations = spotify.recommendations(**params)
        
        if not recommendations['tracks']:
            return "No recommendations found with those seeds"
            
        # Format response
        result = "🎵 Recommended tracks:\n"
        for i, track in enumerate(recommendations['tracks'], 1):
            result += f"{i}. {track['name']} by {track['artists'][0]['name']}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting recommendations: {str(e)}")
        return f"Error getting music recommendations: {str(e)}"

def create_recommendations_playlist(spotify, playlist_name, seed_description, limit=20):
    """Create a playlist with recommendations based on seed description"""
    try:
        # Parse the seed description
        seed_tracks = []
        seed_artists = []
        seed_genres = []
        
        # First try to find artists/tracks based on the description
        if "like" in seed_description.lower():
            query = seed_description.lower().split("like ")[1].strip()
            
            # Try as an artist first
            artist_results = spotify.search(q=query, type='artist', limit=1)
            if artist_results['artists']['items']:
                seed_artists = [artist_results['artists']['items'][0]['id']]
            else:
                # Try as a track
                track_results = spotify.search(q=query, type='track', limit=1)
                if track_results['tracks']['items']:
                    seed_tracks = [track_results['tracks']['items'][0]['id']]
        
        # If no specific seeds found, use top tracks/artists as seeds
        if not seed_tracks and not seed_artists:
            # Get user's top artists and tracks
            try:
                top_artists = spotify.current_user_top_artists(limit=2, time_range='medium_term')
                if top_artists['items']:
                    seed_artists = [artist['id'] for artist in top_artists['items']]
            except:
                pass
                
            try:
                top_tracks = spotify.current_user_top_tracks(limit=3, time_range='medium_term')
                if top_tracks['items']:
                    seed_tracks = [track['id'] for track in top_tracks['items']]
            except:
                pass
                
        # Get recommendations
        recommendations = spotify.recommendations(
            seed_artists=seed_artists[:2],
            seed_tracks=seed_tracks[:3],
            seed_genres=seed_genres,
            limit=limit
        )
        
        if not recommendations['tracks']:
            return "Unable to generate recommendations with those seeds"
            
        # Create a new playlist
        track_uris = [track['uri'] for track in recommendations['tracks']]
        description = f"Recommendations based on: {seed_description}"
        
        result = create_playlist(spotify, playlist_name, track_uris, description)
        return result
    except Exception as e:
        logging.error(f"Error creating recommendations playlist: {str(e)}")
        return f"Error creating recommendations playlist: {str(e)}"

def get_user_playlists(spotify, limit=10):
    """Get the user's playlists"""
    try:
        playlists = spotify.current_user_playlists(limit=limit)
        
        if not playlists['items']:
            return "You don't have any playlists yet"
            
        result = "📋 Your playlists:\n"
        for i, playlist in enumerate(playlists['items'], 1):
            track_count = playlist.get('tracks', {}).get('total', 0)
            result += f"{i}. {playlist['name']} ({track_count} tracks)\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting playlists: {str(e)}")
        return f"Error retrieving your playlists: {str(e)}"

def create_mood_playlist(spotify, mood, playlist_name=None):
    """Create a playlist based on mood"""
    try:
        # Map moods to audio features
        mood_presets = {
            'happy': {
                'target_valence': 0.8,
                'target_energy': 0.7,
                'min_valence': 0.6,
                'limit': 20,
                'name_prefix': 'Happy Vibes'
            },
            'sad': {
                'target_valence': 0.2,
                'target_energy': 0.4,
                'max_valence': 0.4,
                'limit': 20,
                'name_prefix': 'Melancholy Moods'
            },
            'energetic': {
                'target_energy': 0.9,
                'target_danceability': 0.7,
                'min_energy': 0.7,
                'limit': 20,
                'name_prefix': 'Energy Boost'
            },
            'relaxed': {
                'target_energy': 0.3,
                'target_valence': 0.5,
                'max_energy': 0.5,
                'limit': 20,
                'name_prefix': 'Chill & Relax'
            },
            'workout': {
                'target_energy': 0.9,
                'target_tempo': 130,
                'min_energy': 0.7,
                'min_tempo': 120,
                'limit': 25,
                'name_prefix': 'Workout Mix'
            },
            'focus': {
                'target_energy': 0.4,
                'target_instrumentalness': 0.7,
                'max_speechiness': 0.1,
                'target_acousticness': 0.6,
                'limit': 25,
                'name_prefix': 'Focus & Concentration'
            },
            'party': {
                'target_danceability': 0.8,
                'target_energy': 0.8,
                'min_danceability': 0.7,
                'limit': 30,
                'name_prefix': 'Party Hits'
            },
            'sleep': {
                'target_energy': 0.1,
                'target_instrumentalness': 0.8,
                'max_energy': 0.3,
                'target_tempo': 70,
                'max_tempo': 90,
                'limit': 20,
                'name_prefix': 'Sleep Soundly'
            }
        }
        
        # Get mood settings
        mood = mood.lower()
        if mood not in mood_presets:
            return f"Unsupported mood: {mood}. Available moods: {', '.join(mood_presets.keys())}"
            
        preset = mood_presets[mood]
        if not playlist_name:
            playlist_name = f"{preset['name_prefix']} - {datetime.datetime.now().strftime('%b %d')}"
        
        # Get seed tracks and artists
        seed_tracks = []
        seed_artists = []
        
        # Get user's top tracks and artists as seeds
        try:
            top_artists = spotify.current_user_top_artists(limit=2, time_range='medium_term')
            if top_artists['items']:
                seed_artists = [artist['id'] for artist in top_artists['items']]
        except:
            pass
            
        try:
            top_tracks = spotify.current_user_top_tracks(limit=3, time_range='medium_term')
            if top_tracks['items']:
                seed_tracks = [track['id'] for track in top_tracks['items']]
        except:
            pass
        
        # Create recommendation parameters
        params = {
            'seed_artists': seed_artists[:2],
            'seed_tracks': seed_tracks[:3],
            'limit': preset.get('limit', 20)
        }
        
        # Add audio feature targets
        for key, value in preset.items():
            if key.startswith('target_') or key.startswith('min_') or key.startswith('max_'):
                params[key] = value
        
        # Get recommendations
        recommendations = spotify.recommendations(**params)
        
        if not recommendations['tracks']:
            return f"Unable to generate {mood} music recommendations"
            
        # Create a new playlist
        track_uris = [track['uri'] for track in recommendations['tracks']]
        description = f"{mood.capitalize()} playlist created on {datetime.datetime.now().strftime('%B %d, %Y')}"
        
        result = create_playlist(spotify, playlist_name, track_uris, description)
        mood_emoji = {
            'happy': '😊', 'sad': '😢', 'energetic': '⚡', 'relaxed': '😌',
            'workout': '💪', 'focus': '🧠', 'party': '🎉', 'sleep': '💤'
        }
        
        return f"{mood_emoji.get(mood, '')} {result}"
    except Exception as e:
        logging.error(f"Error creating mood playlist: {str(e)}")
        return f"Error creating {mood} playlist: {str(e)}"

# ---- User Profile & Stats Functions ----

def get_top_tracks(spotify, time_range='medium_term', limit=10):
    """Get user's top tracks for a time period
    time_range: short_term (4 weeks), medium_term (6 months), long_term (years)
    """
    try:
        top_tracks = spotify.current_user_top_tracks(limit=limit, time_range=time_range)
        
        if not top_tracks['items']:
            return "No top tracks found for this time period"
        
        # Determine time period for display
        period_display = {
            'short_term': 'last 4 weeks',
            'medium_term': 'last 6 months',
            'long_term': 'all time'
        }.get(time_range, time_range)
        
        result = f"🎵 Your top tracks ({period_display}):\n"
        for i, track in enumerate(top_tracks['items'], 1):
            result += f"{i}. {track['name']} by {track['artists'][0]['name']}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting top tracks: {str(e)}")
        return f"Error retrieving your top tracks: {str(e)}"

def get_top_artists(spotify, time_range='medium_term', limit=10):
    """Get user's top artists for a time period
    time_range: short_term (4 weeks), medium_term (6 months), long_term (years)
    """
    try:
        top_artists = spotify.current_user_top_artists(limit=limit, time_range=time_range)
        
        if not top_artists['items']:
            return "No top artists found for this time period"
        
        # Determine time period for display
        period_display = {
            'short_term': 'last 4 weeks',
            'medium_term': 'last 6 months',
            'long_term': 'all time'
        }.get(time_range, time_range)
        
        result = f"👨‍🎤 Your top artists ({period_display}):\n"
        for i, artist in enumerate(top_artists['items'], 1):
            genres = ", ".join(artist['genres'][:2]) if artist['genres'] else "N/A"
            result += f"{i}. {artist['name']} (Genres: {genres})\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting top artists: {str(e)}")
        return f"Error retrieving your top artists: {str(e)}"

def get_recently_played(spotify, limit=10):
    """Get user's recently played tracks"""
    try:
        recent_tracks = spotify.current_user_recently_played(limit=limit)
        
        if not recent_tracks['items']:
            return "No recently played tracks found"
            
        result = "🕒 Your recently played tracks:\n"
        for i, item in enumerate(recent_tracks['items'], 1):
            track = item['track']
            played_at = datetime.datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            time_ago = get_time_ago(played_at)
            
            result += f"{i}. {track['name']} by {track['artists'][0]['name']} ({time_ago})\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting recently played: {str(e)}")
        return f"Error retrieving your recently played tracks: {str(e)}"

def get_saved_albums(spotify, limit=10):
    """Get user's saved albums"""
    try:
        albums = spotify.current_user_saved_albums(limit=limit)
        
        if not albums['items']:
            return "You don't have any saved albums"
            
        result = "💿 Your saved albums:\n"
        for i, item in enumerate(albums['items'], 1):
            album = item['album']
            result += f"{i}. {album['name']} by {album['artists'][0]['name']}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting saved albums: {str(e)}")
        return f"Error retrieving your saved albums: {str(e)}"

def get_followed_artists(spotify, limit=10):
    """Get user's followed artists"""
    try:
        followed = spotify.current_user_followed_artists(limit=limit)
        artists = followed.get('artists', {}).get('items', [])
        
        if not artists:
            return "You're not following any artists"
            
        result = "🎸 Artists you follow:\n"
        for i, artist in enumerate(artists, 1):
            result += f"{i}. {artist['name']}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting followed artists: {str(e)}")
        return f"Error retrieving your followed artists: {str(e)}"

def get_listening_stats(spotify):
    """Get summary of user's listening habits"""
    try:
        stats = {}
        
        # Get top artists
        try:
            top_artists_long = spotify.current_user_top_artists(time_range='long_term', limit=50)
            top_artists_short = spotify.current_user_top_artists(time_range='short_term', limit=50)
            
            # Extract genre information
            all_genres = []
            for artist in top_artists_long['items']:
                all_genres.extend(artist['genres'])
                
            # Count genre frequency
            genre_count = Counter(all_genres)
            top_genres = genre_count.most_common(5)
            
            stats['top_genres'] = [genre for genre, _ in top_genres]
            stats['top_artist_all_time'] = top_artists_long['items'][0]['name'] if top_artists_long['items'] else None
            stats['top_artist_recent'] = top_artists_short['items'][0]['name'] if top_artists_short['items'] else None
        except Exception as e:
            logging.error(f"Error getting artist stats: {str(e)}")
            
        # Get top tracks
        try:
            top_tracks_long = spotify.current_user_top_tracks(time_range='long_term', limit=50)
            top_tracks_short = spotify.current_user_top_tracks(time_range='short_term', limit=50)
            
            stats['top_track_all_time'] = f"{top_tracks_long['items'][0]['name']} by {top_tracks_long['items'][0]['artists'][0]['name']}" if top_tracks_long['items'] else None
            stats['top_track_recent'] = f"{top_tracks_short['items'][0]['name']} by {top_tracks_short['items'][0]['artists'][0]['name']}" if top_tracks_short['items'] else None
        except Exception as e:
            logging.error(f"Error getting track stats: {str(e)}")
            
        # Get recently played
        try:
            recent = spotify.current_user_recently_played(limit=50)
            stats['recently_played_count'] = len(recent['items'])
        except Exception as e:
            logging.error(f"Error getting recent play stats: {str(e)}")
            
        # Get playlist count
        try:
            playlists = spotify.current_user_playlists(limit=50)
            stats['playlist_count'] = playlists['total']
        except Exception as e:
            logging.error(f"Error getting playlist stats: {str(e)}")
            
        # Format the output
        result = "📊 Your Spotify Stats:\n\n"
        
        if stats.get('top_artist_all_time'):
            result += f"👑 All-time favorite artist: {stats['top_artist_all_time']}\n"
            
        if stats.get('top_artist_recent'):
            result += f"🆕 Current favorite artist: {stats['top_artist_recent']}\n"
            
        if stats.get('top_track_all_time'):
            result += f"💫 All-time favorite track: {stats['top_track_all_time']}\n"
            
        if stats.get('top_track_recent'):
            result += f"🔥 Current favorite track: {stats['top_track_recent']}\n"
            
        if stats.get('top_genres'):
            result += f"🎭 Your top genres: {', '.join(stats['top_genres'])}\n"
            
        if stats.get('playlist_count'):
            result += f"📋 You have {stats['playlist_count']} playlists\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting listening stats: {str(e)}")
        return f"Error retrieving your listening stats: {str(e)}"

# ---- Music Discovery Functions ----

def get_new_releases(spotify, limit=10):
    """Get new album releases"""
    try:
        new_releases = spotify.new_releases(limit=limit)
        
        if not new_releases['albums']['items']:
            return "No new releases found"
            
        result = "🆕 New releases:\n"
        for i, album in enumerate(new_releases['albums']['items'], 1):
            result += f"{i}. {album['name']} by {album['artists'][0]['name']}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting new releases: {str(e)}")
        return f"Error retrieving new releases: {str(e)}"

def discover_similar_artists(spotify, artist_name, limit=10):
    """Find similar artists to a given artist"""
    try:
        # Search for the artist
        results = spotify.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'"
            
        artist = results['artists']['items'][0]
        
        # Get related artists
        related = spotify.artist_related_artists(artist['id'])
        if not related['artists']:
            return f"No similar artists found for {artist['name']}"
            
        result = f"👥 Artists similar to {artist['name']}:\n"
        for i, similar in enumerate(related['artists'][:limit], 1):
            genres = ", ".join(similar['genres'][:2]) if similar['genres'] else "N/A"
            result += f"{i}. {similar['name']} (Genres: {genres})\n"
            
        return result
    except Exception as e:
        logging.error(f"Error finding similar artists: {str(e)}")
        return f"Error finding similar artists: {str(e)}"

def get_featured_playlists(spotify, limit=10):
    """Get Spotify's featured playlists"""
    try:
        featured = spotify.featured_playlists(limit=limit)
        
        if not featured['playlists']['items']:
            return "No featured playlists found"
            
        message = featured.get('message', 'Featured playlists')
        result = f"✨ {message}:\n"
        
        for i, playlist in enumerate(featured['playlists']['items'], 1):
            result += f"{i}. {playlist['name']} - {playlist['description'][:50]}...\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting featured playlists: {str(e)}")
        return f"Error retrieving featured playlists: {str(e)}"

def get_category_playlists(spotify, category_name, limit=10):
    """Get playlists for a specific category"""
    try:
        # First, find the category ID
        categories = spotify.categories(limit=50)
        category_id = None
        
        for category in categories['categories']['items']:
            if category['name'].lower() == category_name.lower():
                category_id = category['id']
                break
                
        # If not found by exact match, try partial match
        if not category_id:
            for category in categories['categories']['items']:
                if category_name.lower() in category['name'].lower():
                    category_id = category['id']
                    category_name = category['name']
                    break
        
        if not category_id:
            # Get list of available categories
            category_list = [cat['name'] for cat in categories['categories']['items']]
            category_str = ", ".join(category_list[:10])
            return f"Category '{category_name}' not found. Try one of these: {category_str}..."
            
        # Get playlists for the category
        playlists = spotify.category_playlists(category_id=category_id, limit=limit)
        
        if not playlists['playlists']['items']:
            return f"No playlists found for category '{category_name}'"
            
        result = f"📂 {category_name} playlists:\n"
        for i, playlist in enumerate(playlists['playlists']['items'], 1):
            result += f"{i}. {playlist['name']} ({playlist['tracks']['total']} tracks)\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting category playlists: {str(e)}")
        return f"Error retrieving playlists for category '{category_name}': {str(e)}"

def get_track_audio_features(spotify, track_name):
    """Get detailed audio features for a track"""
    try:
        # Search for the track
        results = spotify.search(q=track_name, type='track', limit=1)
        if not results['tracks']['items']:
            return f"No track found for '{track_name}'"
            
        track = results['tracks']['items'][0]
        
        # Get audio features
        features = spotify.audio_features(track['id'])[0]
        
        if not features:
            return f"No audio features found for '{track['name']}'"
            
        # Format the results
        result = f"🎵 Audio features for '{track['name']}' by {track['artists'][0]['name']}:\n\n"
        
        # Create a more user-friendly display of the features
        feature_descriptions = {
            'danceability': ('Danceability', f"{int(features['danceability'] * 100)}%", 
                           f"How suitable the track is for dancing (based on tempo, rhythm, etc.)"),
            'energy': ('Energy', f"{int(features['energy'] * 100)}%", 
                     f"The intensity and activity level of the track"),
            'valence': ('Happiness', f"{int(features['valence'] * 100)}%", 
                      f"The musical positiveness of the track (high = happy, low = sad)"),
            'acousticness': ('Acousticness', f"{int(features['acousticness'] * 100)}%", 
                           f"Likelihood the track is acoustic vs. electronic"),
            'instrumentalness': ('Instrumentalness', f"{int(features['instrumentalness'] * 100)}%", 
                               f"Likelihood the track contains no vocals"),
            'tempo': ('Tempo', f"{int(features['tempo'])} BPM", 
                    f"The speed of the track in beats per minute"),
            'key': ('Key', get_musical_key(features['key']), 
                  f"The key of the track (estimated)"),
            'mode': ('Mode', 'Major' if features['mode'] == 1 else 'Minor', 
                   f"The modality of the track"),
            'loudness': ('Loudness', f"{features['loudness']} dB", 
                       f"The overall loudness of the track"),
            'liveness': ('Liveness', f"{int(features['liveness'] * 100)}%", 
                       f"Likelihood the track was performed live")
        }
        
        # Add each feature with explanation
        for feature, (label, value, description) in feature_descriptions.items():
            result += f"{label}: {value}\n"
            
        return result
    except Exception as e:
        logging.error(f"Error getting track audio features: {str(e)}")
        return f"Error retrieving audio features: {str(e)}"

# ---- Social Features ----

def follow_artist(spotify, artist_name):
    """Follow an artist on Spotify"""
    try:
        # Search for the artist
        results = spotify.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'"
            
        artist = results['artists']['items'][0]
        
        # Follow the artist
        spotify.user_follow_artists([artist['id']])
        
        return f"✅ You are now following {artist['name']}"
    except Exception as e:
        logging.error(f"Error following artist: {str(e)}")
        return f"Error following artist: {str(e)}"

def unfollow_artist(spotify, artist_name):
    """Unfollow an artist on Spotify"""
    try:
        # Search for the artist
        results = spotify.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'"
            
        artist = results['artists']['items'][0]
        
        # Unfollow the artist
        spotify.user_unfollow_artists([artist['id']])
        
        return f"🚫 You have unfollowed {artist['name']}"
    except Exception as e:
        logging.error(f"Error unfollowing artist: {str(e)}")
        return f"Error unfollowing artist: {str(e)}"

def share_track(spotify, track_name):
    """Get a shareable link for a track"""
    try:
        # Search for the track
        results = spotify.search(q=track_name, type='track', limit=1)
        if not results['tracks']['items']:
            return f"No track found for '{track_name}'"
            
        track = results['tracks']['items'][0]
        artist = track['artists'][0]['name']
        
        # Get the external URL
        url = track['external_urls']['spotify']
        
        return f"🔗 Share '{track['name']}' by {artist}:\n{url}"
    except Exception as e:
        logging.error(f"Error sharing track: {str(e)}")
        return f"Error getting share link: {str(e)}"

# ---- Travel/Context-Specific Playlist Functions ----

def create_travel_playlist(spotify, destination, playlist_name=None):
    """Create a playlist for a travel destination"""
    try:
        if not playlist_name:
            playlist_name = f"Trip to {destination}"
            
        # Search for music related to the destination
        # Try different search approaches
        
        # 1. Search for city/country name
        results1 = spotify.search(q=destination, type='track', limit=10)
        
        # 2. Search for "travel" + destination
        results2 = spotify.search(q=f"travel {destination}", type='track', limit=10)
        
        # Combine results (avoiding duplicates)
        tracks = []
        track_ids = set()
        
        for results in [results1, results2]:
            for track in results['tracks']['items']:
                if track['id'] not in track_ids:
                    tracks.append(track)
                    track_ids.add(track['id'])
                    
        # If we don't have enough tracks, get some popular music as well
        if len(tracks) < 15:
            # Get some general travel/road trip music
            results3 = spotify.search(q="road trip travel vacation", type='track', limit=20)
            for track in results3['tracks']['items']:
                if track['id'] not in track_ids and len(tracks) < 30:
                    tracks.append(track)
                    track_ids.add(track['id'])
                    
        # If still not enough, get some recommendations
        if len(tracks) < 20:
            seed_tracks = list(track_ids)[:3]  # Use up to 3 seed tracks
            if seed_tracks:
                recommendations = spotify.recommendations(seed_tracks=seed_tracks, limit=20)
                for track in recommendations['tracks']:
                    if track['id'] not in track_ids:
                        tracks.append(track)
                        track_ids.add(track['id'])
        
        # Create the playlist
        if tracks:
            track_uris = [track['uri'] for track in tracks]
            description = f"Soundtrack for your trip to {destination}"
            
            result = create_playlist(spotify, playlist_name, track_uris, description)
            return f"🧳 {result}"
        else:
            return f"Couldn't find enough tracks for a {destination} travel playlist"
    except Exception as e:
        logging.error(f"Error creating travel playlist: {str(e)}")
        return f"Error creating travel playlist: {str(e)}"

def create_workout_playlist(spotify, workout_type, duration_minutes=45, playlist_name=None):
    """Create a workout playlist based on type and duration"""
    try:
        # Map workout types to audio features
        workout_presets = {
            'cardio': {
                'target_energy': 0.9,
                'target_tempo': 130,
                'min_energy': 0.8,
                'min_tempo': 120,
                'name_prefix': 'Cardio Mix'
            },
            'hiit': {
                'target_energy': 0.95,
                'target_tempo': 140,
                'min_energy': 0.85,
                'min_tempo': 130,
                'name_prefix': 'HIIT Workout'
            },
            'strength': {
                'target_energy': 0.85,
                'target_tempo': 110,
                'min_energy': 0.7,
                'target_loudness': -5,
                'name_prefix': 'Strength Training'
            },
            'yoga': {
                'target_energy': 0.4,
                'target_instrumentalness': 0.6,
                'max_energy': 0.6,
                'target_tempo': 90,
                'max_tempo': 110,
                'name_prefix': 'Yoga Flow'
            },
            'running': {
                'target_energy': 0.85,
                'target_tempo': 160,
                'min_energy': 0.7,
                'min_tempo': 140,
                'name_prefix': 'Running Beats'
            }
        }
        
        # Default to cardio if workout type not found
        workout_type = workout_type.lower()
        preset = workout_presets.get(workout_type, workout_presets['cardio'])
        
        if not playlist_name:
            playlist_name = f"{preset['name_prefix']} - {duration_minutes}min"
        
        # Estimate tracks needed based on duration (assuming ~3.5 min per track)
        num_tracks = max(5, round(duration_minutes / 3.5))
        
        # Get seed artists and tracks
        seed_tracks = []
        seed_artists = []
        
        # Try to get user's top artists/tracks as seeds
        try:
            top_artists = spotify.current_user_top_artists(limit=2)
            if top_artists['items']:
                seed_artists = [artist['id'] for artist in top_artists['items']]
        except:
            pass
            
        try:
            top_tracks = spotify.current_user_top_tracks(limit=3)
            if top_tracks['items']:
                seed_tracks = [track['id'] for track in top_tracks['items']]
        except:
            pass
        
        # Get recommendations with the preset parameters
        params = {
            'seed_artists': seed_artists[:2],
            'seed_tracks': seed_tracks[:3],
            'limit': num_tracks
        }
        
        # Add audio feature targets from preset
        for key, value in preset.items():
            if key.startswith('target_') or key.startswith('min_') or key.startswith('max_'):
                params[key] = value
        
        # Get recommendations
        recommendations = spotify.recommendations(**params)
        
        if not recommendations['tracks']:
            return f"Unable to generate {workout_type} workout recommendations"
            
        # Create the playlist
        track_uris = [track['uri'] for track in recommendations['tracks']]
        description = f"{workout_type.capitalize()} workout playlist ({duration_minutes} minutes)"
        
        result = create_playlist(spotify, playlist_name, track_uris, description)
        emoji = {'cardio': '🏃', 'hiit': '⏱️', 'strength': '💪', 'yoga': '🧘', 'running': '👟'}.get(workout_type, '🏋️')
        
        return f"{emoji} {result}"
    except Exception as e:
        logging.error(f"Error creating workout playlist: {str(e)}")
        return f"Error creating workout playlist: {str(e)}"

# ---- Helper Functions ----

def get_time_ago(timestamp):
    """Convert a timestamp to a human-readable 'time ago' string"""
    now = datetime.datetime.now(datetime.timezone.utc)
    if not timestamp.tzinfo:
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}y ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}m ago"
    elif diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"

def get_musical_key(key_number):
    """Convert Spotify's key number to a human-readable key string"""
    keys = ["C", "C♯/D♭", "D", "D♯/E♭", "E", "F", "F♯/G♭", "G", "G♯/A♭", "A", "A♯/B♭", "B"]
    if key_number >= 0 and key_number < len(keys):
        return keys[key_number]
    return "Unknown"
