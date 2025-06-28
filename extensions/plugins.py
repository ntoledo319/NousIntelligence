"""
NOUS Plugin System
Dynamic plugin loading and management system for extensible features
"""

import importlib
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Dynamic plugin registry for modular feature management"""
    
    def __init__(self):
        """Initialize the plugin registry"""
        self._plugins = {}
        self._initialized = False
        logger.info("NOUS Plugin Registry initialized")
    
    def register(self, name: str, module_path: str, blueprint=None, init_fn: Optional[str] = None):
        """Register a plugin with the registry
        
        Args:
            name: Plugin name/identifier
            module_path: Python module path to import
            blueprint: Flask blueprint to register (optional)
            init_fn: Initialization function name in the module (optional)
        """
        if name in self._plugins:
            logger.warning(f"Plugin '{name}' already registered, skipping")
            return
            
        try:
            module = importlib.import_module(module_path)
            self._plugins[name] = {
                'module': module,
                'blueprint': blueprint,
                'init_fn': init_fn,
                'module_path': module_path
            }
            logger.info(f"Plugin '{name}' registered successfully")
        except ImportError as e:
            logger.error(f"Failed to import plugin '{name}' from '{module_path}': {e}")
        except Exception as e:
            logger.error(f"Error registering plugin '{name}': {e}")
    
    def init_all(self, app):
        """Initialize all registered plugins with the Flask app
        
        Args:
            app: Flask application instance
        """
        if self._initialized:
            logger.warning("Plugins already initialized, skipping")
            return
            
        logger.info("Initializing all registered plugins")
        
        for name, cfg in self._plugins.items():
            try:
                if cfg['init_fn']:
                    init_function = getattr(cfg['module'], cfg['init_fn'])
                    if callable(init_function):
                        init_function(app)
                        logger.info(f"Plugin '{name}' initialized successfully")
                    else:
                        logger.warning(f"Plugin '{name}' init function '{cfg['init_fn']}' is not callable")
            except AttributeError:
                logger.error(f"Plugin '{name}' missing init function '{cfg['init_fn']}'")
            except Exception as e:
                logger.error(f"Error initializing plugin '{name}': {e}")
        
        self._initialized = True
    
    def wire_blueprints(self, app):
        """Register all plugin blueprints with the Flask app
        
        Args:
            app: Flask application instance
        """
        logger.info("Registering plugin blueprints")
        
        for name, cfg in self._plugins.items():
            try:
                if cfg['blueprint']:
                    app.register_blueprint(cfg['blueprint'])
                    logger.info(f"Blueprint for plugin '{name}' registered successfully")
            except Exception as e:
                logger.error(f"Error registering blueprint for plugin '{name}': {e}")
    
    def get(self, name: str):
        """Get a registered plugin module
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin module or None if not found
        """
        plugin_data = self._plugins.get(name, {})
        return plugin_data.get('module')
    
    def list_plugins(self) -> list:
        """Get list of all registered plugin names
        
        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())
    
    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin information dictionary or None
        """
        return self._plugins.get(name)
    
    def unregister(self, name: str) -> bool:
        """Unregister a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful, False if plugin not found
        """
        if name in self._plugins:
            del self._plugins[name]
            logger.info(f"Plugin '{name}' unregistered")
            return True
        return False
    
    def reload_plugin(self, name: str, app=None):
        """Reload a plugin module
        
        Args:
            name: Plugin name
            app: Flask app for re-initialization (optional)
        """
        if name not in self._plugins:
            logger.error(f"Cannot reload plugin '{name}': not registered")
            return
            
        try:
            plugin_info = self._plugins[name]
            module = importlib.reload(plugin_info['module'])
            plugin_info['module'] = module
            
            # Re-initialize if app provided and init function exists
            if app and plugin_info['init_fn']:
                init_function = getattr(module, plugin_info['init_fn'])
                if callable(init_function):
                    init_function(app)
                    logger.info(f"Plugin '{name}' reloaded and re-initialized")
                    
        except Exception as e:
            logger.error(f"Error reloading plugin '{name}': {e}")

# Create global plugin registry instance
plugin_registry = PluginRegistry()

def register_plugin(name: str, module_path: str, blueprint=None, init_fn: Optional[str] = None):
    """Decorator to register a plugin
    
    Usage:
        @register_plugin("my_plugin", "my_module", init_fn="init_my_plugin")
        def my_plugin_function():
            pass
    """
    def decorator(func):
        plugin_registry.register(name, module_path, blueprint, init_fn)
        return func
    return decorator