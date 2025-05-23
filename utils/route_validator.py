"""
Route Validator Module

This module provides validation and standardization for application routes.
It ensures proper URL formatting, path validation, and consistent naming conventions.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from flask import Flask, Blueprint, request, current_app, g

# Import our URL utilities
from utils.url_utils import normalize_path, validate_url_path

# Configure logging
logger = logging.getLogger(__name__)

class RouteValidator:
    """
    Utility for validating and standardizing route patterns
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize the route validator
        
        Args:
            app: Optional Flask application to initialize with
        """
        self.validation_rules = {
            'api': self._validate_api_route,
            'web': self._validate_web_route,
            'auth': self._validate_auth_route,
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize with a Flask application
        
        Args:
            app: Flask application to initialize with
        """
        # Store app reference
        self.app = app
        
        # Register validation middleware
        self._register_validation_middleware(app)
        
        # Log initialization
        logger.info("Route validator initialized")
    
    def _register_validation_middleware(self, app: Flask) -> None:
        """
        Register validation middleware with the Flask application
        
        Args:
            app: Flask application to register middleware with
        """
        @app.before_request
        def validate_request_route():
            """Validate all incoming request routes"""
            try:
                # Skip validation for static files
                if request.path.startswith('/static/'):
                    return None
                
                # Basic path validation
                if not validate_url_path(request.path):
                    logger.warning(f"Invalid URL path format: {request.path}")
                    # We don't abort here to allow application to handle it
                    g.invalid_path = True
                else:
                    g.invalid_path = False
                
                # Determine route type for more specific validation
                route_type = self._determine_route_type(request.path)
                
                # Apply specific validation for route type
                validator = self.validation_rules.get(route_type)
                if validator:
                    valid, message = validator(request.path)
                    if not valid:
                        logger.warning(f"Route validation failed: {message} for {request.path}")
                        g.validation_message = message
                
                # Continue processing the request
                return None
            except Exception as e:
                logger.error(f"Error in route validation: {str(e)}")
                return None
    
    def _determine_route_type(self, path: str) -> str:
        """
        Determine the type of route based on the path
        
        Args:
            path: URL path to check
            
        Returns:
            str: Route type ('api', 'web', 'auth', etc.)
        """
        if path.startswith('/api/'):
            return 'api'
        elif path.startswith('/auth/'):
            return 'auth'
        else:
            return 'web'
    
    def _validate_api_route(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an API route
        
        Args:
            path: URL path to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Validate API path format
        # Should follow: /api/v*/resource or /api/resource
        if not re.match(r'^/api(/v\d+)?(/[\w\-]+)+$', path):
            return False, "API route should follow /api/v*/resource pattern"
        
        return True, None
    
    def _validate_web_route(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a web route
        
        Args:
            path: URL path to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Basic validation for web routes
        if '..' in path:
            return False, "Path traversal attempt detected"
        
        # More specific validation can be added here
        
        return True, None
    
    def _validate_auth_route(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an authentication route
        
        Args:
            path: URL path to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Validate auth path format
        # Should follow: /auth/action
        if not re.match(r'^/auth/[\w\-]+$', path):
            return False, "Auth route should follow /auth/action pattern"
        
        return True, None
    
    def analyze_routes(self, app: Flask) -> List[Dict[str, Any]]:
        """
        Analyze all routes in the application for compliance with standards
        
        Args:
            app: Flask application to analyze
            
        Returns:
            List[Dict[str, Any]]: List of route analysis results
        """
        results = []
        
        for rule in app.url_map.iter_rules():
            path = str(rule)
            endpoint = rule.endpoint
            
            # Skip static resources
            if 'static' in endpoint:
                continue
            
            # Determine route type
            route_type = self._determine_route_type(path)
            
            # Validate based on route type
            validator = self.validation_rules.get(route_type)
            valid = True
            message = None
            
            if validator:
                valid, message = validator(path)
            
            # Add to results
            results.append({
                'path': path,
                'endpoint': endpoint,
                'type': route_type,
                'valid': valid,
                'message': message
            })
        
        return results

# Singleton instance for global use
route_validator = RouteValidator()

def init_app(app: Flask) -> None:
    """
    Initialize the route validator with an application (convenience function)
    
    Args:
        app: Flask application to initialize with
    """
    route_validator.init_app(app)

def analyze_routes(app: Flask) -> List[Dict[str, Any]]:
    """
    Analyze all routes in the application (convenience function)
    
    Args:
        app: Flask application to analyze
        
    Returns:
        List[Dict[str, Any]]: List of route analysis results
    """
    return route_validator.analyze_routes(app)