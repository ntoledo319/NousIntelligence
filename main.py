"""
NOUS Personal Assistant - Production Entry Point
Bulletproof deployment configuration
"""
import os
import sys
import logging
from pathlib import Path

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point with error handling"""
    try:
        logger.info("Starting NOUS Personal Assistant...")
        
        # Import app after logging is configured
        from app import create_app
        app = create_app()
        
        # Get port and host from environment with fallbacks
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_ENV', 'production') == 'development'
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Start the app
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
