"""
Spotify Unified Client - Complete Spotify Integration
Consolidates playback, library, playlists, and therapeutic music features
"""
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    logger.warning("Spotipy library not available")


class SpotifyClient:
    """
    Unified Spotify client for all music-related features.
    Handles authentication, playback control, library management, and therapeutic music.
    """
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        """
        Initialize Spotify client with user credentials.
        
        Args:
            credentials: Spotify OAuth credentials with access_token, refresh_token
        """
        if not SPOTIFY_AVAILABLE:
            raise ImportError("Spotipy required. Install with: pip install spotipy")
        
        self.client = None
        if credentials:
            self.client = spotipy.Spotify(auth=credentials.get('access_token'))
    
    # ===== PLAYBACK CONTROL =====
    
    def play(self, device_id: Optional[str] = None, 
            context_uri: Optional[str] = None,
            uris: Optional[List[str]] = None) -> bool:
        """
        Start playback.
        
        Args:
            device_id: Device to play on (None = active device)
            context_uri: Spotify URI of album/playlist/artist
            uris: List of track URIs to play
        """
        try:
            self.client.start_playback(
                device_id=device_id,
                context_uri=context_uri,
                uris=uris
            )
            return True
        except Exception as e:
            logger.error(f"Error starting playback: {e}")
            return False
    
    def pause(self, device_id: Optional[str] = None) -> bool:
        """Pause playback"""
        try:
            self.client.pause_playback(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error pausing: {e}")
            return False
    
    def next_track(self, device_id: Optional[str] = None) -> bool:
        """Skip to next track"""
        try:
            self.client.next_track(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error skipping track: {e}")
            return False
    
    def previous_track(self, device_id: Optional[str] = None) -> bool:
        """Go to previous track"""
        try:
            self.client.previous_track(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error going to previous track: {e}")
            return False
    
    def set_volume(self, volume_percent: int, device_id: Optional[str] = None) -> bool:
        """
        Set playback volume.
        
        Args:
            volume_percent: Volume level 0-100
            device_id: Target device
        """
        try:
            self.client.volume(volume_percent, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def shuffle(self, state: bool, device_id: Optional[str] = None) -> bool:
        """Enable/disable shuffle"""
        try:
            self.client.shuffle(state, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting shuffle: {e}")
            return False
    
    def repeat(self, state: str, device_id: Optional[str] = None) -> bool:
        """
        Set repeat mode.
        
        Args:
            state: 'track', 'context', or 'off'
            device_id: Target device
        """
        try:
            self.client.repeat(state, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting repeat: {e}")
            return False
    
    def get_playback_state(self) -> Optional[Dict]:
        """Get current playback state"""
        try:
            return self.client.current_playback()
        except Exception as e:
            logger.error(f"Error getting playback state: {e}")
            return None
    
    def get_devices(self) -> List[Dict]:
        """Get available playback devices"""
        try:
            devices = self.client.devices()
            return devices.get('devices', [])
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    # ===== LIBRARY MANAGEMENT =====
    
    def get_saved_tracks(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's saved tracks"""
        try:
            results = self.client.current_user_saved_tracks(limit=limit, offset=offset)
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Error getting saved tracks: {e}")
            return []
    
    def save_track(self, track_id: str) -> bool:
        """Save a track to library"""
        try:
            self.client.current_user_saved_tracks_add([track_id])
            return True
        except Exception as e:
            logger.error(f"Error saving track: {e}")
            return False
    
    def remove_track(self, track_id: str) -> bool:
        """Remove a track from library"""
        try:
            self.client.current_user_saved_tracks_delete([track_id])
            return True
        except Exception as e:
            logger.error(f"Error removing track: {e}")
            return False
    
    def get_playlists(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's playlists"""
        try:
            results = self.client.current_user_playlists(limit=limit, offset=offset)
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Error getting playlists: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = '', public: bool = False) -> Optional[Dict]:
        """Create a new playlist"""
        try:
            user_id = self.client.current_user()['id']
            playlist = self.client.user_playlist_create(
                user_id,
                name,
                public=public,
                description=description
            )
            return playlist
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return None
    
    def add_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist"""
        try:
            self.client.playlist_add_items(playlist_id, track_uris)
            return True
        except Exception as e:
            logger.error(f"Error adding to playlist: {e}")
            return False
    
    def get_recently_played(self, limit: int = 20) -> List[Dict]:
        """Get recently played tracks"""
        try:
            results = self.client.current_user_recently_played(limit=limit)
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Error getting recently played: {e}")
            return []
    
    # ===== THERAPEUTIC MUSIC FEATURES =====
    
    def get_mood_playlist(self, mood: str) -> Optional[str]:
        """
        Get playlist URI for a specific mood.
        
        Args:
            mood: 'calm', 'energetic', 'focus', 'sleep', 'happy', 'sad'
        
        Returns:
            Playlist URI or None
        """
        mood_queries = {
            'calm': 'calm relaxing peaceful',
            'energetic': 'energetic workout pump up',
            'focus': 'focus concentration study',
            'sleep': 'sleep relaxation ambient',
            'happy': 'happy upbeat positive',
            'sad': 'sad melancholic emotional'
        }
        
        query = mood_queries.get(mood.lower(), mood)
        
        try:
            results = self.client.search(q=query, type='playlist', limit=1)
            playlists = results.get('playlists', {}).get('items', [])
            if playlists:
                return playlists[0]['uri']
            return None
        except Exception as e:
            logger.error(f"Error getting mood playlist: {e}")
            return None
    
    def play_mood_music(self, mood: str, device_id: Optional[str] = None) -> bool:
        """
        Play music matching a specific mood.
        
        Args:
            mood: Target mood
            device_id: Playback device
        """
        playlist_uri = self.get_mood_playlist(mood)
        if playlist_uri:
            return self.play(device_id=device_id, context_uri=playlist_uri)
        return False
    
    def get_recommendations(self, seed_tracks: List[str] = None,
                           seed_artists: List[str] = None,
                           seed_genres: List[str] = None,
                           target_energy: Optional[float] = None,
                           target_valence: Optional[float] = None,
                           limit: int = 20) -> List[Dict]:
        """
        Get track recommendations based on seeds and audio features.
        
        Args:
            seed_tracks: Track IDs to base recommendations on
            seed_artists: Artist IDs to base recommendations on
            seed_genres: Genres to base recommendations on
            target_energy: Target energy level (0.0-1.0)
            target_valence: Target mood/positivity (0.0-1.0)
            limit: Number of recommendations
        """
        try:
            params = {
                'limit': limit,
                'seed_tracks': seed_tracks,
                'seed_artists': seed_artists,
                'seed_genres': seed_genres
            }
            
            if target_energy is not None:
                params['target_energy'] = target_energy
            if target_valence is not None:
                params['target_valence'] = target_valence
            
            results = self.client.recommendations(**params)
            return results.get('tracks', [])
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def get_audio_features(self, track_id: str) -> Optional[Dict]:
        """
        Get audio features for a track (energy, valence, tempo, etc.).
        
        Useful for mood correlation analysis.
        """
        try:
            features = self.client.audio_features([track_id])
            return features[0] if features else None
        except Exception as e:
            logger.error(f"Error getting audio features: {e}")
            return None
    
    # ===== ANALYTICS =====
    
    def get_top_tracks(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict]:
        """
        Get user's top tracks.
        
        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
            limit: Number of tracks
        """
        try:
            results = self.client.current_user_top_tracks(
                time_range=time_range,
                limit=limit
            )
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Error getting top tracks: {e}")
            return []
    
    def get_top_artists(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict]:
        """Get user's top artists"""
        try:
            results = self.client.current_user_top_artists(
                time_range=time_range,
                limit=limit
            )
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Error getting top artists: {e}")
            return []
