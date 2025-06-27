"""
Spotify AI Integration

This module provides integration between AI features and Spotify music services.
It allows for intelligent music recommendations and playlist generation based on user preferences.

@module utils.spotify_ai_integration
@description AI-powered Spotify recommendation and assistant features
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union
import random
from flask import session

from utils.spotify_helper import get_spotify_client

logger = logging.getLogger(__name__)

class SpotifyAIIntegration:
    """
    Integrates AI capabilities with Spotify functionality

    This class provides advanced Spotify integration features including:
    - Mood-based recommendations
    - Context-aware playlist generation
    - Listening history analysis
    - Audio feature processing
    - Social music recommendations
    - Music taste comparisons
    - Music discovery tools
    """

    def __init__(self):
        """Initialize the Spotify AI integration"""
        self.logger = logging.getLogger(__name__)

        # Initialize with None values until properly authenticated
        self.spotify_client = None
        self.spotify_auth = None

        # Get credentials from environment variables
        self.client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        from config import AppConfig
        default_redirect = AppConfig.get_external_url('callback')
        self.redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", default_redirect)

        self.logger.info("Spotify AI Integration initialized")

    def authenticate(self, session_obj, user_id=None):
        """Authenticate with Spotify API"""
        self.spotify_client, self.spotify_auth = get_spotify_client(
            session=session_obj,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            user_id=user_id
        )
        return self.is_authenticated()

    def is_authenticated(self):
        """Check if Spotify client is authenticated"""
        return self.spotify_client is not None

    def recommend_music_by_mood(self, mood: str, diversity_level: float = 0.5) -> List[Dict[str, Any]]:
        """
        Recommend music based on user's mood with customizable diversity

        Args:
            mood: The user's current mood (e.g., "happy", "sad", "energetic")
            diversity_level: Controls how diverse the recommendations are (0.0-1.0)
                             Higher values produce more varied selections

        Returns:
            List of track recommendations
        """
        self.logger.info(f"Recommending music for mood: {mood} with diversity: {diversity_level}")

        # Enhanced mood mappings with more audio features
        mood_mappings = {
            "happy": {"min_valence": 0.7, "target_energy": 0.7, "target_danceability": 0.6},
            "sad": {"max_valence": 0.4, "target_energy": 0.3, "target_mode": 0, "target_tempo": 80},
            "relaxed": {"max_energy": 0.4, "target_valence": 0.5, "target_acousticness": 0.6},
            "energetic": {"min_energy": 0.7, "target_valence": 0.6, "min_tempo": 120},
            "focused": {"max_energy": 0.5, "max_valence": 0.5, "target_instrumentalness": 0.5, "max_speechiness": 0.1},
            "uplifting": {"min_valence": 0.6, "target_energy": 0.6, "min_mode": 1},
            "melancholic": {"max_valence": 0.4, "target_acousticness": 0.5, "max_energy": 0.5},
            "motivated": {"target_energy": 0.8, "target_tempo": 130, "min_valence": 0.5},
            "nostalgic": {"target_acousticness": 0.6, "target_valence": 0.5, "max_popularity": 70},
            "intense": {"min_energy": 0.8, "min_loudness": -8.0, "max_acousticness": 0.3},
        }

        # Use default parameters if mood not recognized
        base_params = mood_mappings.get(mood.lower(), {"target_valence": 0.5, "target_energy": 0.5})

        # Adjust parameters based on diversity level
        params = self._apply_diversity(base_params, diversity_level)

        # Get recommendations from Spotify
        try:
            if self.spotify_client.is_authenticated():
                # Add genre seeds for more varied results
                # Get user's top genres
                top_genres = self._get_user_top_genres(limit=3)
                if top_genres:
                    params["seed_genres"] = random.sample(top_genres, min(2, len(top_genres)))

                return self.spotify_client.get_recommendations(limit=15, **params)
            else:
                self.logger.warning("Spotify client not authenticated")
                return []
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def _apply_diversity(self, params: Dict[str, Any], diversity_level: float) -> Dict[str, Any]:
        """
        Adjust recommendation parameters based on desired diversity level

        Args:
            params: Base recommendation parameters
            diversity_level: 0.0-1.0 with higher values increasing diversity

        Returns:
            Modified parameters dict
        """
        result = params.copy()

        # Adjust min/max ranges based on diversity
        for key in list(result.keys()):
            if key.startswith("min_") and diversity_level > 0.3:
                # Decrease min values to allow more variation
                result[key] = max(0, result[key] - (diversity_level * 0.2))
            elif key.startswith("max_") and diversity_level > 0.3:
                # Increase max values to allow more variation
                result[key] = min(1.0, result[key] + (diversity_level * 0.2))
            elif key.startswith("target_") and diversity_level > 0.7:
                # For high diversity, remove some target constraints
                result.pop(key, None)

        return result

    def _get_user_top_genres(self, limit: int = 5) -> List[str]:
        """
        Get the user's top genres based on their favorite artists

        Args:
            limit: Maximum number of genres to return

        Returns:
            List of genre names
        """
        try:
            if not self.spotify_client.is_authenticated():
                return []

            # Get user's top artists
            top_artists = self.spotify_client.get_top_artists(limit=10)

            # Extract genres
            genres = []
            for artist in top_artists:
                genres.extend(artist.get("genres", []))

            # Count genre occurrences
            genre_counts = {}
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

            # Sort by count
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

            # Return top genres
            return [genre for genre, _ in sorted_genres[:limit]]
        except Exception as e:
            self.logger.error(f"Error getting top genres: {str(e)}")
            return []

    def get_playlist_for_activity(self, activity: str, personalize: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a suitable playlist for a specific activity with personalization

        Args:
            activity: The activity (e.g., "workout", "study", "relaxation")
            personalize: Whether to personalize based on user's taste

        Returns:
            Playlist information or None if not found
        """
        # Enhanced activity mappings
        activity_queries = {
            "workout": "workout gym exercise fitness",
            "cardio": "cardio running jogging upbeat",
            "weightlifting": "weightlifting strength heavy",
            "yoga": "yoga mindfulness calm flow",
            "study": "focus study concentration",
            "work": "productivity focus work concentration",
            "reading": "reading ambient calm",
            "relaxation": "relax calm peaceful",
            "meditation": "meditation mindfulness zen",
            "sleep": "sleep peaceful ambient",
            "party": "party upbeat dance fun",
            "dinner": "dinner jazz acoustic chill",
            "cooking": "cooking kitchen upbeat jazz",
            "morning": "morning wake up energetic",
            "commute": "commute driving travel",
            "gaming": "gaming electronic intense",
            "cleaning": "cleaning upbeat motivation",
        }

        base_query = activity_queries.get(activity.lower(), activity)

        try:
            if not self.spotify_client.is_authenticated():
                return None

            if personalize:
                # Add personalization based on user's taste
                top_genres = self._get_user_top_genres(limit=2)
                if top_genres:
                    # Add top genre to the search query
                    personalized_query = f"{base_query} {' '.join(top_genres)}"
                else:
                    personalized_query = base_query

                playlists = self.spotify_client.search_playlists(personalized_query, limit=8)
            else:
                playlists = self.spotify_client.search_playlists(base_query, limit=5)

            if playlists:
                # Return the most relevant playlist
                return playlists[0]
            return None
        except Exception as e:
            self.logger.error(f"Error finding playlist for activity: {str(e)}")
            return None

    def analyze_user_listening_history(self, time_range: str = 'medium_term') -> Dict[str, Any]:
        """
        Analyze the user's listening history to generate insights

        Args:
            time_range: The time range to analyze ('short_term', 'medium_term', 'long_term')

        Returns:
            Dictionary containing insights about listening habits
        """
        if not self.spotify_client.is_authenticated():
            self.logger.warning("Spotify client not authenticated")
            return {"error": "Not authenticated with Spotify"}

        try:
            # Get user's recently played tracks
            recent_tracks = self.spotify_client.get_recently_played(limit=50)

            # Get user's top tracks for the specified time range
            top_tracks = self.spotify_client.get_top_tracks(time_range=time_range, limit=50)

            # Get user's top artists for the specified time range
            top_artists = self.spotify_client.get_top_artists(time_range=time_range, limit=20)

            # Get audio features for top tracks
            track_ids = [track["id"] for track in top_tracks[:20]]
            audio_features = {}

            # Process in batches of 10 to avoid API limits
            for i in range(0, len(track_ids), 10):
                batch = track_ids[i:i+10]
                features_batch = self.spotify_client.get_audio_features(batch)
                for j, features in enumerate(features_batch):
                    if features:
                        audio_features[batch[j]] = features

            # Calculate average audio features
            avg_features = self._calculate_average_features(audio_features)

            # Extract genre information
            genres = self._extract_top_genres(top_artists)

            # Calculate listening patterns
            listening_patterns = self._analyze_listening_patterns(recent_tracks)

            # Analyze energy and mood distribution
            mood_distribution = self._analyze_mood_distribution(audio_features)

            # Get recently discovered artists
            recent_discoveries = self._get_recent_discoveries(recent_tracks, top_artists)

            # Get recommendations for similar artists
            similar_artists = self._get_similar_artists(top_artists[:3])

            return {
                "top_genres": genres,
                "favorite_artists": [artist["name"] for artist in top_artists[:5]],
                "listening_patterns": listening_patterns,
                "mood_distribution": mood_distribution,
                "audio_profile": avg_features,
                "recent_discoveries": recent_discoveries,
                "recommendations": {
                    "similar_artists": similar_artists,
                    "suggested_genres": self._suggest_new_genres(genres)
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing listening history: {str(e)}")
            return {"error": str(e)}

    def _calculate_average_features(self, audio_features: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average audio features from a set of tracks

        Args:
            audio_features: Dict mapping track IDs to their audio features

        Returns:
            Dict with average values for each feature
        """
        if not audio_features:
            return {}

        # Features to analyze
        features_to_analyze = [
            'danceability', 'energy', 'valence', 'acousticness',
            'instrumentalness', 'liveness', 'speechiness', 'tempo'
        ]

        avg_features = {}

        for feature in features_to_analyze:
            values = [
                features[feature]
                for features in audio_features.values()
                if feature in features and features[feature] is not None
            ]

            if values:
                avg_features[feature] = sum(values) / len(values)

        return avg_features

    def _analyze_listening_patterns(self, recent_tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze listening patterns from recently played tracks

        Args:
            recent_tracks: List of recently played tracks

        Returns:
            Dict with listening pattern insights
        """
        if not recent_tracks:
            return {}

        # TODO: Extract time of day patterns from timestamps
        # This is a placeholder for now
        return {
            "morning": 30,
            "afternoon": 45,
            "evening": 120,
        }

    def _analyze_mood_distribution(self, audio_features: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze mood distribution based on audio features

        Args:
            audio_features: Dict mapping track IDs to their audio features

        Returns:
            Dict with mood distribution percentages
        """
        if not audio_features:
            return {}

        moods = {
            "happy": 0,
            "energetic": 0,
            "relaxed": 0,
            "melancholic": 0
        }

        # Count tracks in each mood category
        for track_id, features in audio_features.items():
            valence = features.get('valence', 0.5)
            energy = features.get('energy', 0.5)

            if valence > 0.6 and energy > 0.6:
                moods["happy"] += 1
            elif energy > 0.6:
                moods["energetic"] += 1
            elif valence <= 0.4:
                moods["melancholic"] += 1
            else:
                moods["relaxed"] += 1

        # Convert to percentages
        total = sum(moods.values())
        if total > 0:
            for mood in moods:
                moods[mood] = int((moods[mood] / total) * 100)

        return moods

    def _get_recent_discoveries(self, recent_tracks: List[Dict[str, Any]],
                              top_artists: List[Dict[str, Any]]) -> List[str]:
        """
        Identify artists that appear in recent tracks but not in top artists

        Args:
            recent_tracks: List of recently played tracks
            top_artists: List of top artists

        Returns:
            List of recently discovered artist names
        """
        if not recent_tracks or not top_artists:
            return []

        # Get set of top artist IDs
        top_artist_ids = {artist["id"] for artist in top_artists}

        # Find artists in recent tracks that aren't in top artists
        discoveries = set()
        for track in recent_tracks:
            for artist in track.get("artists", []):
                if artist["id"] not in top_artist_ids:
                    discoveries.add(artist["name"])

        return list(discoveries)[:5]  # Limit to 5 discoveries

    def _get_similar_artists(self, artists: List[Dict[str, Any]]) -> List[str]:
        """
        Get similar artists based on the user's top artists

        Args:
            artists: List of the user's top artists

        Returns:
            List of similar artist names
        """
        if not artists or not self.spotify_client.is_authenticated():
            return []

        similar_artists = set()

        try:
            for artist in artists:
                artist_id = artist.get("id")
                if not artist_id:
                    continue

                related = self.spotify_client.get_artist_related_artists(artist_id)
                for related_artist in related[:3]:  # Get top 3 related for each
                    similar_artists.add(related_artist["name"])

            return list(similar_artists)[:5]  # Limit to 5 similar artists
        except Exception as e:
            self.logger.error(f"Error getting similar artists: {str(e)}")
            return []

    def _suggest_new_genres(self, current_genres: List[str]) -> List[str]:
        """
        Suggest new genres based on the user's current favorites

        Args:
            current_genres: List of the user's current favorite genres

        Returns:
            List of suggested genre names
        """
        # This is a simplified implementation that could be enhanced with more genre mappings
        genre_recommendations = {
            "rock": ["indie rock", "alternative rock", "classic rock", "punk rock"],
            "pop": ["dance pop", "electropop", "indie pop", "synth pop"],
            "hip hop": ["trap", "alternative hip hop", "rap", "r&b"],
            "electronic": ["house", "techno", "ambient", "drum and bass"],
            "indie": ["indie folk", "indie rock", "indie pop", "alternative"],
            "folk": ["singer-songwriter", "indie folk", "americana", "acoustic"],
            "jazz": ["nu jazz", "vocal jazz", "jazz fusion", "bebop"],
            "classical": ["contemporary classical", "neo-classical", "minimalism", "baroque"],
            "metal": ["heavy metal", "progressive metal", "black metal", "death metal"],
            "country": ["americana", "folk", "bluegrass", "alternative country"]
        }

        suggestions = set()

        # Find related genres
        for genre in current_genres:
            genre_lower = genre.lower()
            for key, related in genre_recommendations.items():
                # If the genre contains one of our keys, suggest related genres
                if key in genre_lower:
                    suggestions.update(related)

        # Remove current genres from suggestions
        current_lower = [g.lower() for g in current_genres]
        suggestions = [g for g in suggestions if g.lower() not in current_lower]

        return list(suggestions)[:5]  # Limit to 5 suggestions

    def _extract_top_genres(self, artists: List[Dict[str, Any]]) -> List[str]:
        """
        Extract top genres from a list of artists

        Args:
            artists: List of artist objects from Spotify API

        Returns:
            List of top genres
        """
        genre_count = {}

        for artist in artists:
            for genre in artist.get("genres", []):
                genre_count[genre] = genre_count.get(genre, 0) + 1

        # Sort genres by count
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)

        # Return top 5 genres
        return [genre for genre, count in sorted_genres[:5]]

    def generate_smart_playlist(self, name: str, seed_type: str, seed_value: str,
                             track_count: int = 25) -> Dict[str, Any]:
        """
        Create a smart playlist based on a seed (artist, track, or genre)

        Args:
            name: Name for the playlist
            seed_type: Type of seed ('artist', 'track', or 'genre')
            seed_value: Name of the artist, track, or genre
            track_count: Number of tracks to include (max 100)

        Returns:
            Dict with playlist information and result status
        """
        if not self.spotify_client.is_authenticated():
            return {"success": False, "error": "Not authenticated with Spotify"}

        try:
            # Limit track count to API maximum
            track_count = min(track_count, 100)

            # Prepare recommendation parameters
            params = {"limit": track_count}

            # Add seeds based on type
            if seed_type == 'artist':
                # Search for artist
                artists = self.spotify_client.search(query=seed_value, type='artist', limit=1)
                if not artists or not artists.get('artists', {}).get('items'):
                    return {"success": False, "error": f"Artist '{seed_value}' not found"}

                artist_id = artists['artists']['items'][0]['id']
                params["seed_artists"] = [artist_id]

            elif seed_type == 'track':
                # Search for track
                tracks = self.spotify_client.search(query=seed_value, type='track', limit=1)
                if not tracks or not tracks.get('tracks', {}).get('items'):
                    return {"success": False, "error": f"Track '{seed_value}' not found"}

                track_id = tracks['tracks']['items'][0]['id']
                params["seed_tracks"] = [track_id]

            elif seed_type == 'genre':
                # Validate genre
                available_genres = self.spotify_client.get_available_genre_seeds()
                if seed_value not in available_genres:
                    return {"success": False, "error": f"Genre '{seed_value}' not available. Valid genres: {', '.join(available_genres[:10])}..."}

                params["seed_genres"] = [seed_value]

            else:
                return {"success": False, "error": f"Invalid seed type: {seed_type}"}

            # Get recommendations
            recommendations = self.spotify_client.get_recommendations(**params)
            if not recommendations or not recommendations.get('tracks'):
                return {"success": False, "error": "Failed to get recommendations"}

            # Create playlist
            user_info = self.spotify_client.current_user()
            user_id = user_info['id']

            # Create the playlist
            playlist = self.spotify_client.user_playlist_create(
                user_id,
                name,
                description=f"Smart playlist based on {seed_type}: {seed_value}"
            )

            # Add tracks to playlist
            track_uris = [track['uri'] for track in recommendations['tracks']]
            self.spotify_client.user_playlist_add_tracks(user_id, playlist['id'], track_uris)

            return {
                "success": True,
                "playlist": {
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "url": playlist['external_urls']['spotify'],
                    "track_count": len(track_uris)
                }
            }

        except Exception as e:
            self.logger.error(f"Error creating smart playlist: {str(e)}")
            return {"success": False, "error": str(e)}

    def compare_music_taste(self, friend_id: str) -> Dict[str, Any]:
        """
        Compare the user's music taste with a friend's

        Args:
            friend_id: Spotify ID of the friend to compare with

        Returns:
            Dict with comparison results
        """
        if not self.spotify_client.is_authenticated():
            return {"error": "Not authenticated with Spotify"}

        try:
            # This would require permission to access friend's data
            # For now, returning a mock implementation
            return {
                "message": "Friend comparison feature requires additional permissions",
                "compatibility_score": 0,
                "common_artists": [],
                "common_genres": [],
                "suggested_playlist": None
            }
        except Exception as e:
            self.logger.error(f"Error comparing music taste: {str(e)}")
            return {"error": str(e)}

    def get_concert_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get concert recommendations based on user's favorite artists

        Returns:
            List of concert recommendations
        """
        if not self.spotify_client.is_authenticated():
            return []

        try:
            # This would require integration with a concert API
            # For now, returning a mock implementation
            return []
        except Exception as e:
            self.logger.error(f"Error getting concert recommendations: {str(e)}")
            return []

    def classify_track_mood(self, track_id: str) -> Dict[str, Any]:
        """
        Classify the mood of a track based on its audio features

        Args:
            track_id: Spotify ID of the track

        Returns:
            Dict with mood classification
        """
        if not self.spotify_client.is_authenticated():
            return {"error": "Not authenticated with Spotify"}

        try:
            # Get track info
            track = self.spotify_client.track(track_id)
            if not track:
                return {"error": "Track not found"}

            # Get audio features
            features = self.spotify_client.audio_features([track_id])[0]
            if not features:
                return {"error": "Audio features not available"}

            # Classify mood based on valence and energy
            valence = features.get('valence', 0)
            energy = features.get('energy', 0)

            # Simple mood classification
            if valence > 0.7 and energy > 0.7:
                mood = "Euphoric"
            elif valence > 0.7 and energy <= 0.7:
                mood = "Happy"
            elif valence <= 0.3 and energy > 0.7:
                mood = "Angry"
            elif valence <= 0.3 and energy <= 0.3:
                mood = "Sad"
            elif energy > 0.7:
                mood = "Energetic"
            elif valence > 0.5:
                mood = "Pleasant"
            elif features.get('acousticness', 0) > 0.7:
                mood = "Intimate"
            else:
                mood = "Neutral"

            return {
                "track": {
                    "name": track.get('name'),
                    "artist": track.get('artists', [{}])[0].get('name'),
                    "album": track.get('album', {}).get('name')
                },
                "audio_features": {
                    "valence": valence,
                    "energy": energy,
                    "danceability": features.get('danceability'),
                    "tempo": features.get('tempo'),
                    "acousticness": features.get('acousticness')
                },
                "mood": mood
            }
        except Exception as e:
            self.logger.error(f"Error classifying track mood: {str(e)}")
            return {"error": str(e)}

# Create a singleton instance
spotify_ai = SpotifyAIIntegration()

def get_spotify_ai() -> SpotifyAIIntegration:
    """Get the singleton instance of SpotifyAIIntegration"""
    return spotify_ai