from flask import Flask
from src.infrastructure.di_container import setup_dependencies
from src.infrastructure.cache import cache
from utils.security_headers import init_security_headers
from utils.csrf_protection import init_csrf
from utils.env_loader import load_environment, get_config
import logging

def create_app(config_name='development'):
    """Application factory"""
    # Load environment
    load_environment()
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.update(config)
    
    # Initialize extensions
    init_security_headers(app)
    init_csrf(app)
    
    # Setup dependencies
    setup_dependencies()
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize NOUS core runtime (event bus + semantic index + policy)
    try:
        from services.runtime_service import init_runtime
        init_runtime(app)
    except Exception:
        pass
    
    # Register API v2 blueprint
    try:
        from routes.api_v2 import api_v2_bp
        app.register_blueprint(api_v2_bp, url_prefix="/api/v2")
    except Exception:
        pass
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from src.presentation.api.health import health_bp
    from src.presentation.api.auth import auth_bp
    from src.presentation.api.mental_health import mental_health_bp
    from src.presentation.api.tasks import tasks_bp
    from src.presentation.api.family import family_bp
    from src.presentation.api.analytics import analytics_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mental_health_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(analytics_bp)

def setup_logging(app):
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
