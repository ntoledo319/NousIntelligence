"""
Routes initialization module
Centralizes the registration of all application blueprints
"""

import logging
import importlib
from flask import Blueprint, Flask
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Core blueprint definitions
CORE_BLUEPRINTS = [
    {'name': 'main', 'module': 'routes.main', 'attr': 'main_bp', 'url_prefix': None},
    {'name': 'health_api', 'module': 'routes.health_api', 'attr': 'health_api_bp', 'url_prefix': '/api'},
    {'name': 'google_auth', 'module': 'routes.auth_routes', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'auth_api', 'module': 'routes.simple_auth_api', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'api', 'module': 'routes.api_routes', 'attr': 'api_bp', 'url_prefix': '/api/v1'},
    {'name': 'chat', 'module': 'routes.chat_routes', 'attr': 'chat_bp', 'url_prefix': None},
]

# Feature blueprints
OPTIONAL_BLUEPRINTS = [
    {'name': 'dashboard', 'module': 'routes.dashboard', 'attr': 'dashboard_bp', 'url_prefix': None},
    {'name': 'user', 'module': 'routes.user_routes', 'attr': 'user_bp', 'url_prefix': '/user'},
    {'name': 'dbt', 'module': 'routes.dbt_routes', 'attr': 'dbt_bp', 'url_prefix': '/dbt'},
    {'name': 'cbt', 'module': 'routes.cbt_routes', 'attr': 'cbt_bp', 'url_prefix': '/cbt'},
    {'name': 'aa', 'module': 'routes.aa_routes', 'attr': 'aa_bp', 'url_prefix': '/aa'},
    {'name': 'financial', 'module': 'routes.financial_routes', 'attr': 'financial_bp', 'url_prefix': '/financial'},
    {'name': 'search', 'module': 'routes.search_routes', 'attr': 'search_bp', 'url_prefix': '/api/v1/search'},
    {'name': 'analytics', 'module': 'routes.analytics_routes', 'attr': 'analytics_bp', 'url_prefix': '/api/v1/analytics'},
    {'name': 'notifications', 'module': 'routes.notification_routes', 'attr': 'notifications_bp', 'url_prefix': '/api/v1/notifications'},
    {'name': 'maps', 'module': 'routes.maps_routes', 'attr': 'maps_bp', 'url_prefix': None},
    {'name': 'weather', 'module': 'routes.weather_routes', 'attr': 'weather_bp', 'url_prefix': None},
    {'name': 'tasks', 'module': 'routes.tasks_routes', 'attr': 'tasks_bp', 'url_prefix': None},
]

def register_all_blueprints(app: Flask) -> Flask:
    """Register all application blueprints with the Flask app"""
    
    registered_count = 0
    failed_count = 0
    registered_blueprints = set()
    
    # Register core blueprints
    for bp_config in CORE_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            # Check if blueprint is already registered
            if blueprint.name in registered_blueprints or blueprint.name in app.blueprints:
                logger.warning(f"⚠️  Blueprint {blueprint.name} already registered, skipping")
                continue
                
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            registered_blueprints.add(blueprint.name)
            logger.info(f"✅ Registered core blueprint: {bp_config['name']}")
            registered_count += 1
            
        except ValueError as e:
            if 'already registered' in str(e):
                logger.warning(f"⚠️  Blueprint {bp_config['name']} already registered, skipping")
            else:
                logger.error(f"❌ Failed to register core blueprint {bp_config['name']}: {e}")
                failed_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register core blueprint {bp_config['name']}: {e}")
            failed_count += 1

    # Register optional blueprints
    for bp_config in OPTIONAL_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            # Check if blueprint is already registered
            if blueprint.name in registered_blueprints or blueprint.name in app.blueprints:
                logger.warning(f"⚠️  Blueprint {blueprint.name} already registered, skipping")
                continue
            
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            registered_blueprints.add(blueprint.name)
            logger.info(f"✅ Registered optional blueprint: {bp_config['name']}")
            registered_count += 1
            
        except ValueError as e:
            if 'already registered' in str(e):
                logger.warning(f"⚠️  Blueprint {bp_config['name']} already registered, skipping")
            else:
                logger.warning(f"⚠️  Optional blueprint {bp_config['name']} not available: {e}")
        except Exception as e:
            logger.warning(f"⚠️  Optional blueprint {bp_config['name']} not available: {e}")
    
    logger.info(f"📊 Blueprint registration complete: {registered_count} registered, {failed_count} failed")
    return app
