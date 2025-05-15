"""
Routes package for our app
"""

from routes.aa_routes import aa_bp
from routes.voice_mindfulness_routes import voice_mindfulness_bp
from routes.smart_shopping_routes import smart_shopping_bp
from routes.crisis_routes import crisis_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(aa_bp)
    app.register_blueprint(voice_mindfulness_bp)
    app.register_blueprint(smart_shopping_bp)
    app.register_blueprint(crisis_bp)