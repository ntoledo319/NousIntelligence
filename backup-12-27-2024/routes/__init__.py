"""
Routes initialization module
Centralizes the registration of all application blueprints with standardized patterns
"""

import logging
import importlib
from flask import Blueprint, Flask
from typing import Dict, List, Optional

# Import route standardization utilities
from utils.route_standards import register_blueprint, verify_routes

# Configure logging
logger = logging.getLogger(__name__)

# Core blueprint definitions - name, module, url_prefix
CORE_BLUEPRINTS = [
    {'name': 'main', 'module': 'routes.main', 'attr': 'main_bp', 'url_prefix': None},
    {'name': 'health_api', 'module': 'routes.api.health', 'attr': 'health_bp', 'url_prefix': '/api'},
    {'name': 'auth', 'module': 'routes.auth', 'attr': 'auth_bp', 'url_prefix': None},  # Auth routes are essential
]

# Optional blueprint definitions
OPTIONAL_BLUEPRINTS = [
    {'name': 'analytics', 'module': 'routes.aa_routes', 'attr': 'aa_bp', 'url_prefix': '/aa'},
    {'name': 'user', 'module': 'routes.user_routes', 'attr': 'user_bp', 'url_prefix': '/user'},
    {'name': 'dashboard', 'module': 'routes.dashboard', 'attr': 'dashboard_bp', 'url_prefix': '/dashboard'},
    {'name': 'smart_shopping', 'module': 'routes.smart_shopping_routes', 'attr': 'smart_shopping_bp', 'url_prefix': '/smart-shopping'},
    {'name': 'price_tracking', 'module': 'routes.price_routes', 'attr': 'price_tracking_bp', 'url_prefix': '/price-tracking'},
]

def register_all_blueprints(app: Flask) -> Flask:
    """
    Register all application blueprints with the Flask app using standardized patterns

    Args:
        app: Flask application instance

    Returns:
        Flask application instance with registered blueprints
    """
    registered_blueprints = []

    # Register core blueprints (required for application)
    for bp_config in CORE_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            register_blueprint(blueprint, app, bp_config['url_prefix'])
            registered_blueprints.append(bp_config['name'])
        except (ImportError, AttributeError) as e:
            logger.error(f"Error registering core blueprint {bp_config['name']}: {str(e)}")
            # Core blueprints are required, raise the error
            raise

    # Register optional blueprints (application works without them)
    for bp_config in OPTIONAL_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            register_blueprint(blueprint, app, bp_config['url_prefix'])
            registered_blueprints.append(bp_config['name'])
        except (ImportError, AttributeError) as e:
            logger.info(f"Optional blueprint {bp_config['name']} not registered: {str(e)}")

    logger.info(f"Registered blueprints: {', '.join(registered_blueprints)}")

    # Verify all routes after registration
    issues = verify_routes(app)
    if issues:
        for issue in issues:
            logger.warning(f"Route issue: {issue['endpoint']} {issue['url']} - {issue['issue']}")

    return app