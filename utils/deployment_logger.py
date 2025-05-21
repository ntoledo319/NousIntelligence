"""
Deployment Logging Module

This module configures enhanced logging for deployment environments
to ensure better visibility into application issues.
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Max log file size (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Keep 5 backup log files
BACKUP_COUNT = 5

def configure_deployment_logging(app=None):
    """
    Configure deployment-specific logging
    
    Args:
        app: Optional Flask application instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create deployment log file with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    deployment_log = logs_dir / f'deployment_{timestamp}.log'
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        deployment_log,
        maxBytes=MAX_LOG_SIZE, 
        backupCount=BACKUP_COUNT
    )
    
    # Set log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Configure root logger if no app provided
    if app is None:
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        # Also log to stdout for visibility
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)
        
        # Set level based on environment
        if os.environ.get('FLASK_ENV') == 'development':
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
            
        return root_logger
    
    # Configure Flask app logger
    app.logger.addHandler(file_handler)
    
    # Log all uncaught exceptions
    @app.errorhandler(Exception)
    def log_exception(e):
        app.logger.exception("Unhandled exception: %s", str(e))
        raise e
    
    # Log key application events
    app.logger.info(f"Application configured for deployment in {os.environ.get('FLASK_ENV', 'production')} environment")
    
    return app.logger

def log_deployment_event(event_type, message, level=logging.INFO):
    """
    Log a deployment-specific event
    
    Args:
        event_type: Type of event (e.g., 'startup', 'config', 'database')
        message: Event message
        level: Logging level (default: INFO)
    """
    logger = logging.getLogger('deployment')
    
    # Format message with event type
    formatted_message = f"[{event_type.upper()}] {message}"
    
    # Log at appropriate level
    logger.log(level, formatted_message)
    
    # Also return the message for convenience
    return formatted_message

# Configure the module logger
deployment_logger = logging.getLogger('deployment')