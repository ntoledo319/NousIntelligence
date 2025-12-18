import sys
import os
from flask import Flask

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sanitized_app():
    """
    Creates a Flask app that ONLY loads the working Spotify stack
    and critical auth routes, ignoring broken legacy modules.
    """
    from database import db
    
    app = Flask(__name__)
    
    # Load basic config
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
    app.config['INSTANCE_PATH'] = 'instance'

    # Initialize extensions
    try:
        db.init_app(app)
        try:
            from extensions import login_manager
            login_manager.init_app(app)
        except (ImportError, AttributeError):
            pass  # login_manager is optional
    except Exception as e:
        print(f"Warning: Extension init issues: {e}")

    # --- REGISTRATION BLOCK ---
    # We manually register ONLY the blueprints we just fixed/created.
    # This bypasses the 'haunted' routes/__init__.py if it tries to load broken files.
    
    try:
        from routes.spotify_v2_routes import spotify_v2_bp
        from routes.consolidated_spotify_routes import legacy_spotify_bp
        
        app.register_blueprint(spotify_v2_bp, url_prefix='/api/v2/spotify')
        app.register_blueprint(legacy_spotify_bp) # Compat layer
        print("✅ Spotify Subsystem Registered Successfully")
    except Exception as e:
        print(f"❌ CRITICAL: Could not register Spotify Subsystem: {e}")
        sys.exit(1)

    return app

if __name__ == "__main__":
    print("🧹 Starting Spotify Janitor Instance...")
    print("   (Running only Spotify routes to isolate syntax errors in other files)")
    app = create_sanitized_app()
    app.run(debug=True, port=5000)
