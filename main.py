"""
NOUS Personal Assistant - Production Entry Point
"""
import os
import logging
from pathlib import Path

# Create logs directory
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

if __name__ == "__main__":
    try:
        from app import create_app
        app = create_app()
        
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        raise
