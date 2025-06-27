"""
Error Handler Module

This module provides error handling functionality for the application.

@module utils.error_handler
@description Error handling and custom error pages
"""

import logging
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Register error handlers for the application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"400 error: {error}")
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html', error=str(error)), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        logger.warning(f"401 error: {error}")
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource'
            }), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"403 error: {error}")
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        logger.warning(f"404 error: {error}")
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error errors"""
        logger.error(f"500 error: {error}", exc_info=True)
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        # If it's an HTTPException, use the built-in handler
        if isinstance(error, HTTPException):
            if request.path.startswith('/api'):
                return jsonify({
                    'error': error.name,
                    'message': error.description
                }), error.code
            return render_template(f'errors/{error.code}.html'), error.code
            
        # For non-HTTP exceptions, treat as 500 Internal Server Error
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500

    logger.info("Registered application error handlers") 