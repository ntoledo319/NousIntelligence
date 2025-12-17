"""
Routes initialization module
Centralizes the registration of all application blueprints
"""

import importlib
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Core blueprint definitions
CORE_BLUEPRINTS = [
    {'name': 'main', 'module': 'routes.view.index', 'attr': 'main_bp', 'url_prefix': None},
    {'name': 'health', 'module': 'routes.health', 'attr': 'health_bp', 'url_prefix': None},
    {'name': 'auth', 'module': 'routes.auth_routes', 'attr': 'auth_bp', 'url_prefix': None},
    {'name': 'api_v2', 'module': 'routes.api_v2', 'attr': 'api_v2_bp', 'url_prefix': None},
    {'name': 'nexus', 'module': 'routes.nexus_routes', 'attr': 'nexus_bp', 'url_prefix': None},
    {'name': 'spotify', 'module': 'routes.spotify_routes', 'attr': 'spotify_bp', 'url_prefix': None},
]

# Optional blueprints - can be enabled/disabled
OPTIONAL_BLUEPRINTS = [
    {'name': 'assistant', 'module': 'routes.assistant_routes', 'attr': 'assistant_bp', 'url_prefix': None, 'env_var': 'ENABLE_ASSISTANT_ROUTES'},
    {'name': 'files', 'module': 'routes.file_routes', 'attr': 'file_bp', 'url_prefix': None, 'env_var': 'ENABLE_FILE_ROUTES'},
    {'name': 'scraper', 'module': 'routes.scraper_routes', 'attr': 'scraper_bp', 'url_prefix': None, 'env_var': 'ENABLE_SCRAPER_ROUTES'},
    {'name': 'spotify_routes', 'module': 'routes.consolidated_spotify_routes', 'attr': 'consolidated_spotify_bp', 'url_prefix': None, 'env_var': 'ENABLE_LEGACY_SPOTIFY_ROUTES'},
    {'name': 'notion', 'module': 'routes.notion_routes', 'attr': 'notion_bp', 'url_prefix': None, 'env_var': 'ENABLE_NOTION_ROUTES'},
    {'name': 'tasks', 'module': 'routes.task_routes', 'attr': 'task_bp', 'url_prefix': None, 'env_var': 'ENABLE_TASK_ROUTES'},
    {'name': 'api_docs', 'module': 'routes.api_docs', 'attr': 'api_docs_bp', 'url_prefix': None, 'env_var': 'ENABLE_API_DOCS'},
]

def register_blueprint_safely(app, bp_config: Dict[str, Any]) -> bool:
    """
    Register a blueprint with error handling.
    
    Args:
        app: Flask app instance
        bp_config: Blueprint configuration dict
        
    Returns:
        bool: True if registered successfully, False otherwise
    """
    try:
        module = importlib.import_module(bp_config['module'])
        blueprint = getattr(module, bp_config['attr'])
        
        if bp_config['url_prefix']:
            app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
        else:
            app.register_blueprint(blueprint)
            
        logger.info(f"✅ Registered blueprint: {bp_config['name']} ({bp_config['module']}.{bp_config['attr']})")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import blueprint {bp_config['name']}: {e}")
        return False
    except AttributeError as e:
        logger.error(f"❌ Blueprint {bp_config['name']} attribute not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error registering blueprint {bp_config['name']}: {e}")
        return False

def register_all_blueprints(app) -> None:
    """
    Register all blueprints (core + enabled optional).
    """
    registered_blueprints = set()
    
    # Register core blueprints
    for bp_config in CORE_BLUEPRINTS:
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            logger.info(f"✅ Registered core blueprint: {bp_config['name']}")
            # Optional per-blueprint alias registration (used by Spotify compatibility endpoints)
            if hasattr(module, 'register_aliases'):
                try:
                    module.register_aliases(app)
                except Exception as e:
                    logger.warning(f"⚠️  Alias registration failed for {bp_config['name']}: {e}")

            registered_blueprints.add(blueprint.name)
            
        except Exception as e:
            logger.error(f"❌ Failed to register core blueprint {bp_config['name']}: {e}")
    
    # Register enabled optional blueprints
    for bp_config in OPTIONAL_BLUEPRINTS:
        env_var = bp_config.get('env_var')
        if env_var and os.getenv(env_var, '').lower() not in ('true', '1', 'yes', 'on'):
            logger.info(f"⏭️  Skipping optional blueprint {bp_config['name']} (disabled by {env_var})")
            continue
            
        try:
            module = importlib.import_module(bp_config['module'])
            blueprint = getattr(module, bp_config['attr'])
            
            if bp_config['url_prefix']:
                app.register_blueprint(blueprint, url_prefix=bp_config['url_prefix'])
            else:
                app.register_blueprint(blueprint)
            
            logger.info(f"✅ Registered optional blueprint: {bp_config['name']}")
            # Optional per-blueprint alias registration (used by Spotify compatibility endpoints)
            if hasattr(module, 'register_aliases'):
                try:
                    module.register_aliases(app)
                except Exception as e:
                    logger.warning(f"⚠️  Alias registration failed for {bp_config['name']}: {e}")

            registered_blueprints.add(blueprint.name)
            
        except Exception as e:
            logger.error(f"❌ Failed to register optional blueprint {bp_config['name']}: {e}")
    
    logger.info(f"📋 Total registered blueprints: {len(registered_blueprints)}")
    logger.info(f"📋 Blueprint names: {sorted(registered_blueprints)}")

def get_registered_blueprints(app) -> List[str]:
    """Get list of registered blueprint names."""
    return list(app.blueprints.keys())
