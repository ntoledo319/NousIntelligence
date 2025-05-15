"""
Routes package for our app
"""

from routes.aa_routes import aa_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(aa_bp)