"""
Error Handler Module

This module provides standardized error handling for the application.
It registers error handlers for common HTTP errors and provides utility
functions for creating consistent error responses.

@module utils.error_handler
@author NOUS Development Team
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from flask import jsonify, request, render_template
from werkzeug.exceptions import HTTPException

# Configure logger
logger = logging.getLogger(__name__)

class APIError(Exception):
    """
    Custom exception for API errors that can be raised from anywhere in the application.
    Will be caught by the error handler and converted to a proper API response.
    """
    def __init__(self, message, status_code=400, error_code=None, title=None, details=None):
        """
        Initialize API error with provided information.
        
        Args:
            message: Error message
            status_code: HTTP status code (default: 400)
            error_code: Application-specific error code (default: derived from status_code)
            title: Error title (default: derived from status code)
            details: Additional error details (default: None)
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"
        self.title = title or {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            429: "Too Many Requests",
            500: "Internal Server Error"
        }.get(status_code, "Error")
        self.details = details
        
        super().__init__(self.message)

def handle_error(error: Union[APIError, HTTPException, Exception]) -> tuple:
    """
    Standardized error handler that creates consistent error responses
    
    Args:
        error: The exception to handle
        
    Returns:
        A tuple of (response_json, status_code)
    """
    # Get client IP for logging
    ip_address = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip() \
        if request.headers.getlist("X-Forwarded-For") else request.remote_addr
    
    # Check if this is an API request
    is_api_request = request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json'
    
    # Handle our custom API errors
    if isinstance(error, APIError):
        logger.warning(f"API Error ({error.status_code}): {error.message} - IP: {ip_address}")
        
        if is_api_request:
            response = {
                "success": False,
                "error": error.error_code,
                "message": error.message
            }
            
            # Add details if available
            if error.details:
                response["details"] = error.details
                
            return jsonify(response), error.status_code
        else:
            return render_template('errors/error.html', 
                                  status_code=error.status_code,
                                  title=error.title,
                                  message=error.message), error.status_code
    
    # Handle Werkzeug HTTP exceptions
    if isinstance(error, HTTPException):
        logger.warning(f"HTTP Error ({error.code}): {error.description} - IP: {ip_address}")
        
        if is_api_request:
            response = {
                "success": False,
                "error": f"HTTP_{error.code}",
                "message": error.description
            }
            return jsonify(response), error.code
        else:
            title = {
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                405: "Method Not Allowed",
                429: "Too Many Requests",
                500: "Internal Server Error"
            }.get(error.code, "Error")
            return render_template('errors/error.html', 
                                  status_code=error.code,
                                  title=title,
                                  message=error.description), error.code
    
    # Handle unexpected exceptions
    logger.error(f"Unexpected Error: {str(error)} - IP: {ip_address}")
    logger.error(traceback.format_exc())
    
    # In production, don't expose internal error details
    is_production = request.headers.get('X-Environment') == 'production'
    
    if is_api_request:
        response = {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred"
        }
        
        # Add error details in non-production environments
        if not is_production:
            response["details"] = {
                "exception": str(error),
                "traceback": traceback.format_exc().split("\n")
            }
            
        return jsonify(response), 500
    else:
        return render_template('errors/error.html', 
                              status_code=500,
                              title="Internal Server Error",
                              message="An unexpected error occurred on the server."), 500

def register_error_handlers(app):
    """
    Register error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return handle_error(error)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        return handle_error(error)
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        return handle_error(error)
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return handle_error(error)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        return handle_error(error)
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors"""
        return handle_error(error)
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 Internal Server Error errors"""
        # Log the error with traceback for debugging
        logger.error(f"Internal server error: {str(error)}")
        logger.error(traceback.format_exc())
        
        return handle_error(error)
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        return handle_error(error)

def validation_error(message: str, field: Optional[str] = None) -> APIError:
    """
    Create a validation error
    
    Args:
        message: Error message
        field: Field that failed validation
        
    Returns:
        APIError instance
    """
    details = {"field": field} if field else None
    return APIError(
        message=message,
        status_code=400,
        error_code="VALIDATION_ERROR",
        details=details
    )

def authentication_error(message: str = "Authentication required") -> APIError:
    """
    Create an authentication error
    
    Args:
        message: Error message
        
    Returns:
        APIError instance
    """
    return APIError(
        message=message,
        status_code=401,
        error_code="AUTHENTICATION_ERROR"
    )

def authorization_error(message: str = "Not authorized") -> APIError:
    """
    Create an authorization error
    
    Args:
        message: Error message
        
    Returns:
        APIError instance
    """
    return APIError(
        message=message,
        status_code=403,
        error_code="AUTHORIZATION_ERROR"
    )

def not_found_error(resource_type: str, resource_id: str) -> APIError:
    """
    Create a not found error
    
    Args:
        resource_type: Type of resource that wasn't found
        resource_id: ID of resource that wasn't found
        
    Returns:
        APIError instance
    """
    return APIError(
        message=f"{resource_type} not found: {resource_id}",
        status_code=404,
        error_code="NOT_FOUND_ERROR",
        details={
            "resource_type": resource_type,
            "resource_id": resource_id
        }
    )

def rate_limit_error(retry_after: int) -> APIError:
    """
    Create a rate limit error
    
    Args:
        retry_after: Seconds until retry is allowed
        
    Returns:
        APIError instance
    """
    return APIError(
        message="Rate limit exceeded",
        status_code=429,
        error_code="RATE_LIMIT_ERROR",
        details={
            "retry_after": retry_after
        }
    ) 