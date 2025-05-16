# Import routes to make them available for registration with Flask app
from routes.spotify_visualization import spotify_viz
from routes.voice_emotion_routes import voice_emotion_bp

def register_blueprints(app):
    """Register all blueprint modules with the Flask application"""
    app.register_blueprint(spotify_viz)
    app.register_blueprint(voice_emotion_bp)