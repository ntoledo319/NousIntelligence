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
    {'name': 'health_api', 'module': 'routes.health_api', 'attr': 'health_api_bp', 'url_prefix': '/api'},
    {'name': 'auth_api', 'module': 'routes.simple_auth_api', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'api', 'module': 'routes.api_routes', 'attr': 'api_bp', 'url_prefix': '/api/v1'},
    {'name': 'analytics', 'module': 'routes.analytics_routes', 'attr': 'analytics_bp', 'url_prefix': '/api/v1/analytics'},
    {'name': 'search', 'module': 'routes.search_routes', 'attr': 'search_bp', 'url_prefix': '/api/v1/search'},
    {'name': 'notifications', 'module': 'routes.notification_routes', 'attr': 'notifications_bp', 'url_prefix': '/api/v1/notifications'}
]

# Optional blueprint definitions - Updated for consolidated routes
OPTIONAL_BLUEPRINTS = [
    {'name': 'aa', 'module': 'routes.aa_routes', 'attr': 'aa_bp', 'url_prefix': '/aa'},
    {'name': 'dbt', 'module': 'routes.dbt_routes', 'attr': 'dbt_bp', 'url_prefix': '/dbt'},
    {'name': 'cbt', 'module': 'routes.cbt_routes', 'attr': 'cbt_bp', 'url_prefix': '/cbt'},
    {'name': 'user', 'module': 'routes.user_routes', 'attr': 'user_bp', 'url_prefix': '/user'},
    {'name': 'dashboard', 'module': 'routes.dashboard', 'attr': 'dashboard_bp', 'url_prefix': '/dashboard'},
    {'name': 'smart_shopping', 'module': 'routes.smart_shopping_routes', 'attr': 'smart_shopping_bp', 'url_prefix': '/smart-shopping'},
    {'name': 'price_tracking', 'module': 'routes.price_routes', 'attr': 'price_tracking_bp', 'url_prefix': '/price-tracking'},
    {'name': 'language_learning', 'module': 'routes.language_learning_routes', 'attr': 'll_bp', 'url_prefix': '/learn'},
    {'name': 'meetings', 'module': 'routes.meet_routes', 'attr': 'meet_bp', 'url_prefix': '/meet'},
    {'name': 'forms', 'module': 'routes.forms_routes', 'attr': 'forms_bp', 'url_prefix': '/forms'},
    {'name': 'amazon', 'module': 'routes.amazon_routes', 'attr': 'amazon_bp', 'url_prefix': '/amazon'},
    {'name': 'memory', 'module': 'routes.memory_routes', 'attr': 'memory_bp', 'url_prefix': '/memory'},
    {'name': 'crisis', 'module': 'routes.crisis_routes', 'attr': 'crisis_bp', 'url_prefix': '/crisis'},
    {'name': 'financial', 'module': 'routes.financial_routes', 'attr': 'financial_bp', 'url_prefix': '/financial'},
    {'name': 'collaboration', 'module': 'routes.collaboration_routes', 'attr': 'collaboration_bp', 'url_prefix': '/collaboration'},
    {'name': 'onboarding', 'module': 'routes.onboarding_routes', 'attr': 'onboarding_bp', 'url_prefix': '/onboarding'},
    {'name': 'nous_tech_status', 'module': 'routes.nous_tech_status_routes', 'attr': 'nous_tech_bp', 'url_prefix': '/nous-tech'},
    # Consolidated route modules
    {'name': 'consolidated_api', 'module': 'routes.consolidated_api_routes', 'attr': 'consolidated_api_bp', 'url_prefix': '/api'},
    {'name': 'consolidated_voice', 'module': 'routes.consolidated_voice_routes', 'attr': 'consolidated_voice_bp', 'url_prefix': '/voice'},
    {'name': 'consolidated_spotify', 'module': 'routes.consolidated_spotify_routes', 'attr': 'consolidated_spotify_bp', 'url_prefix': '/spotify'},
    # Enhanced Intelligence Services
    {'name': 'enhanced_api', 'module': 'routes.enhanced_api_routes', 'attr': 'enhanced_api', 'url_prefix': '/api/v2'},
    # Adaptive AI System
    {'name': 'adaptive_ai', 'module': 'routes.adaptive_ai_routes', 'attr': 'adaptive_ai_bp', 'url_prefix': '/api/adaptive'},
    # Chat API System
    {'name': 'api_chat', 'module': 'api.chat', 'attr': 'api_chat_bp', 'url_prefix': None},
    # Enhanced Chat API
    {'name': 'enhanced_chat_api', 'module': 'api.enhanced_chat', 'attr': 'enhanced_chat_bp', 'url_prefix': '/api/enhanced'},
    # Therapeutic Chat API - Emotion-aware DBT/CBT support
    {'name': 'therapeutic_chat', 'module': 'api.therapeutic_chat', 'attr': 'therapeutic_chat_bp', 'url_prefix': '/api/therapeutic'},
    # NOUS Technology Status and Monitoring
    {'name': 'nous_tech_status', 'module': 'routes.nous_tech_status_routes', 'attr': 'nous_tech_status_bp', 'url_prefix': '/nous-tech'}
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