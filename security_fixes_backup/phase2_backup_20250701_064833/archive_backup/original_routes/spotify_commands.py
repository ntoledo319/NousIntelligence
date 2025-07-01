"""
Spotify Commands API

This module provides API routes for handling Spotify commands from the chat interface.
It processes actions detected by the AI helper and executes the appropriate Spotify operations.

@module routes.spotify_commands
@description API endpoints for Spotify chat commands
"""

import logging
from flask import Blueprint, jsonify, request, session
from utils.auth_compat import login_required, current_user, get_current_user
import os

from utils.spotify_helper import get_spotify_client
from utils.spotify_ai_integration import get_spotify_ai

# Get Spotify credentials from environment variables
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.environ.get("SPOTIFY_REDIRECT_URI") or "http://localhost:5000/callback/spotify"

spotify_commands = Blueprint('spotify_commands', __name__)

@spotify_commands.route("/api/spotify/command/execute", methods=["POST"])
@login_required
def execute_spotify_command():
    """Execute a Spotify command from the chat interface"""
    if not is_authenticated():
        return jsonify({"success": False, "error": "Demo mode - limited features"}), 401

    # Get Spotify client
    spotify_client, _ = get_spotify_client(
        session=session,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT,
        user_id=get_current_user().get("id") if get_current_user() else None
    )

    if not spotify_client:
        return jsonify({"success": False, "error": "Spotify connection required"}), 400

    # Get command data from request
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No command data provided"}), 400

    command_type = data.get('type')

    try:
        result = {"success": True}

        # Handle different types of commands
        if command_type == 'spotify_playback':
            # Handle playback control
            playback_command = data.get('command')
            if playback_command == 'play' or playback_command == 'resume':
                spotify_client.start_playback()
                message = "▶️ Playback resumed"
            elif playback_command == 'pause' or playback_command == 'stop':
                spotify_client.pause_playback()
                message = "⏸️ Playback paused"
            elif playback_command == 'skip' or playback_command == 'next':
                spotify_client.next_track()
                current = spotify_client.current_playback()
                if current and current.get('item'):
                    track = current['item']
                    message = f"⏭️ Skipped to '{track['name']}' by {track['artists'][0]['name']}"
                else:
                    message = "⏭️ Skipped to next track"
            elif playback_command == 'previous':
                spotify_client.previous_track()
                current = spotify_client.current_playback()
                if current and current.get('item'):
                    track = current['item']
                    message = f"⏮️ Went back to '{track['name']}' by {track['artists'][0]['name']}"
                else:
                    message = "⏮️ Went back to previous track"
            elif playback_command == 'shuffle':
                # Toggle shuffle mode
                current = spotify_client.current_playback()
                if current:
                    new_state = not current.get('shuffle_state', False)
                    spotify_client.shuffle(new_state)
                    message = "🔀 Shuffle turned on" if new_state else "↩️ Shuffle turned off"
                else:
                    message = "No active playback found"
            elif playback_command == 'repeat':
                # Toggle repeat mode (off -> context -> track -> off)
                current = spotify_client.current_playback()
                if current:
                    current_state = current.get('repeat_state', 'off')
                    next_state = {
                        'off': 'context',  # repeat playlist/album
                        'context': 'track',  # repeat song
                        'track': 'off'  # no repeat
                    }.get(current_state, 'off')
                    spotify_client.repeat(next_state)
                    messages = {
                        'off': "🔁 Repeat turned off",
                        'context': "🔁 Repeating playlist/album",
                        'track': "🔂 Repeating this track"
                    }
                    message = messages.get(next_state, "Repeat mode changed")
                else:
                    message = "No active playback found"
            else:
                message = f"Unknown playback command: {playback_command}"
                result["success"] = False

            result["message"] = message

        elif command_type == 'spotify_play':
            # Handle content playback
            content_type = data.get('content_type')
            query = data.get('query')

            if not query:
                return jsonify({"success": False, "error": "No query provided"}), 400

            # Check if devices are available
            devices = spotify_client.devices()
            if not devices or not devices.get('devices'):
                return jsonify({"success": False, "error": "No active Spotify devices found. Please open Spotify on a device first."}), 400

            if content_type == 'track':
                # Search for and play a track
                tracks = spotify_client.search_tracks(query, limit=1)
                if not tracks:
                    message = f"No tracks found for '{query}'"
                    result["success"] = False
                else:
                    track = tracks[0]
                    spotify_client.start_playback(uris=[track['uri']])
                    message = f"▶️ Playing '{track['name']}' by {track['artists'][0]['name']}"
            elif content_type == 'artist':
                # Play top tracks from an artist
                artists = spotify_client.search_artists(query, limit=1)
                if not artists:
                    message = f"No artist found for '{query}'"
                    result["success"] = False
                else:
                    artist = artists[0]
                    top_tracks = spotify_client.artist_top_tracks(artist['id'])
                    if not top_tracks.get('tracks'):
                        message = f"No tracks found for artist '{artist['name']}'"
                        result["success"] = False
                    else:
                        track_uris = [track['uri'] for track in top_tracks['tracks']]
                        spotify_client.start_playback(uris=track_uris)
                        message = f"▶️ Playing top tracks from {artist['name']}"
            elif content_type == 'album':
                # Play an album
                albums = spotify_client.search_albums(query, limit=1)
                if not albums:
                    message = f"No album found for '{query}'"
                    result["success"] = False
                else:
                    album = albums[0]
                    spotify_client.start_playback(context_uri=album['uri'])
                    message = f"▶️ Playing album '{album['name']}' by {album['artists'][0]['name']}"
            elif content_type == 'playlist':
                # Play a playlist
                playlists = spotify_client.search_playlists(query, limit=1)
                if not playlists:
                    message = f"No playlist found for '{query}'"
                    result["success"] = False
                else:
                    playlist = playlists[0]
                    spotify_client.start_playback(context_uri=playlist['uri'])
                    message = f"▶️ Playing playlist '{playlist['name']}' by {playlist['owner']['display_name']}"
            else:
                message = f"Unknown content type: {content_type}"
                result["success"] = False

            result["message"] = message

        elif command_type == 'spotify_create_playlist':
            # Handle playlist creation
            name = data.get('name')
            description = data.get('description', f"Playlist created via NOUS Assistant")

            if not name:
                return jsonify({"success": False, "error": "No playlist name provided"}), 400

            # Get user info and create playlist
            user_info = spotify_client.current_user()
            user_id = user_info['id']

            playlist = spotify_client.user_playlist_create(
                user_id=user_id,
                name=name,
                description=description
            )

            if playlist and playlist.get('id'):
                result["message"] = f"Created playlist '{name}'"
                result["playlist"] = {
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "url": playlist['external_urls']['spotify']
                }
            else:
                result["success"] = False
                result["message"] = f"Failed to create playlist"

        elif command_type == 'spotify_mood':
            # Handle mood-based recommendations
            mood = data.get('mood')
            create_playlist = data.get('create_playlist', False)

            if not mood:
                return jsonify({"success": False, "error": "No mood provided"}), 400

            if create_playlist:
                # Create a mood-based playlist using SpotifyAI
                spotify_ai = get_spotify_ai()
                spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)

                # Get mood recommendations
                tracks = spotify_ai.recommend_music_by_mood(mood, diversity_level=0.7)

                if not tracks:
                    result["success"] = False
                    result["message"] = f"Could not find recommendations for mood: {mood}"
                else:
                    # Create a new playlist
                    user_info = spotify_client.current_user()
                    user_id = user_info['id']

                    # Create playlist
                    playlist = spotify_client.user_playlist_create(
                        user_id=user_id,
                        name=f"Mood: {mood}",
                        description=f"Playlist for {mood} mood created by NOUS Assistant"
                    )

                    # Add tracks to playlist
                    if playlist and tracks:
                        track_uris = [track['uri'] for track in tracks]
                        spotify_client.playlist_add_items(playlist['id'], track_uris)

                        # Use an appropriate emoji for the mood
                        mood_emoji = "🎵"
                        if "happy" in mood.lower():
                            mood_emoji = "😊"
                        elif any(word in mood.lower() for word in ["sad", "melancholy"]):
                            mood_emoji = "😢"
                        elif any(word in mood.lower() for word in ["energetic", "workout"]):
                            mood_emoji = "💪"
                        elif any(word in mood.lower() for word in ["calm", "chill", "relax"]):
                            mood_emoji = "😌"

                        result["message"] = f"{mood_emoji} Created '{playlist['name']}' playlist with {len(track_uris)} tracks"
                        result["playlist"] = {
                            "id": playlist['id'],
                            "name": playlist['name'],
                            "url": playlist['external_urls']['spotify']
                        }
                    else:
                        result["success"] = False
                        result["message"] = "Failed to create playlist"
            else:
                # Use the AI integration for recommendations
                spotify_ai = get_spotify_ai()
                spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)
                recommendations = spotify_ai.recommend_music_by_mood(mood)

                if recommendations:
                    tracks = []
                    for track in recommendations[:5]:  # Limit to 5 for the response
                        tracks.append({
                            "name": track['name'],
                            "artist": track['artists'][0]['name'],
                            "album": track['album']['name']
                        })

                    result["message"] = f"Here are some {mood} tracks for you"
                    result["recommendations"] = tracks
                else:
                    result["success"] = False
                    result["message"] = f"Could not find recommendations for mood: {mood}"

        elif command_type == 'spotify_activity':
            # Handle activity-based playlists
            activity = data.get('activity')

            if not activity:
                return jsonify({"success": False, "error": "No activity provided"}), 400

            # Use the AI integration to find an activity playlist
            spotify_ai = get_spotify_ai()
            spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)
            playlist = spotify_ai.get_playlist_for_activity(activity, personalize=True)

            if playlist:
                result["message"] = f"Found a playlist for {activity}"
                result["playlist"] = {
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "url": playlist['external_urls']['spotify'],
                    "owner": playlist['owner']['display_name']
                }

                # Start playing the playlist if requested
                if data.get('play', False):
                    spotify_client.start_playback(context_uri=playlist['uri'])
                    result["play_result"] = f"▶️ Playing playlist '{playlist['name']}'"
            else:
                result["success"] = False
                result["message"] = f"Could not find a playlist for: {activity}"

        elif command_type == 'spotify_analyze':
            # Handle music analysis requests
            analysis_type = data.get('analysis_type')

            if analysis_type == 'track':
                track_name = data.get('track_name')
                if not track_name:
                    return jsonify({"success": False, "error": "No track name provided"}), 400

                # Use SpotifyAI for track analysis
                spotify_ai = get_spotify_ai()
                spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)

                # Search for the track
                tracks = spotify_client.search_tracks(track_name, limit=1)
                if not tracks:
                    return jsonify({"success": False, "error": f"No track found for '{track_name}'"}), 404

                track = tracks[0]
                track_id = track['id']

                # Get audio features
                features = spotify_client.audio_features(track_id)

                # Format the result
                analysis = {
                    "track": {
                        "name": track['name'],
                        "artist": track['artists'][0]['name'],
                        "album": track['album']['name']
                    },
                    "audio_features": features
                }

                if features:
                    # Classify mood
                    mood = spotify_ai.classify_track_mood(track_id)
                    if mood and not isinstance(mood, dict):
                        analysis["mood"] = mood

                result["message"] = "Track analysis complete"
                result["analysis"] = analysis

            elif analysis_type == 'taste':
                time_range = data.get('time_range', 'medium_term')

                # Get the user's top tracks and artists
                top_tracks = spotify_client.current_user_top_tracks(
                    limit=10,
                    time_range=time_range
                )

                top_artists = spotify_client.current_user_top_artists(
                    limit=10,
                    time_range=time_range
                )

                # Format the results
                analysis = {
                    "top_tracks": [
                        {
                            "name": track['name'],
                            "artist": track['artists'][0]['name']
                        }
                        for track in top_tracks.get('items', [])
                    ],
                    "top_artists": [
                        {
                            "name": artist['name'],
                            "genres": artist.get('genres', [])
                        }
                        for artist in top_artists.get('items', [])
                    ],
                    "time_range": {
                        "short_term": "last 4 weeks",
                        "medium_term": "last 6 months",
                        "long_term": "several years"
                    }.get(time_range, time_range)
                }

                # Use SpotifyAI for more advanced analysis
                spotify_ai = get_spotify_ai()
                spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)
                listening_history = spotify_ai.analyze_user_listening_history(time_range)

                if listening_history and not isinstance(listening_history, dict) and not listening_history.get('error'):
                    analysis.update(listening_history)

                result["message"] = "Music taste analysis complete"
                result["analysis"] = analysis
            else:
                result["success"] = False
                result["message"] = f"Unknown analysis type: {analysis_type}"

        elif command_type == 'spotify_recommendations':
            # Handle recommendations
            seed_type = data.get('seed_type')
            seed_value = data.get('seed_value')
            limit = data.get('limit', 10)

            if not seed_type or not seed_value:
                return jsonify({"success": False, "error": "Missing seed parameters"}), 400

            # Prepare parameters for recommendations
            params = {'limit': min(limit, 20)}  # Cap at 20 for response size

            if seed_type == 'artist':
                # Search for artist
                artists = spotify_client.search_artists(seed_value, limit=1)
                if not artists:
                    return jsonify({"success": False, "error": f"Artist '{seed_value}' not found"}), 404

                artist_id = artists[0]['id']
                params["seed_artists"] = [artist_id]

            elif seed_type == 'track':
                # Search for track
                tracks = spotify_client.search_tracks(seed_value, limit=1)
                if not tracks:
                    return jsonify({"success": False, "error": f"Track '{seed_value}' not found"}), 404

                track_id = tracks[0]['id']
                params["seed_tracks"] = [track_id]

            elif seed_type == 'genre':
                # Check if genre is available
                available_genres = spotify_client.get_available_genre_seeds()
                if seed_value not in available_genres:
                    similar_genres = [g for g in available_genres if seed_value.lower() in g.lower()]
                    if similar_genres:
                        seed_value = similar_genres[0]  # Use first similar match
                    else:
                        return jsonify({"success": False, "error": f"Genre '{seed_value}' not available"}), 404

                params["seed_genres"] = [seed_value]

            else:
                return jsonify({"success": False, "error": f"Invalid seed type: {seed_type}"}), 400

            # Get recommendations
            recommendations = spotify_client.get_recommendations(**params)

            if not recommendations or not recommendations.get('tracks'):
                return jsonify({"success": False, "error": "Failed to get recommendations"}), 500

            # Format response
            tracks = []
            for track in recommendations['tracks']:
                tracks.append({
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "album": track['album']['name'],
                    "uri": track['uri']
                })

            result["message"] = f"Here are recommendations based on {seed_type}: {seed_value}"
            result["recommendations"] = tracks

            # Create playlist if requested
            if data.get('create_playlist', False):
                user_info = spotify_client.current_user()
                user_id = user_info['id']

                playlist_name = data.get('playlist_name', f"Recommendations based on {seed_value}")

                # Create the playlist
                playlist = spotify_client.user_playlist_create(
                    user_id=user_id,
                    name=playlist_name,
                    description=f"Recommendations based on {seed_type}: {seed_value}"
                )

                # Add tracks to playlist
                if playlist:
                    track_uris = [track['uri'] for track in recommendations['tracks']]
                    spotify_client.playlist_add_items(playlist['id'], track_uris)

                    result["playlist"] = {
                        "id": playlist['id'],
                        "name": playlist['name'],
                        "url": playlist['external_urls']['spotify'],
                        "track_count": len(track_uris)
                    }

        else:
            result["success"] = False
            result["message"] = f"Unknown command type: {command_type}"

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error executing Spotify command: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_commands.route("/api/spotify/smart-playlist", methods=["POST"])
@login_required
def create_smart_playlist():
    """Create a smart playlist based on a seed"""
    if not is_authenticated():
        return jsonify({"success": False, "error": "Demo mode - limited features"}), 401

    # Get Spotify client
    spotify_client, _ = get_spotify_client(
        session=session,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT,
        user_id=get_current_user().get("id") if get_current_user() else None
    )

    if not spotify_client:
        return jsonify({"success": False, "error": "Spotify connection required"}), 400

    # Get request data
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    seed_type = data.get('seed_type')
    seed_value = data.get('seed_value')
    name = data.get('name')
    track_count = min(data.get('track_count', 25), 100)  # Cap at 100

    if not seed_type or not seed_value or not name:
        return jsonify({"success": False, "error": "Missing required parameters"}), 400

    try:
        # Create a smart playlist using SpotifyAI
        spotify_ai = get_spotify_ai()
        spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)

        result = spotify_ai.generate_smart_playlist(name, seed_type, seed_value, track_count)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error creating smart playlist: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_commands.route("/api/spotify/track-mood", methods=["GET"])
@login_required
def get_track_mood():
    """Get the mood classification for a track"""
    if not is_authenticated():
        return jsonify({"success": False, "error": "Demo mode - limited features"}), 401

    # Get Spotify client
    spotify_client, _ = get_spotify_client(
        session=session,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT,
        user_id=get_current_user().get("id") if get_current_user() else None
    )

    if not spotify_client:
        return jsonify({"success": False, "error": "Spotify connection required"}), 400

    # Get track ID
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify({"success": False, "error": "No track ID provided"}), 400

    try:
        # Get track info
        track = spotify_client.track(track_id)
        if not track:
            return jsonify({"success": False, "error": "Track not found"}), 404

        # Get audio features
        features = spotify_client.audio_features(track_id)
        if not features:
            return jsonify({"success": False, "error": "Audio features not available"}), 500

        # Use SpotifyAI for mood classification
        spotify_ai = get_spotify_ai()
        spotify_ai.authenticate(session, get_current_user().get("id") if get_current_user() else None)
        mood = spotify_ai.classify_track_mood(track_id)

        result = {
            "success": True,
            "track": {
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name']
            },
            "audio_features": features,
            "mood": mood
        }

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error getting track mood: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500