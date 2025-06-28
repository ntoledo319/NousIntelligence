"""
Unified Spotify Services
Consolidated Spotify API integrations and utilities
"""
import os
import json
import time
from typing import Dict, Any, Optional, List, Union

class UnifiedSpotifyService:
    """Unified Spotify services with all integrations"""
    
    def __init__(self):
        self.sp = None
        self.auth_manager = None
        self.setup_client()
    
    def setup_client(self):
        """Setup Spotify client"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8080/callback')
            
            if client_id and client_secret:
                self.auth_manager = SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-modify-public playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read"
                )
                self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
                return True
            else:
                print("Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
                return False
                
        except ImportError:
            print("Spotipy library not available. Install with: pip install spotipy")
            return False
        except Exception as e:
            print(f"Spotify setup error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not self.sp:
            return False
        try:
            self.sp.current_user()
            return True
        except:
            return False
    
    # Player Control Functions
    def get_current_playback(self):
        """Get current playback state"""
        if not self.sp:
            return None
        try:
            return self.sp.current_playback()
        except Exception as e:
            print(f"Playback state error: {e}")
            return None
    
    def get_current_track(self):
        """Get currently playing track"""
        playback = self.get_current_playback()
        if playback and playback.get('item'):
            track = playback['item']
            return {
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'id': track['id'],
                'uri': track['uri'],
                'duration_ms': track['duration_ms'],
                'progress_ms': playback.get('progress_ms', 0),
                'is_playing': playback.get('is_playing', False)
            }
        return None
    
    def play_track(self, track_uri: str = None, context_uri: str = None):
        """Play a track or resume playback"""
        if not self.sp:
            return False
        try:
            if track_uri:
                self.sp.start_playback(uris=[track_uri])
            elif context_uri:
                self.sp.start_playback(context_uri=context_uri)
            else:
                self.sp.start_playback()
            return True
        except Exception as e:
            print(f"Play error: {e}")
            return False
    
    def pause_playback(self):
        """Pause current playback"""
        if not self.sp:
            return False
        try:
            self.sp.pause_playback()
            return True
        except Exception as e:
            print(f"Pause error: {e}")
            return False
    
    def skip_track(self):
        """Skip to next track"""
        if not self.sp:
            return False
        try:
            self.sp.next_track()
            return True
        except Exception as e:
            print(f"Skip error: {e}")
            return False
    
    def previous_track(self):
        """Go to previous track"""
        if not self.sp:
            return False
        try:
            self.sp.previous_track()
            return True
        except Exception as e:
            print(f"Previous error: {e}")
            return False
    
    def set_volume(self, volume_percent: int):
        """Set playback volume (0-100)"""
        if not self.sp:
            return False
        try:
            self.sp.volume(volume_percent)
            return True
        except Exception as e:
            print(f"Volume error: {e}")
            return False
    
    def shuffle(self, state: bool):
        """Set shuffle mode"""
        if not self.sp:
            return False
        try:
            self.sp.shuffle(state)
            return True
        except Exception as e:
            print(f"Shuffle error: {e}")
            return False
    
    def repeat(self, state: str):
        """Set repeat mode: 'track', 'context', 'off'"""
        if not self.sp:
            return False
        try:
            self.sp.repeat(state)
            return True
        except Exception as e:
            print(f"Repeat error: {e}")
            return False
    
    # Search and Discovery
    def search_tracks(self, query: str, limit: int = 10, market: str = 'US'):
        """Search for tracks"""
        if not self.sp:
            return []
        try:
            results = self.sp.search(q=query, type='track', limit=limit, market=market)
            return results['tracks']['items']
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_artists(self, query: str, limit: int = 10):
        """Search for artists"""
        if not self.sp:
            return []
        try:
            results = self.sp.search(q=query, type='artist', limit=limit)
            return results['artists']['items']
        except Exception as e:
            print(f"Artist search error: {e}")
            return []
    
    def search_albums(self, query: str, limit: int = 10):
        """Search for albums"""
        if not self.sp:
            return []
        try:
            results = self.sp.search(q=query, type='album', limit=limit)
            return results['albums']['items']
        except Exception as e:
            print(f"Album search error: {e}")
            return []
    
    def search_playlists(self, query: str, limit: int = 10):
        """Search for playlists"""
        if not self.sp:
            return []
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            return results['playlists']['items']
        except Exception as e:
            print(f"Playlist search error: {e}")
            return []
    
    def get_recommendations(self, seed_tracks: List[str] = None, seed_artists: List[str] = None, 
                          seed_genres: List[str] = None, limit: int = 10, **kwargs):
        """Get track recommendations"""
        if not self.sp:
            return []
        try:
            return self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists, 
                seed_genres=seed_genres,
                limit=limit,
                **kwargs
            )['tracks']
        except Exception as e:
            print(f"Recommendations error: {e}")
            return []
    
    def get_featured_playlists(self, limit: int = 10, country: str = 'US'):
        """Get featured playlists"""
        if not self.sp:
            return []
        try:
            results = self.sp.featured_playlists(limit=limit, country=country)
            return results['playlists']['items']
        except Exception as e:
            print(f"Featured playlists error: {e}")
            return []
    
    # Playlist Management
    def get_user_playlists(self, limit: int = 50):
        """Get current user's playlists"""
        if not self.sp:
            return []
        try:
            results = self.sp.current_user_playlists(limit=limit)
            return results['items']
        except Exception as e:
            print(f"User playlists error: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = "", public: bool = True):
        """Create a new playlist"""
        if not self.sp:
            return None
        try:
            user_id = self.sp.current_user()['id']
            return self.sp.user_playlist_create(
                user_id, name, public=public, description=description
            )
        except Exception as e:
            print(f"Create playlist error: {e}")
            return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]):
        """Add tracks to playlist"""
        if not self.sp:
            return False
        try:
            self.sp.playlist_add_items(playlist_id, track_uris)
            return True
        except Exception as e:
            print(f"Add tracks error: {e}")
            return False
    
    def remove_tracks_from_playlist(self, playlist_id: str, track_uris: List[str]):
        """Remove tracks from playlist"""
        if not self.sp:
            return False
        try:
            self.sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
            return True
        except Exception as e:
            print(f"Remove tracks error: {e}")
            return False
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100):
        """Get tracks from a playlist"""
        if not self.sp:
            return []
        try:
            results = self.sp.playlist_tracks(playlist_id, limit=limit)
            return results['items']
        except Exception as e:
            print(f"Playlist tracks error: {e}")
            return []
    
    # User Library Management
    def get_saved_tracks(self, limit: int = 50):
        """Get user's saved tracks"""
        if not self.sp:
            return []
        try:
            results = self.sp.current_user_saved_tracks(limit=limit)
            return results['items']
        except Exception as e:
            print(f"Saved tracks error: {e}")
            return []
    
    def save_tracks(self, track_ids: List[str]):
        """Save tracks to user's library"""
        if not self.sp:
            return False
        try:
            self.sp.current_user_saved_tracks_add(track_ids)
            return True
        except Exception as e:
            print(f"Save tracks error: {e}")
            return False
    
    def remove_saved_tracks(self, track_ids: List[str]):
        """Remove tracks from user's library"""
        if not self.sp:
            return False
        try:
            self.sp.current_user_saved_tracks_delete(track_ids)
            return True
        except Exception as e:
            print(f"Remove saved tracks error: {e}")
            return False
    
    # Analytics and Insights
    def get_audio_features(self, track_ids: List[str]):
        """Get audio features for tracks"""
        if not self.sp:
            return []
        try:
            return self.sp.audio_features(track_ids)
        except Exception as e:
            print(f"Audio features error: {e}")
            return []
    
    def get_audio_analysis(self, track_id: str):
        """Get detailed audio analysis for a track"""
        if not self.sp:
            return None
        try:
            return self.sp.audio_analysis(track_id)
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return None
    
    def get_top_tracks(self, time_range: str = 'medium_term', limit: int = 20):
        """Get user's top tracks (short_term, medium_term, long_term)"""
        if not self.sp:
            return []
        try:
            results = self.sp.current_user_top_tracks(
                time_range=time_range, limit=limit
            )
            return results['items']
        except Exception as e:
            print(f"Top tracks error: {e}")
            return []
    
    def get_top_artists(self, time_range: str = 'medium_term', limit: int = 20):
        """Get user's top artists"""
        if not self.sp:
            return []
        try:
            results = self.sp.current_user_top_artists(
                time_range=time_range, limit=limit
            )
            return results['items']
        except Exception as e:
            print(f"Top artists error: {e}")
            return []
    
    def get_recently_played(self, limit: int = 50):
        """Get recently played tracks"""
        if not self.sp:
            return []
        try:
            results = self.sp.current_user_recently_played(limit=limit)
            return results['items']
        except Exception as e:
            print(f"Recently played error: {e}")
            return []
    
    # Health and Mood Integration
    def create_workout_playlist(self, name: str = None, duration_minutes: int = 60, 
                               intensity: str = "medium"):
        """Create workout playlist based on duration and intensity"""
        if not name:
            name = f"Workout {intensity.title()} - {duration_minutes}min"
        
        # Get high-energy tracks
        energy_level = {"low": 0.6, "medium": 0.8, "high": 0.95}
        target_energy = energy_level.get(intensity, 0.8)
        
        # Search for workout tracks
        workout_queries = [
            "workout", "pump up", "energy", "motivation", "gym",
            "running", "cardio", "power", "beast mode"
        ]
        
        all_tracks = []
        for query in workout_queries:
            tracks = self.search_tracks(query, limit=10)
            all_tracks.extend(tracks)
        
        # Filter tracks by energy level if audio features available
        selected_tracks = []
        track_ids = [track['id'] for track in all_tracks]
        
        if track_ids:
            audio_features = self.get_audio_features(track_ids)
            
            for i, features in enumerate(audio_features):
                if features and features.get('energy', 0) >= target_energy:
                    selected_tracks.append(all_tracks[i])
                    
                    # Limit playlist length based on duration
                    avg_track_length = 3.5  # minutes
                    max_tracks = int(duration_minutes / avg_track_length)
                    if len(selected_tracks) >= max_tracks:
                        break
        
        # Create playlist
        playlist = self.create_playlist(name, f"High-energy {intensity} workout playlist")
        
        if playlist and selected_tracks:
            track_uris = [track['uri'] for track in selected_tracks]
            self.add_tracks_to_playlist(playlist['id'], track_uris)
            return playlist
        
        return None
    
    def get_mood_based_recommendations(self, mood: str, activity: str = None, limit: int = 20):
        """Get recommendations based on mood and activity"""
        mood_attributes = {
            "happy": {"valence": 0.8, "energy": 0.7},
            "sad": {"valence": 0.2, "energy": 0.3},
            "energetic": {"valence": 0.7, "energy": 0.9},
            "calm": {"valence": 0.5, "energy": 0.2},
            "focused": {"valence": 0.6, "energy": 0.4, "instrumentalness": 0.8},
            "romantic": {"valence": 0.6, "energy": 0.4, "danceability": 0.6},
            "party": {"valence": 0.8, "energy": 0.9, "danceability": 0.8}
        }
        
        attributes = mood_attributes.get(mood.lower(), {"valence": 0.5, "energy": 0.5})
        
        # Add activity-specific adjustments
        if activity:
            if activity.lower() in ["workout", "gym", "running"]:
                attributes["energy"] = 0.9
                attributes["danceability"] = 0.8
            elif activity.lower() in ["study", "work", "focus"]:
                attributes["energy"] = 0.3
                attributes["instrumentalness"] = 0.7
            elif activity.lower() in ["sleep", "relax"]:
                attributes["energy"] = 0.1
                attributes["valence"] = 0.3
        
        # Get user's top tracks for seed
        top_tracks = self.get_top_tracks(limit=5)
        seed_tracks = [track['id'] for track in top_tracks[:2]] if top_tracks else None
        
        return self.get_recommendations(
            seed_tracks=seed_tracks,
            limit=limit,
            **attributes
        )
    
    # Visualization and Analysis
    def generate_playlist_visualization(self, playlist_id: str):
        """Generate visualization data for playlist"""
        tracks = self.get_playlist_tracks(playlist_id)
        if not tracks:
            return None
        
        track_ids = [item['track']['id'] for item in tracks if item['track']]
        audio_features = self.get_audio_features(track_ids)
        
        if not audio_features:
            return None
        
        # Calculate averages
        features_sum = {}
        feature_keys = ['danceability', 'energy', 'speechiness', 'acousticness', 
                       'instrumentalness', 'liveness', 'valence']
        
        for key in feature_keys:
            features_sum[key] = 0
        
        valid_tracks = 0
        for features in audio_features:
            if features:
                valid_tracks += 1
                for key in feature_keys:
                    features_sum[key] += features.get(key, 0)
        
        if valid_tracks == 0:
            return None
        
        averages = {key: value / valid_tracks for key, value in features_sum.items()}
        
        # Get playlist info
        playlist_info = self.sp.playlist(playlist_id) if self.sp else None
        
        return {
            'playlist_info': playlist_info,
            'track_count': len(tracks),
            'audio_features_average': averages,
            'mood_analysis': {
                'energy_level': 'High' if averages['energy'] > 0.7 else 'Medium' if averages['energy'] > 0.4 else 'Low',
                'mood': 'Happy' if averages['valence'] > 0.6 else 'Neutral' if averages['valence'] > 0.4 else 'Melancholic',
                'danceability': 'High' if averages['danceability'] > 0.7 else 'Medium' if averages['danceability'] > 0.4 else 'Low'
            }
        }
    
    def get_listening_stats(self):
        """Get user's listening statistics"""
        if not self.sp:
            return None
        
        try:
            top_tracks_short = self.get_top_tracks('short_term', 10)
            top_tracks_medium = self.get_top_tracks('medium_term', 10)
            top_artists_short = self.get_top_artists('short_term', 10)
            recently_played = self.get_recently_played(50)
            
            return {
                'top_tracks_4_weeks': top_tracks_short,
                'top_tracks_6_months': top_tracks_medium,
                'top_artists_4_weeks': top_artists_short,
                'recently_played': recently_played,
                'total_playlists': len(self.get_user_playlists()),
                'saved_tracks_count': len(self.get_saved_tracks())
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return None

# Backward compatibility functions
def get_spotify_client():
    """Backward compatibility for spotify_client"""
    return UnifiedSpotifyService()

def create_spotify_playlist(name: str, tracks: List[str]):
    """Backward compatibility function"""
    service = UnifiedSpotifyService()
    playlist = service.create_playlist(name)
    if playlist and tracks:
        service.add_tracks_to_playlist(playlist['id'], tracks)
    return playlist

def get_current_spotify_track():
    """Legacy function for getting current track"""
    service = UnifiedSpotifyService()
    return service.get_current_track()

def control_spotify_playback(action: str):
    """Legacy function for playback control"""
    service = UnifiedSpotifyService()
    
    if action == 'play':
        return service.play_track()
    elif action == 'pause':
        return service.pause_playback()
    elif action == 'skip':
        return service.skip_track()
    elif action == 'previous':
        return service.previous_track()
    
    return False

def search_spotify(query: str, search_type: str = 'track'):
    """Legacy search function"""
    service = UnifiedSpotifyService()
    
    if search_type == 'track':
        return service.search_tracks(query)
    elif search_type == 'artist':
        return service.search_artists(query)
    elif search_type == 'album':
        return service.search_albums(query)
    elif search_type == 'playlist':
        return service.search_playlists(query)
    
    return []

# Global service instance for convenience
spotify_service = UnifiedSpotifyService()