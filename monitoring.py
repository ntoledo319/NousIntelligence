"""
NOUS Personal Assistant - Monitoring Module

This module provides robust error monitoring and logging for the NOUS application.
It captures errors, logs them properly, and helps with debugging.
"""

import logging
import sys
import os
import traceback
from datetime import datetime
from flask import request, g

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nous_errors.log')
    ]
)

# Create a logger for this module
logger = logging.getLogger(__name__)

class ErrorMonitor:
    """Error monitoring and logging class for NOUS"""
    
    @staticmethod
    def setup_error_logging(app):
        """Set up error logging for the Flask application
        
        Args:
            app: Flask application instance
        """
        # Configure app-level logging
        if not app.debug:
            # In production, log to file
            handler = logging.FileHandler('nous_errors.log')
            handler.setLevel(logging.ERROR)
            app.logger.addHandler(handler)
        
        # Register error handlers
        @app.errorhandler(Exception)
        def handle_exception(e):
            """Log all uncaught exceptions"""
            ErrorMonitor.log_exception(e)
            return ErrorMonitor.render_error_response(e)
        
        # Log requests
        @app.before_request
        def log_request():
            """Log incoming requests"""
            g.request_start_time = datetime.now()
            logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
        
        @app.after_request
        def log_response(response):
            """Log responses and their timing"""
            if hasattr(g, 'request_start_time'):
                duration = datetime.now() - g.request_start_time
                logger.info(f"Response: {response.status_code} in {duration.total_seconds():.3f}s")
            return response
    
    @staticmethod
    def log_exception(exception):
        """Log detailed information about an exception
        
        Args:
            exception: The exception to log
        """
        # Get current request information if available
        request_info = ""
        try:
            if request:
                request_info = f"Request: {request.method} {request.path}"
        except:
            pass
        
        # Log the exception
        error_details = {
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'traceback': traceback.format_exc(),
            'request_info': request_info,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"Exception occurred: {error_details['error_type']}: {error_details['error_message']}")
        logger.error(f"Request info: {error_details['request_info']}")
        logger.error(f"Traceback:\n{error_details['traceback']}")
        
        # Also write to a structured error log
        ErrorMonitor._write_error_log(error_details)
        
        return error_details
    
    @staticmethod
    def _write_error_log(error_details):
        """Write error details to a structured log file
        
        Args:
            error_details: Dictionary containing error information
        """
        error_log_file = "detailed_errors.log"
        try:
            with open(error_log_file, 'a') as f:
                f.write("-" * 80 + "\n")
                f.write(f"TIMESTAMP: {error_details['timestamp']}\n")
                f.write(f"ERROR TYPE: {error_details['error_type']}\n")
                f.write(f"ERROR MESSAGE: {error_details['error_message']}\n")
                f.write(f"REQUEST INFO: {error_details['request_info']}\n")
                f.write("TRACEBACK:\n")
                f.write(error_details['traceback'])
                f.write("-" * 80 + "\n\n")
        except Exception as e:
            logger.error(f"Failed to write to error log: {str(e)}")
    
    @staticmethod
    def render_error_response(exception):
        """Generate an appropriate error response
        
        Args:
            exception: The exception that occurred
        
        Returns:
            Flask response with error details
        """
        from flask import render_template, jsonify
        
        # Determine error code
        code = getattr(exception, 'code', 500)
        
        # For API requests, return JSON
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'error': {
                    'code': code,
                    'type': type(exception).__name__,
                    'message': str(exception)
                }
            }), code
        
        # For regular requests, render the error template
        try:
            return render_template(
                'error.html',
                code=code,
                title="Internal Server Error" if code == 500 else type(exception).__name__,
                message=str(exception),
                details=traceback.format_exc() if code == 500 else None
            ), code
        except:
            # Fallback to a simple error page if template rendering fails
            return f"""
            <html>
                <head><title>Error {code}</title></head>
                <body>
                    <h1>Error {code}</h1>
                    <p>{str(exception)}</p>
                    <a href="/">Return to Home</a>
                </body>
            </html>
            """, code

def setup_monitoring(app):
    """Set up monitoring for the Flask application
    
    Args:
        app: Flask application instance
    """
    ErrorMonitor.setup_error_logging(app)
    logger.info("Error monitoring initialized")