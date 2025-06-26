"""
Error Handlers Module

This module contains error handlers for the NOUS application.
"""

import logging
import traceback
from flask import render_template, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with the Flask application

    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        logger.warning(f"404 error: {request.path}")

        # For API requests, return JSON
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'error': {
                    'code': 404,
                    'message': "The requested resource was not found"
                }
            }), 404

        # For regular requests, render the error template
        return render_template('error.html',
                              code=404,
                              title="Page Not Found",
                              message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        error_details = str(e)
        logger.error(f"500 error: {error_details}")
        logger.error(traceback.format_exc())

        # For API requests, return JSON
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'error': {
                    'code': 500,
                    'message': "Internal server error"
                }
            }), 500

        # For regular requests, render the error template
        return render_template('error.html',
                              code=500,
                              title="Internal Server Error",
                              message="The server encountered an error. Please try again later.",
                              details=traceback.format_exc() if app.debug else None), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all uncaught exceptions"""
        error_details = str(e)
        logger.error(f"Uncaught exception: {error_details}")
        logger.error(traceback.format_exc())

        # For API requests, return JSON
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'error': {
                    'code': 500,
                    'type': type(e).__name__,
                    'message': error_details
                }
            }), 500

        # For regular requests, render the error template
        return render_template('error.html',
                              code=500,
                              title="Server Error",
                              message=f"An unexpected error occurred: {error_details}",
                              details=traceback.format_exc() if app.debug else None), 500

    logger.info("Error handlers registered successfully")