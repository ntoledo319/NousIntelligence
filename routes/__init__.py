"""
Routes package for our app
"""

from routes.aa_routes import aa_bp
from routes.voice_mindfulness_routes import voice_mindfulness_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(aa_bp)
    app.register_blueprint(voice_mindfulness_bp)