"""
@module error_handler
@description Standardized error handling for consistent error responses
@author AI Assistant
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

# Configure logger
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API error class with status code and error details"""
    
    def __init__(self, 
                 message: str, 
                 status_code: int = 400, 
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize API error
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"
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
    
    # Handle our custom API errors
    if isinstance(error, APIError):
        logger.warning(f"API Error ({error.status_code}): {error.message} - IP: {ip_address}")
        response = {
            "success": False,
            "error": error.error_code,
            "message": error.message
        }
        
        # Add details if available
        if error.details:
            response["details"] = error.details
            
        return jsonify(response), error.status_code
    
    # Handle Werkzeug HTTP exceptions
    if isinstance(error, HTTPException):
        logger.warning(f"HTTP Error ({error.code}): {error.description} - IP: {ip_address}")
        response = {
            "success": False,
            "error": f"HTTP_{error.code}",
            "message": error.description
        }
        return jsonify(response), error.code
    
    # Handle unexpected exceptions
    logger.error(f"Unexpected Error: {str(error)} - IP: {ip_address}")
    logger.error(traceback.format_exc())
    
    # In production, don't expose internal error details
    is_production = request.headers.get('X-Environment') == 'production'
    
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

def register_error_handlers(app):
    """
    Register error handlers with a Flask application
    
    Args:
        app: The Flask application
    """
    # Register handler for our custom API errors
    app.register_error_handler(APIError, handle_error)
    
    # Register handlers for common HTTP errors
    for error_code in [400, 401, 403, 404, 405, 429, 500]:
        app.register_error_handler(error_code, handle_error)
    
    # Register catch-all handler for other exceptions
    app.register_error_handler(Exception, handle_error)

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