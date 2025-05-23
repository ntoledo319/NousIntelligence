#!/usr/bin/env python
"""
NOUS Personal Assistant - Launcher Script

This script provides a simple way to launch the NOUS application
consistently regardless of deployment environment.
"""
import os
import sys
import importlib
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for launching the NOUS application"""
    # Set environment variables if not already set
    os.environ.setdefault('PORT', '8080')
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    # Ensure we're using the right app file
    app_file = os.environ.get('NOUS_APP_FILE', 'app.py')
    app_var = os.environ.get('NOUS_APP_VAR', 'app')
    
    # In development mode, run directly through Flask
    if os.environ.get('FLASK_ENV') == 'development':
        logger.info(f"Starting app in development mode using {app_file}")
        app_module = app_file.replace('.py', '')
        try:
            module = importlib.import_module(app_module)
            app = getattr(module, app_var)
            port = int(os.environ.get('PORT', 8080))
            app.run(host='0.0.0.0', port=port, debug=True)
        except Exception as e:
            logger.error(f"Failed to start app in development mode: {str(e)}")
            sys.exit(1)
    else:
        # In production, use gunicorn if available
        try:
            import gunicorn
            logger.info(f"Starting app in production mode using Gunicorn with {app_file}")
            cmd = f"gunicorn --bind 0.0.0.0:{os.environ.get('PORT', 8080)} --workers=2 {app_module}:{app_var}"
            os.system(cmd)
        except ImportError:
            logger.warning("Gunicorn not available, using Flask development server")
            module = importlib.import_module(app_module)
            app = getattr(module, app_var)
            port = int(os.environ.get('PORT', 8080))
            app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    logger.info("NOUS Launcher starting up")
    main()