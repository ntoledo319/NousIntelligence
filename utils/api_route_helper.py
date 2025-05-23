"""
API Route Helper

This module provides utilities to standardize API route creation and documentation.
It ensures consistent versioning, documentation, and error handling for API endpoints.
"""

import functools
import logging
import json
from typing import Callable, Dict, Any, Optional, Union, List
from flask import jsonify, request, Blueprint, Response, current_app

from utils.url_utils import normalize_path

# Configure logging
logger = logging.getLogger(__name__)

def api_route(blueprint: Blueprint, rule: str, **options):
    """
    Decorator for API routes with standardized response handling and documentation
    
    Args:
        blueprint: Flask blueprint to attach the route to
        rule: URL rule for the route
        **options: Additional options for route registration
        
    Returns:
        Decorator function
    """
    # Extract documentation information from options
    api_doc = options.pop('api_doc', {})
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Call the original route function
                result = func(*args, **kwargs)
                
                # If result is already a Response, return it directly
                if isinstance(result, Response):
                    return result
                
                # Convert dict to JSON response with standard structure
                if isinstance(result, dict):
                    # If success/error already set, use as is
                    if 'success' not in result:
                        result['success'] = True
                    
                    return jsonify(result)
                
                # For other return types, wrap in a standard response
                return jsonify({
                    'success': True,
                    'data': result
                })
                
            except Exception as e:
                # Log the error
                logger.exception(f"API Error in {request.path}: {str(e)}")
                
                # Return standardized error response
                status_code = getattr(e, 'code', 500)
                error_message = str(e)
                
                # In production, hide internal error details
                if not current_app.debug and status_code == 500:
                    error_message = "Internal server error"
                
                return jsonify({
                    'success': False,
                    'error': error_message
                }), status_code
        
        # Add API documentation to the route function
        wrapper.api_doc = api_doc
        
        # Normalize the rule to ensure consistency
        normalized_rule = normalize_path(rule)
        
        # Register the route with the blueprint
        endpoint = options.pop('endpoint', None)
        blueprint.add_url_rule(normalized_rule, endpoint, wrapper, **options)
        
        return wrapper
    
    return decorator

def create_api_blueprint(name: str, import_name: str, url_prefix: str, 
                         version: str = "v1") -> Blueprint:
    """
    Create an API blueprint with standardized naming and versioning
    
    Args:
        name: Name of the blueprint
        import_name: Import name for the blueprint
        url_prefix: URL prefix for the blueprint
        version: API version string
        
    Returns:
        Configured Flask blueprint
    """
    # Normalize the URL prefix
    normalized_prefix = normalize_path(url_prefix)
    
    # Add version to URL prefix if not already present
    if not normalized_prefix.startswith(f"/api/{version}"):
        if normalized_prefix == "/api":
            normalized_prefix = f"/api/{version}"
        elif normalized_prefix.startswith("/api/"):
            # Don't modify if it already has a version
            if not any(normalized_prefix.startswith(f"/api/v{i}") for i in range(1, 10)):
                normalized_prefix = f"/api/{version}{normalized_prefix[5:]}"
    
    # Create the blueprint
    blueprint = Blueprint(name, import_name, url_prefix=normalized_prefix)
    
    # Add version info to blueprint for documentation
    blueprint.api_version = version
    
    return blueprint

def register_api_error_handlers(blueprint: Blueprint) -> None:
    """
    Register standardized error handlers for an API blueprint
    
    Args:
        blueprint: Flask blueprint to register error handlers with
    """
    @blueprint.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Bad request"
        }), 400
    
    @blueprint.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Unauthorized"
        }), 401
    
    @blueprint.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Forbidden"
        }), 403
    
    @blueprint.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Resource not found"
        }), 404
    
    @blueprint.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Method not allowed"
        }), 405
    
    @blueprint.errorhandler(429)
    def handle_too_many_requests(e):
        return jsonify({
            'success': False,
            'error': str(e) or "Too many requests"
        }), 429
    
    @blueprint.errorhandler(500)
    def handle_server_error(e):
        # Log the error
        logger.exception(f"Server error in API: {str(e)}")
        
        # Hide details in production
        if current_app.debug:
            error_message = str(e) or "Internal server error"
        else:
            error_message = "Internal server error"
            
        return jsonify({
            'success': False,
            'error': error_message
        }), 500