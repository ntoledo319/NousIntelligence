# Import routes to make them available for registration with Flask app
from routes.spotify_visualization import spotify_viz

def register_blueprints(app):
    """Register all blueprint modules with the Flask application"""
    app.register_blueprint(spotify_viz)