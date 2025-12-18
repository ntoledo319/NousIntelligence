import sys
import os
from sqlalchemy import inspect

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.spotify_janitor import create_sanitized_app
from database import db

app = create_sanitized_app()

with app.app_context():
    print("🔄 Checking Database for Spotify Tables...")
    try:
        # Ensure instance directory exists
        instance_path = app.config.get('INSTANCE_PATH', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if "spotify_tokens" in tables:
            print("✅ Table 'spotify_tokens' already exists.")
        else:
            print("⚠️ Table 'spotify_tokens' missing. Attempting creation...")
            try:
                # Import the model to ensure SQLAlchemy knows about it
                from models.spotify_models import SpotifyToken
                db.create_all()
                print("✅ Successfully created 'spotify_tokens' table.")
            except Exception as e:
                print(f"❌ Failed to create table: {e}")
                print("   (Fallback: FileTokenStore will be used automatically by the app)")
    except Exception as e:
        print(f"⚠️ Database check failed: {e}")
        print("   (Fallback: FileTokenStore will be used automatically by the app)")
