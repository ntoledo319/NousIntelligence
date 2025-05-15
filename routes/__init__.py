"""
Routes package for our app
"""

from routes.aa_routes import aa_bp
from routes.voice_mindfulness_routes import voice_mindfulness_bp
from routes.smart_shopping_routes import smart_shopping_bp
from routes.crisis_routes import crisis_bp
from routes.admin_routes import admin_bp, initialize_admin
from routes.beta_routes import beta_bp
from routes.setup_routes import setup_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(aa_bp)
    app.register_blueprint(voice_mindfulness_bp)
    app.register_blueprint(smart_shopping_bp)
    app.register_blueprint(crisis_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(beta_bp)
    app.register_blueprint(setup_bp)
    
    # Configure beta mode if enabled
    if app.config.get('ENABLE_BETA_MODE', False):
        from utils.beta_test_helper import configure_beta_mode
        configure_beta_mode(app)
    
    # Set up a function to run during the first request to initialize admin
    # Using a simpler approach that works with all Flask versions
    def setup_admin_user():
        with app.app_context():
            initialize_admin()
    
    # Run this immediately if the app is already set up
    setup_admin_user()