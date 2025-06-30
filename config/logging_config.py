"""
Centralized Logging Configuration
Fixes logging level and rotation issues identified in the investigation
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

def setup_logging(app=None, environment='production'):
    """
    Set up comprehensive logging configuration
    
    Args:
        app: Flask application instance (optional)
        environment: 'production' or 'development' (default: 'production')
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Determine log level based on environment
    if environment == 'development' or os.environ.get('DEBUG', '').lower() == 'true':
        log_level = logging.DEBUG
        log_format = '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s'
    else:
        log_level = logging.INFO
        log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    
    # Create formatters
    formatter = logging.Formatter(log_format)
    
    # Create handlers with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=10  # Keep 10 backup files
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Error log handler
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Security events handler
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=20
    )
    security_formatter = logging.Formatter(
        '[%(asctime)s] SECURITY %(levelname)s: %(message)s'
    )
    security_handler.setFormatter(security_formatter)
    security_handler.setLevel(logging.WARNING)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Configure Flask app logger if provided
    if app:
        app.logger.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        
        # Add security logger
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {environment} environment")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Log files: app.log, error.log, security.log")
    
    return logger


def get_security_logger():
    """Get dedicated security logger for authentication events"""
    return logging.getLogger('security')


def log_security_event(event_type, message, user_id=None, ip_address=None):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event ('auth_success', 'auth_failure', 'oauth_error', etc.)
        message: Detailed message
        user_id: User ID if applicable
        ip_address: Client IP address if applicable
    """
    security_logger = get_security_logger()
    
    log_entry = f"{event_type.upper()}: {message}"
    if user_id:
        log_entry += f" | User: {user_id}"
    if ip_address:
        log_entry += f" | IP: {ip_address}"
    
    security_logger.warning(log_entry)


def log_oauth_event(event_type, message, error_details=None):
    """
    Log OAuth-specific events with appropriate detail level
    
    Args:
        event_type: 'oauth_init', 'oauth_redirect', 'oauth_callback', 'oauth_error'
        message: User-friendly message
        error_details: Technical error details (not logged in production)
    """
    logger = logging.getLogger('oauth')
    security_logger = get_security_logger()
    
    # Log basic event
    logger.info(f"OAuth {event_type}: {message}")
    
    # Log security event if it's an error
    if event_type == 'oauth_error':
        security_logger.warning(f"OAuth Error: {message}")
        
        # Log technical details only in development
        if os.environ.get('DEBUG', '').lower() == 'true' and error_details:
            logger.debug(f"OAuth Error Details: {error_details}")