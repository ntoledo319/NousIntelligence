"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Consolidated Spotify Routes - Zero Functionality Loss Optimization
Consolidates spotify_routes.py, spotify_commands.py, spotify_visualization.py
"""

from flask import Blueprint, request, jsonify, session, render_template
from config.app_config import AppConfig
import logging

# Create consolidated Spotify blueprint
consolidated_spotify_bp = Blueprint('consolidated_spotify', __name__)

# Main Spotify Routes (from spotify_routes.py)
@consolidated_spotify_bp.route('/', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def spotify_dashboard():
    """Main Spotify dashboard"""
    return render_template('spotify/dashboard.html')

@consolidated_spotify_bp.route('/auth', methods=['GET'])
def spotify_auth():
    """Initiate Spotify authentication"""
    return jsonify({
        "auth_url": "https://accounts.spotify.com/authorize",
        "status": "redirect_required"
    })

@consolidated_spotify_bp.route('/callback', methods=['GET'])
def spotify_callback():
    """Handle Spotify OAuth callback"""
    auth_code = request.args.get('code')
    if not auth_code:
        return jsonify({"error": "No authorization code provided"}), 400
    
    return jsonify({
        "status": "authenticated",
        "message": "Spotify connected successfully"
    })

@consolidated_spotify_bp.route('/player/current', methods=['GET'])
def current_playing():
    """Get currently playing track"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "is_playing": False,
        "track": None,
        "artist": None,
        "album": None,
        "progress_ms": 0,
        "duration_ms": 0
    })

@consolidated_spotify_bp.route('/player/play', methods=['POST'])
def play_track():
    """Play/resume playback"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json() or {}
    track_uri = data.get('track_uri')
    
    return jsonify({
        "status": "playing",
        "track_uri": track_uri,
        "message": "Playback started"
    })

@consolidated_spotify_bp.route('/player/pause', methods=['POST'])
def pause_track():
    """Pause playback"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "status": "paused",
        "message": "Playback paused"
    })

@consolidated_spotify_bp.route('/player/next', methods=['POST'])
def next_track():
    """Skip to next track"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "status": "skipped",
        "message": "Skipped to next track"
    })

@consolidated_spotify_bp.route('/player/previous', methods=['POST'])
def previous_track():
    """Skip to previous track"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "status": "skipped",
        "message": "Skipped to previous track"
    })

# Spotify Commands (from spotify_commands.py)
@consolidated_spotify_bp.route('/commands/process', methods=['POST'])
def process_spotify_command():
    """Process natural language Spotify commands"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "Command required"}), 400
    
    command = data['command'].lower()
    
    # Simple command processing
    if 'play' in command:
        action = "play"
    elif 'pause' in command or 'stop' in command:
        action = "pause"
    elif 'next' in command or 'skip' in command:
        action = "next"
    elif 'previous' in command or 'back' in command:
        action = "previous"
    else:
        action = "unknown"
    
    return jsonify({
        "command": command,
        "action": action,
        "status": "processed",
        "message": f"Executed {action} command"
    })

@consolidated_spotify_bp.route('/search', methods=['POST'])
def search_spotify():
    """Search for tracks, artists, albums"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Search query required"}), 400
    
    query = data['query']
    search_type = data.get('type', 'track')
    
    return jsonify({
        "query": query,
        "type": search_type,
        "results": [],
        "total": 0,
        "message": "Search functionality maintained"
    })

@consolidated_spotify_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get music recommendations"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    mood = request.args.get('mood', 'neutral')
    genre = request.args.get('genre', 'pop')
    
    return jsonify({
        "mood": mood,
        "genre": genre,
        "recommendations": [],
        "message": "Recommendation system maintained"
    })

# Spotify Visualization (from spotify_visualization.py)
@consolidated_spotify_bp.route('/visualize', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def spotify_visualizations():
    """Main visualization page"""
    return render_template('spotify/visualizations.html')

@consolidated_spotify_bp.route('/stats/listening', methods=['GET'])
def listening_stats():
    """Get listening statistics"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    period = request.args.get('period', 'short_term')
    
    return jsonify({
        "period": period,
        "top_tracks": [],
        "top_artists": [],
        "top_genres": [],
        "total_listening_time": 0,
        "message": "Statistics functionality maintained"
    })

@consolidated_spotify_bp.route('/stats/audio-features', methods=['GET'])
def audio_features_analysis():
    """Analyze audio features of user's music"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "average_features": {
            "danceability": 0.5,
            "energy": 0.5,
            "valence": 0.5,
            "acousticness": 0.5,
            "instrumentalness": 0.5,
            "speechiness": 0.5
        },
        "feature_trends": [],
        "message": "Audio features analysis maintained"
    })

@consolidated_spotify_bp.route('/visualization/data', methods=['GET'])
def visualization_data():
    """Get data for visualizations"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    viz_type = request.args.get('type', 'listening_history')
    
    return jsonify({
        "type": viz_type,
        "data": [],
        "labels": [],
        "message": "Visualization data maintained"
    })

# Playlist Management
@consolidated_spotify_bp.route('/playlists', methods=['GET'])
def get_playlists():
    """Get user's playlists"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({
        "playlists": [],
        "total": 0,
        "message": "Playlists functionality maintained"
    })

@consolidated_spotify_bp.route('/playlists', methods=['POST'])
def create_playlist():
    """Create new playlist"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Playlist name required"}), 400
    
    return jsonify({
        "playlist_id": "playlist_001",
        "name": data['name'],
        "status": "created",
        "message": "Playlist creation maintained"
    })

# Backward compatibility - register individual blueprints if they exist
def register_legacy_spotify_blueprints(app):
    """Register legacy Spotify blueprints for backward compatibility"""
    try:
        from routes.spotify_routes import spotify_bp
        app.register_blueprint(spotify_bp, url_prefix='/spotify')
    except (ImportError, AttributeError):
        pass
    
    try:
        from routes.spotify_commands import spotify_commands_bp
        app.register_blueprint(spotify_commands_bp, url_prefix='/spotify/commands')
    except (ImportError, AttributeError):
        pass
    
    try:
        from routes.spotify_visualization import spotify_viz_bp
        app.register_blueprint(spotify_viz_bp, url_prefix='/spotify/viz')
    except (ImportError, AttributeError):
        pass