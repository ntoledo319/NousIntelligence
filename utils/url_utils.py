"""
URL Utilities

This module provides utilities for standardized URL handling in the application.
It ensures consistent URL generation and validation across features.
"""

import re
import logging
import urllib.parse
from typing import Dict, Any, Optional
from flask import url_for, current_app, request

# Configure logging
logger = logging.getLogger(__name__)

class URLStandardizer:
    """
    Utility class for standardizing and validating URLs
    """
    
    # URL component patterns for validation
    URL_PATTERNS = {
        'domain': r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}$',
        'path': r'^[\w\-\/\.]+$',
        'query_param': r'^[\w\-\.]+$',
    }
    
    # Reserved route names that should never be used
    RESERVED_ROUTES = [
        'static',
        'admin',
        'api',
        'login',
        'logout',
        'register',
        'reset_password',
    ]
    
    @staticmethod
    def get_absolute_url(endpoint: str, **kwargs) -> str:
        """
        Generate an absolute URL for an endpoint
        
        Args:
            endpoint: The Flask endpoint name
            **kwargs: Keyword arguments for the URL parameters
            
        Returns:
            str: The absolute URL
        """
        # Generate relative URL
        relative_url = url_for(endpoint, **kwargs)
        
        # Get the base URL
        if current_app.config.get('SERVER_NAME'):
            # Use configured server name if available
            server_name = current_app.config['SERVER_NAME']
            scheme = current_app.config.get('PREFERRED_URL_SCHEME', 'https')
            base_url = f"{scheme}://{server_name}"
        else:
            # Build from current request
            try:
                scheme = request.scheme
                host = request.host
                base_url = f"{scheme}://{host}"
            except RuntimeError:
                # No active request context, use a default
                logger.warning("No request context, using default base URL")
                base_url = "https://nous.chat"
        
        # Combine base URL and relative URL
        if relative_url.startswith('/'):
            absolute_url = f"{base_url}{relative_url}"
        else:
            absolute_url = f"{base_url}/{relative_url}"
            
        return absolute_url
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a URL path
        
        Args:
            path: URL path to normalize
            
        Returns:
            str: Normalized URL path
        """
        # Ensure path starts with forward slash
        if not path.startswith('/'):
            path = f'/{path}'
        
        # Remove trailing slash unless it's the root path
        if path.endswith('/') and len(path) > 1:
            path = path[:-1]
        
        # Replace multiple slashes with a single slash
        path = re.sub(r'/+', '/', path)
        
        return path
    
    @staticmethod
    def validate_url_path(path: str) -> bool:
        """
        Validate a URL path
        
        Args:
            path: URL path to validate
            
        Returns:
            bool: True if path is valid, False otherwise
        """
        if not path.startswith('/'):
            return False
            
        # Check for path traversal
        if '..' in path:
            return False
            
        # Basic pattern validation
        path_without_leading_slash = path[1:]
        if path_without_leading_slash and not re.match(URLStandardizer.URL_PATTERNS['path'], path_without_leading_slash):
            return False
            
        return True
    
    @staticmethod
    def append_query_params(url: str, params: Dict[str, Any]) -> str:
        """
        Append query parameters to a URL
        
        Args:
            url: The URL to append query parameters to
            params: The query parameters to append
            
        Returns:
            str: The URL with query parameters
        """
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Parse existing query parameters
        query_dict = dict(urllib.parse.parse_qsl(parsed_url.query))
        
        # Update with new parameters
        query_dict.update(params)
        
        # Build new query string
        query_string = urllib.parse.urlencode(query_dict)
        
        # Reconstruct the URL
        new_url = urllib.parse.urlunparse(
            (
                parsed_url.scheme, 
                parsed_url.netloc, 
                parsed_url.path, 
                parsed_url.params, 
                query_string, 
                parsed_url.fragment
            )
        )
        
        return new_url
    
    @staticmethod
    def is_valid_blueprint_url_prefix(prefix: str) -> bool:
        """
        Check if a URL prefix is valid for a blueprint
        
        Args:
            prefix: The URL prefix to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Must start with a slash
        if not prefix.startswith('/'):
            return False
            
        # Remove leading slash for further checks
        prefix_without_slash = prefix[1:]
        
        # Check if it's a reserved name
        if prefix_without_slash in URLStandardizer.RESERVED_ROUTES:
            return False
            
        # Check if it follows our pattern
        if not re.match(r'^[a-z0-9\-]+$', prefix_without_slash):
            return False
            
        return True

def get_absolute_url(endpoint: str, **kwargs) -> str:
    """
    Generate an absolute URL for an endpoint (convenience function)
    
    Args:
        endpoint: The Flask endpoint name
        **kwargs: Keyword arguments for the URL parameters
        
    Returns:
        str: The absolute URL
    """
    return URLStandardizer.get_absolute_url(endpoint, **kwargs)

def normalize_path(path: str) -> str:
    """
    Normalize a URL path (convenience function)
    
    Args:
        path: URL path to normalize
        
    Returns:
        str: Normalized URL path
    """
    return URLStandardizer.normalize_path(path)

def validate_url_path(path: str) -> bool:
    """
    Validate a URL path (convenience function)
    
    Args:
        path: URL path to validate
        
    Returns:
        bool: True if path is valid, False otherwise
    """
    return URLStandardizer.validate_url_path(path)

def append_query_params(url: str, params: Dict[str, Any]) -> str:
    """
    Append query parameters to a URL (convenience function)
    
    Args:
        url: The URL to append query parameters to
        params: The query parameters to append
        
    Returns:
        str: The URL with query parameters
    """
    return URLStandardizer.append_query_params(url, params)