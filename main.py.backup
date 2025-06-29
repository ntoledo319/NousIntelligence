"""
NOUS Personal Assistant - Optimized Production Entry Point
Fast startup, minimal overhead, maximum performance
"""
import os
import sys
import logging
from pathlib import Path

# Set production environment variables for optimal performance
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('WERKZEUG_RUN_MAIN', 'true')

# Create required directories
Path('logs').mkdir(exist_ok=True)
Path('flask_session').mkdir(exist_ok=True)
Path('static').mkdir(exist_ok=True)
Path('templates').mkdir(exist_ok=True)

# Configure optimized logging
logging.basicConfig(
    level=logging.WARNING,  # Reduced logging for performance
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', mode='a')
    ]
)

def main():
    """Optimized main entry point"""
    try:
        # Try optimized app first, fallback to regular app
        try:
            from app_optimized import app
            logging.info("Using optimized application")
        except ImportError:
            from app import create_app
            app = create_app()
            logging.info("Using standard application")
        
        # Get configuration from environment
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Production startup message
        print(f"🚀 NOUS Assistant starting on {host}:{port}")
        
        # Run with production settings
        app.run(
            host=host, 
            port=port, 
            debug=False,
            use_reloader=False,  # Disable reloader for production
            threaded=True        # Enable threading for better performance
        )
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
