"""
Routes initialization module
Centralizes the registration of all application blueprints
"""

import logging
import importlib
from flask import Flask
from typing import Optional

logger = logging.getLogger(__name__)

CORE_BLUEPRINTS = [
    {'name': 'main', 'module': 'routes.main', 'attr': 'main_bp', 'url_prefix': None},
    {'name': 'health_api', 'module': 'routes.health_api', 'attr': 'health_api_bp', 'url_prefix': '/api'},
    {'name': 'auth', 'module': 'routes.auth_routes', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'demo', 'module': 'routes.demo_routes', 'attr': 'demo_bp', 'url_prefix': None},
    {'name': 'callback', 'module': 'routes.callback_routes', 'attr': 'callback_bp', 'url_prefix': None},
    {'name': 'api', 'module': 'routes.api_routes', 'attr': 'api_bp', 'url_prefix': '/api/v1'},
    {'name': 'api_v2', 'module': 'routes.api_v2', 'attr': 'api_v2_bp', 'url_prefix': '/api/v2'},
    {'name': 'spotify_v2', 'module': 'routes.spotify_v2_routes', 'attr': 'spotify_v2_bp', 'url_prefix': '/api/v2/spotify'},
    {'name': 'nexus', 'module': 'routes.nexus_api', 'attr': 'nexus_bp', 'url_prefix': '/api/v2'},
    {'name': 'metrics', 'module': 'routes.metrics_routes', 'attr': 'metrics_bp', 'url_prefix': ''},
    {'name': 'nexus_console', 'module': 'routes.nexus_console_routes', 'attr': 'nexus_console_bp', 'url_prefix': ''},
    {'name': 'chat', 'module': 'routes.chat_routes', 'attr': 'chat_bp', 'url_prefix': None},
    {'name': 'resources', 'module': 'routes.mental_health_resources_routes', 'attr': 'resources_bp', 'url_prefix': '/resources'},
]

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
    {'name': 'seed', 'module': 'routes.seed_routes', 'attr': 'seed_bp', 'url_prefix': None},
    {'name': 'drone_swarm', 'module': 'routes.drone_swarm_routes', 'attr': 'drone_swarm_bp', 'url_prefix': None},
    {'name': 'drone_dashboard', 'module': 'routes.drone_dashboard_routes', 'attr': 'drone_dashboard_bp', 'url_prefix': None},
    {'name': 'social', 'module': 'routes.social_routes', 'attr': 'social_bp', 'url_prefix': '/social'},
    {'name': 'gamification', 'module': 'routes.gamification_routes', 'attr': 'gamification_bp', 'url_prefix': '/gamification'},
    {'name': 'growth', 'module': 'routes.personal_growth_routes', 'attr': 'growth_bp', 'url_prefix': '/growth'},
]


def register_all_blueprints(app: Flask) -> Flask:
    registered_count = 0
    failed_count = 0
    registered_blueprints = set()

    for bp_config in CORE_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])

            if blueprint.name in registered_blueprints or blueprint.name in app.blueprints:
                logger.warning(f"Blueprint {blueprint.name} already registered, skipping")
                continue

            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)

            registered_blueprints.add(blueprint.name)
            logger.info(f"Registered core blueprint: {bp_config['name']}")
            registered_count += 1

        except Exception as e:
            logger.error(f"Failed to register core blueprint {bp_config['name']}: {e}")
            failed_count += 1

    for bp_config in OPTIONAL_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])

            if blueprint.name in registered_blueprints or blueprint.name in app.blueprints:
                logger.warning(f"Blueprint {blueprint.name} already registered, skipping")
                continue

            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)

            registered_blueprints.add(blueprint.name)
            logger.info(f"Registered optional blueprint: {bp_config['name']}")
            registered_count += 1

        except Exception as e:
            logger.warning(f"Optional blueprint {bp_config['name']} not available: {e}")

    logger.info(f"Blueprint registration complete: {registered_count} registered, {failed_count} failed")
    return app
