from flask import Blueprint, jsonify, request, render_template, session
from flask_login import current_user, login_required
import logging
from utils.spotify_helper import get_spotify_client
from utils.spotify_visualizer import (
    generate_top_artists_chart,
    generate_top_tracks_chart,
    generate_genre_chart,
    generate_listening_history_chart,
    generate_audio_features_radar_chart,
    generate_playlist_mood_analysis,
    generate_spotify_listening_report,
    generate_audio_feature_comparison
)
import os

# Get Spotify credentials from environment variables
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.environ.get("SPOTIFY_REDIRECT_URI") or "http://localhost:5000/callback/spotify"

spotify_viz = Blueprint('spotify_viz', __name__)

@spotify_viz.route("/viz/spotify/report")
@login_required
def spotify_report_page():
    """Render the main Spotify visualization report page"""
    return render_template("spotify_report.html")

@spotify_viz.route("/api/spotify/visualization/report")
@login_required
def get_spotify_report():
    """Generate a full Spotify listening report with multiple visualizations"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        # Generate the report with all visualizations
        report = generate_spotify_listening_report(spotify)
        
        if not report:
            return jsonify({"error": "Could not generate report"}), 400
            
        return jsonify({"success": True, "report": report})
    except Exception as e:
        logging.error(f"Error generating Spotify report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/artists")
@login_required
def get_top_artists_chart():
    """Generate chart of top artists"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    time_range = request.args.get("time_range", "medium_term")
    limit = int(request.args.get("limit", 10))
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img = generate_top_artists_chart(spotify, time_range, limit)
        
        if not img:
            return jsonify({"error": "Could not generate chart"}), 400
            
        return jsonify({"success": True, "image": img})
    except Exception as e:
        logging.error(f"Error generating top artists chart: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/tracks")
@login_required
def get_top_tracks_chart():
    """Generate chart of top tracks"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    time_range = request.args.get("time_range", "medium_term")
    limit = int(request.args.get("limit", 10))
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img = generate_top_tracks_chart(spotify, time_range, limit)
        
        if not img:
            return jsonify({"error": "Could not generate chart"}), 400
            
        return jsonify({"success": True, "image": img})
    except Exception as e:
        logging.error(f"Error generating top tracks chart: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/genres")
@login_required
def get_genre_chart():
    """Generate chart of top genres"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    limit = int(request.args.get("limit", 10))
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img = generate_genre_chart(spotify, limit)
        
        if not img:
            return jsonify({"error": "Could not generate chart"}), 400
            
        return jsonify({"success": True, "image": img})
    except Exception as e:
        logging.error(f"Error generating genre chart: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/history")
@login_required
def get_listening_history_chart():
    """Generate chart of listening history"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    limit = int(request.args.get("limit", 50))
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img = generate_listening_history_chart(spotify, limit)
        
        if not img:
            return jsonify({"error": "Could not generate chart"}), 400
            
        return jsonify({"success": True, "image": img})
    except Exception as e:
        logging.error(f"Error generating listening history chart: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/track-features")
@login_required
def get_track_features_chart():
    """Generate radar chart of audio features for a track"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    track_id = request.args.get("track_id")
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img, track_info = generate_audio_features_radar_chart(spotify, track_id)
        
        if not img:
            return jsonify({"error": "Could not generate chart"}), 400
            
        return jsonify({
            "success": True, 
            "image": img,
            "track_info": track_info
        })
    except Exception as e:
        logging.error(f"Error generating track features chart: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/playlist-analysis")
@login_required
def get_playlist_analysis():
    """Generate analysis of a playlist's mood and characteristics"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters
    playlist_id = request.args.get("playlist_id")
    
    if not playlist_id:
        return jsonify({"error": "Playlist ID required"}), 400
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        analysis = generate_playlist_mood_analysis(spotify, playlist_id)
        
        if not analysis:
            return jsonify({"error": "Could not generate analysis"}), 400
            
        return jsonify({
            "success": True, 
            "analysis": analysis
        })
    except Exception as e:
        logging.error(f"Error generating playlist analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@spotify_viz.route("/api/spotify/visualization/compare-tracks")
@login_required
def compare_tracks():
    """Generate comparison of audio features between multiple tracks"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get parameters from JSON body
    data = request.json
    if not data or 'track_ids' not in data:
        return jsonify({"error": "Track IDs required"}), 400
    
    track_ids = data.get('track_ids', [])
    track_names = data.get('track_names')
    
    if not track_ids:
        return jsonify({"error": "At least one track ID required"}), 400
    
    # Get Spotify client
    spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                                 SPOTIFY_REDIRECT, current_user.id)
    
    if not spotify:
        return jsonify({"error": "Spotify connection required"}), 400
    
    try:
        img = generate_audio_feature_comparison(spotify, track_ids, track_names)
        
        if not img:
            return jsonify({"error": "Could not generate comparison"}), 400
            
        return jsonify({
            "success": True, 
            "image": img
        })
    except Exception as e:
        logging.error(f"Error generating track comparison: {str(e)}")
        return jsonify({"error": str(e)}), 500