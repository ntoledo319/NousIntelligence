"""
Spotify Health Integration

This module integrates Spotify music services with health-related features.
It provides functionality for mood-based music recommendations, pain management
through music, and personalized playlists for health activities.

@module utils.spotify_health_integration
@description Health-related Spotify features and integrations
"""

import logging
import os
from typing import Dict, List, Any, Optional

from utils.spotify_helper import get_spotify_client

logger = logging.getLogger(__name__)

class SpotifyHealthIntegration:
    """
    Provides health-focused Spotify functionality
    """

    def __init__(self):
        """Initialize the Spotify health integration"""
        self.logger = logging.getLogger(__name__)
        self.spotify_client = get_spotify_client()
        self.logger.info("Spotify Health Integration initialized")

    def get_pain_management_playlist(self, pain_level: int, pain_type: str) -> Dict[str, Any]:
        """
        Get a playlist recommendation for pain management

        Args:
            pain_level: Pain level on a scale of 1-10
            pain_type: Type of pain (e.g., "headache", "back", "joint")

        Returns:
            Dict containing playlist information
        """
        self.logger.info(f"Finding pain management playlist for {pain_type} at level {pain_level}")

        # Map pain types to music characteristics
        pain_music_mapping = {
            "headache": {
                "search_terms": "calm ambient relaxing",
                "features": {"max_energy": 0.3, "max_loudness": -10}
            },
            "back": {
                "search_terms": "relaxing piano meditation",
                "features": {"max_energy": 0.4, "target_tempo": 70}
            },
            "joint": {
                "search_terms": "gentle classical relaxing",
                "features": {"max_energy": 0.4, "target_instrumentalness": 0.8}
            },
            "general": {
                "search_terms": "relaxing ambient meditation",
                "features": {"max_energy": 0.4, "target_valence": 0.6}
            }
        }

        pain_settings = pain_music_mapping.get(pain_type.lower(), pain_music_mapping["general"])

        # Adjust features based on pain level
        if pain_level > 7:
            # For severe pain, decrease energy and loudness further
            pain_settings["features"]["max_energy"] = 0.2
            pain_settings["features"]["max_loudness"] = -15

        try:
            if self.spotify_client.is_authenticated():
                # Search for playlists
                playlists = self.spotify_client.search_playlists(
                    pain_settings["search_terms"],
                    limit=3
                )

                if playlists:
                    return {
                        "playlist": playlists[0],
                        "recommendation_reason": f"Music for {pain_type} pain level {pain_level}",
                        "suggested_volume": "low" if pain_level > 6 else "medium",
                        "suggested_duration": 30 if pain_level > 7 else 45
                    }

            # Fallback if not authenticated or no playlists found
            return {
                "error": "Could not find suitable playlist",
                "recommendation": "Try searching for gentle ambient music"
            }
        except Exception as e:
            self.logger.error(f"Error getting pain management playlist: {str(e)}")
            return {"error": str(e)}

    def get_mood_improvement_tracks(self, current_mood: str, target_mood: str) -> List[Dict[str, Any]]:
        """
        Get tracks to help transition from current mood to target mood

        Args:
            current_mood: The user's current mood
            target_mood: The mood the user wants to achieve

        Returns:
            List of recommended tracks
        """
        self.logger.info(f"Finding mood transition tracks from {current_mood} to {target_mood}")

        # Define mood characteristics
        mood_characteristics = {
            "sad": {"valence": 0.2, "energy": 0.3},
            "neutral": {"valence": 0.5, "energy": 0.5},
            "happy": {"valence": 0.8, "energy": 0.7},
            "anxious": {"valence": 0.3, "energy": 0.7},
            "relaxed": {"valence": 0.6, "energy": 0.3},
            "energetic": {"valence": 0.7, "energy": 0.9},
            "focused": {"valence": 0.5, "energy": 0.5, "instrumentalness": 0.7},
        }

        current = mood_characteristics.get(current_mood.lower(), mood_characteristics["neutral"])
        target = mood_characteristics.get(target_mood.lower(), mood_characteristics["neutral"])

        # Create a gradual transition in 3 steps
        transitions = []
        for i in range(1, 4):
            ratio = i / 4.0
            step = {
                "target_valence": current["valence"] * (1 - ratio) + target["valence"] * ratio,
                "target_energy": current["energy"] * (1 - ratio) + target["energy"] * ratio
            }

            # Add instrumentalness if needed
            if "instrumentalness" in current or "instrumentalness" in target:
                current_instr = current.get("instrumentalness", 0.3)
                target_instr = target.get("instrumentalness", 0.3)
                step["target_instrumentalness"] = current_instr * (1 - ratio) + target_instr * ratio

            transitions.append(step)

        # Get recommendations for each transition step
        all_tracks = []
        try:
            if self.spotify_client.is_authenticated():
                for i, params in enumerate(transitions):
                    tracks = self.spotify_client.get_recommendations(limit=5, **params)
                    if tracks:
                        all_tracks.extend(tracks)

            return all_tracks
        except Exception as e:
            self.logger.error(f"Error getting mood transition tracks: {str(e)}")
            return []

    def get_sleep_playlist(self, duration_minutes: int) -> Dict[str, Any]:
        """
        Get a playlist to help with sleep

        Args:
            duration_minutes: Desired sleep playlist duration in minutes

        Returns:
            Dict containing playlist information
        """
        self.logger.info(f"Creating sleep playlist for {duration_minutes} minutes")

        # Sleep music parameters
        sleep_params = {
            "target_energy": 0.1,
            "max_energy": 0.3,
            "target_instrumentalness": 0.8,
            "target_tempo": 60,
            "max_loudness": -15
        }

        try:
            if self.spotify_client.is_authenticated():
                # Get recommendations
                tracks = self.spotify_client.get_recommendations(limit=20, **sleep_params)

                # Filter out tracks with sudden changes that might disrupt sleep
                filtered_tracks = [
                    track for track in tracks
                    if track.get("loudness", -20) < -10 and track.get("energy", 1) < 0.3
                ]

                return {
                    "tracks": filtered_tracks[:10],
                    "duration_minutes": min(duration_minutes, len(filtered_tracks) * 3),
                    "recommendation_reason": "Gentle tracks to help with sleep",
                    "suggested_volume": "very low"
                }

            return {"error": "Not authenticated with Spotify"}
        except Exception as e:
            self.logger.error(f"Error creating sleep playlist: {str(e)}")
            return {"error": str(e)}

# Create a singleton instance
spotify_health = SpotifyHealthIntegration()

def get_spotify_health() -> SpotifyHealthIntegration:
    """Get the singleton instance of SpotifyHealthIntegration"""
    return spotify_health