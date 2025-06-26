"""
Route Standards Utility

This module provides standards and validation for route definitions.
It ensures consistent URL patterns and blueprint conventions across the application.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from flask import Blueprint, Flask

# Configure logging
logger = logging.getLogger(__name__)

# URL pattern standards
URL_PATTERNS = {
    'api': r'^/api/[\w\-/]+$',           # API endpoints
    'web': r'^/[\w\-/]*$',               # Web pages
    'static': r'^/static/[\w\-/\.]+$',   # Static resources
    'auth': r'^/auth/[\w\-/]+$',         # Authentication routes
    'user': r'^/user/[\w\-/]+$',         # User-specific routes
}

# Blueprint naming conventions
BLUEPRINT_CONVENTIONS = {
    'api': '{name}_api',
    'web': '{name}',
    'auth': 'auth_{name}',
    'user': 'user_{name}',
}

class RouteValidator:
    """
    Validates and standardizes route configurations
    """

    @staticmethod
    def validate_url_pattern(url: str, pattern_type: str = 'web') -> bool:
        """
        Validate a URL against the standard pattern

        Args:
            url: URL to validate
            pattern_type: Type of pattern to validate against

        Returns:
            bool: True if URL matches pattern, False otherwise
        """
        if pattern_type not in URL_PATTERNS:
            logger.warning(f"Unknown pattern type: {pattern_type}")
            return True

        pattern = URL_PATTERNS[pattern_type]
        return bool(re.match(pattern, url))

    @staticmethod
    def get_standardized_blueprint_name(name: str, category: str = 'web') -> str:
        """
        Get a standardized blueprint name following conventions

        Args:
            name: Base name for the blueprint
            category: Category for naming convention

        Returns:
            str: Standardized blueprint name
        """
        if category not in BLUEPRINT_CONVENTIONS:
            logger.warning(f"Unknown blueprint category: {category}")
            return name

        return BLUEPRINT_CONVENTIONS[category].format(name=name)

    @staticmethod
    def standardize_url_prefix(prefix: str) -> str:
        """
        Standardize a URL prefix to ensure consistency

        Args:
            prefix: URL prefix to standardize

        Returns:
            str: Standardized URL prefix
        """
        # Ensure prefix starts with forward slash
        if not prefix.startswith('/'):
            prefix = f'/{prefix}'

        # Remove trailing slash if present
        if prefix.endswith('/') and len(prefix) > 1:
            prefix = prefix[:-1]

        return prefix

class BlueprintRegistry:
    """
    Centralized registry for Flask blueprints
    """

    def __init__(self):
        self.blueprints: Dict[str, Blueprint] = {}
        self.validator = RouteValidator()

    def register(self, bp: Blueprint, app: Flask, url_prefix: Optional[str] = None) -> None:
        """
        Register a blueprint with validation and standardization

        Args:
            bp: Blueprint to register
            app: Flask application instance
            url_prefix: Optional URL prefix override
        """
        # Store blueprint in registry
        self.blueprints[bp.name] = bp

        # Standardize URL prefix if provided
        if url_prefix:
            url_prefix = self.validator.standardize_url_prefix(url_prefix)

        # Register blueprint with app
        app.register_blueprint(bp, url_prefix=url_prefix)
        logger.info(f"Registered blueprint: {bp.name} with prefix: {url_prefix or 'None'}")

    def verify_all_routes(self, app: Flask) -> List[Dict[str, Any]]:
        """
        Verify all routes against standards

        Args:
            app: Flask application instance

        Returns:
            List of issues found
        """
        issues = []

        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            url = str(rule)

            # Skip static files
            if 'static' in endpoint:
                continue

            # Determine pattern type
            pattern_type = 'web'
            if url.startswith('/api/'):
                pattern_type = 'api'
            elif url.startswith('/auth/'):
                pattern_type = 'auth'
            elif url.startswith('/user/'):
                pattern_type = 'user'

            # Validate URL pattern
            if not self.validator.validate_url_pattern(url, pattern_type):
                issues.append({
                    'endpoint': endpoint,
                    'url': url,
                    'issue': f"URL doesn't match {pattern_type} pattern standard"
                })

        return issues

# Global blueprint registry
blueprint_registry = BlueprintRegistry()

def register_blueprint(bp: Blueprint, app: Flask, url_prefix: Optional[str] = None) -> None:
    """
    Register a blueprint with standard validation

    Args:
        bp: Blueprint to register
        app: Flask application instance
        url_prefix: Optional URL prefix
    """
    blueprint_registry.register(bp, app, url_prefix)

def verify_routes(app: Flask) -> List[Dict[str, Any]]:
    """
    Verify all routes in the application against standards

    Args:
        app: Flask application instance

    Returns:
        List of issues found
    """
    return blueprint_registry.verify_all_routes(app)