"""
NOUS Personal Assistant - Application Entry Point

This module provides the Flask application instance for deployment.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

# Create and configure the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 10,
    "pool_timeout": 20,
    "connect_args": {
        "connect_timeout": 10,
        "application_name": "NOUS",
    },
}

# Add ProxyFix middleware for proper handling of forwarded requests
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions
db.init_app(app)

# Import and register blueprints
with app.app_context():
    # Import models
    from models.user import User
    
    # Create database tables
    db.create_all()
    
    # Register blueprints
    from routes.main import main_bp
    from routes.dashboard import dashboard_bp
    from routes.smart_shopping_routes import smart_shopping_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(smart_shopping_bp)
    
    # Register error handlers
    from error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Setup monitoring
    from monitoring import setup_monitoring
    setup_monitoring(app)

# Run the app when executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)