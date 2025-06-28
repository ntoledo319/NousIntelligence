"""
MTM-CE Plugin Registry System
Dynamic plugin management with hot-swappable features
"""

import importlib
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Dynamic plugin registry for modular feature management"""
    
    def __init__(self):
        self._plugins = {}
        self._initialized = False
        
    def register(self, name: str, module_path: str, blueprint=None, init_fn: str = None):
        """Register a plugin with the registry"""
        if name in self._plugins:
            logger.warning(f"Plugin {name} already registered, skipping")
            return
            
        try:
            module = importlib.import_module(module_path)
            self._plugins[name] = {
                'module': module,
                'blueprint': blueprint,
                'init_fn': init_fn,
                'module_path': module_path
            }
            logger.info(f"Registered plugin: {name}")
        except ImportError as e:
            logger.error(f"Failed to register plugin {name}: {e}")
            
    def init_all(self, app):
        """Initialize all registered plugins"""
        for name, config in self._plugins.items():
            try:
                if config['init_fn']:
                    init_function = getattr(config['module'], config['init_fn'])
                    init_function(app)
                    logger.info(f"Initialized plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")
                
        self._initialized = True
        
    def wire_blueprints(self, app):
        """Wire all plugin blueprints to the Flask app"""
        for name, config in self._plugins.items():
            try:
                if config['blueprint']:
                    app.register_blueprint(config['blueprint'])
                    logger.info(f"Registered blueprint for plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to register blueprint for plugin {name}: {e}")
                
    def get(self, name: str):
        """Get a specific plugin module"""
        return self._plugins.get(name, {}).get('module')
        
    def list_plugins(self) -> list:
        """List all registered plugin names"""
        return list(self._plugins.keys())
        
    def get_plugin_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a plugin"""
        return self._plugins.get(name, {})
        
    def is_initialized(self) -> bool:
        """Check if plugins have been initialized"""
        return self._initialized
        
    def reload_plugin(self, name: str):
        """Hot-reload a specific plugin"""
        if name not in self._plugins:
            logger.error(f"Plugin {name} not found for reload")
            return False
            
        try:
            config = self._plugins[name]
            importlib.reload(config['module'])
            logger.info(f"Reloaded plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload plugin {name}: {e}")
            return False

# Global plugin registry instance
plugin_registry = PluginRegistry()