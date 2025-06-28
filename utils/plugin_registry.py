"""
NOUS Dynamic Plugin Registry System
Enables hot-swappable features and modular component management for NOUS Personal Assistant
"""

import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class PluginStatus(Enum):
    """Plugin status enumeration"""
    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PluginInfo:
    """Plugin information container"""
    name: str
    module_path: str
    version: str = "1.0.0"
    description: str = ""
    status: PluginStatus = PluginStatus.INACTIVE
    dependencies: List[str] = field(default_factory=list)
    loaded_at: Optional[datetime] = None
    error_message: Optional[str] = None
    instance: Optional[Any] = None
    
class PluginRegistry:
    """Central plugin registry for dynamic feature management"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.categories: Dict[str, List[str]] = {}
        
        # Initialize core plugin categories
        self.categories.update({
            'ai_services': [],
            'intelligence': [],
            'unified_services': [],
            'analytics': [],
            'authentication': [],
            'monitoring': [],
            'integrations': []
        })
        
        # Auto-discover existing plugins
        self._auto_discover_plugins()
    
    def _auto_discover_plugins(self):
        """Auto-discover existing NOUS services as plugins"""
        try:
            # Discover unified services
            unified_services = [
                ('unified_ai_service', 'utils.unified_ai_service', 'ai_services'),
                ('unified_google_services', 'utils.unified_google_services', 'integrations'),
                ('unified_spotify_services', 'utils.unified_spotify_services', 'integrations'),
                ('unified_security_services', 'utils.unified_security_services', 'authentication'),
                ('adaptive_ai_system', 'utils.adaptive_ai_system', 'ai_services')
            ]
            
            for name, module_path, category in unified_services:
                self.register_plugin(
                    name=name,
                    module_path=module_path,
                    category=category,
                    auto_load=False
                )
            
            # Discover intelligence services
            intelligence_services = [
                ('predictive_analytics', 'services.predictive_analytics', 'intelligence'),
                ('enhanced_voice', 'services.enhanced_voice', 'intelligence'),
                ('intelligent_automation', 'services.intelligent_automation', 'intelligence'),
                ('visual_intelligence', 'services.visual_intelligence', 'intelligence'),
                ('context_aware_ai', 'services.context_aware_ai', 'intelligence')
            ]
            
            for name, module_path, category in intelligence_services:
                self.register_plugin(
                    name=name,
                    module_path=module_path,
                    category=category,
                    auto_load=False
                )
            
            logger.info(f"Auto-discovered {len(self.plugins)} plugins")
            
        except Exception as e:
            logger.error(f"Error auto-discovering plugins: {e}")
    
    def register_plugin(self, name: str, module_path: str, category: str = 'general', 
                       description: str = "", dependencies: List[str] = None, 
                       auto_load: bool = True) -> bool:
        """Register a new plugin"""
        try:
            if dependencies is None:
                dependencies = []
            
            plugin_info = PluginInfo(
                name=name,
                module_path=module_path,
                description=description,
                dependencies=dependencies
            )
            
            self.plugins[name] = plugin_info
            
            # Add to category
            if category not in self.categories:
                self.categories[category] = []
            if name not in self.categories[category]:
                self.categories[category].append(name)
            
            if auto_load:
                self.load_plugin(name)
            
            logger.info(f"Registered plugin: {name} in category: {category}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering plugin {name}: {e}")
            return False
    
    def load_plugin(self, name: str) -> bool:
        """Load a specific plugin"""
        if name not in self.plugins:
            logger.error(f"Plugin {name} not registered")
            return False
        
        plugin = self.plugins[name]
        
        try:
            plugin.status = PluginStatus.LOADING
            
            # Check dependencies
            for dep in plugin.dependencies:
                if dep not in self.plugins or self.plugins[dep].status != PluginStatus.ACTIVE:
                    raise Exception(f"Dependency {dep} not available")
            
            # Import module
            module = importlib.import_module(plugin.module_path)
            
            # Find plugin class or function
            plugin_instance = self._create_plugin_instance(module, name)
            
            plugin.instance = plugin_instance
            plugin.status = PluginStatus.ACTIVE
            plugin.loaded_at = datetime.now()
            plugin.error_message = None
            
            # Execute plugin hooks
            self._execute_hooks('plugin_loaded', name, plugin_instance)
            
            logger.info(f"Successfully loaded plugin: {name}")
            return True
            
        except Exception as e:
            plugin.status = PluginStatus.ERROR
            plugin.error_message = str(e)
            logger.error(f"Error loading plugin {name}: {e}")
            return False
    
    def _create_plugin_instance(self, module: Any, plugin_name: str) -> Any:
        """Create plugin instance from module"""
        # Look for common patterns
        instance_patterns = [
            f'get_{plugin_name}',
            f'{plugin_name}_instance',
            'get_instance',
            'create_instance'
        ]
        
        # Try function patterns first
        for pattern in instance_patterns:
            if hasattr(module, pattern):
                func = getattr(module, pattern)
                if callable(func):
                    return func()
        
        # Look for classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.lower().replace('_', '') in plugin_name.lower().replace('_', ''):
                return obj()
        
        # Return module itself as fallback
        return module
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a specific plugin"""
        if name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[name]
            
            # Execute unload hooks
            self._execute_hooks('plugin_unloaded', name, plugin.instance)
            
            plugin.status = PluginStatus.INACTIVE
            plugin.instance = None
            plugin.loaded_at = None
            
            logger.info(f"Unloaded plugin: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {name}: {e}")
            return False
    
    def reload_plugin(self, name: str) -> bool:
        """Reload a plugin"""
        if self.unload_plugin(name):
            return self.load_plugin(name)
        return False
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get plugin instance"""
        if name in self.plugins and self.plugins[name].status == PluginStatus.ACTIVE:
            return self.plugins[name].instance
        return None
    
    def list_plugins(self, category: str = None, status: PluginStatus = None) -> List[Dict[str, Any]]:
        """List plugins with optional filtering"""
        plugins = []
        
        for name, plugin in self.plugins.items():
            # Apply filters
            if category and name not in self.categories.get(category, []):
                continue
            if status and plugin.status != status:
                continue
            
            plugins.append({
                'name': name,
                'status': plugin.status.value,
                'description': plugin.description,
                'loaded_at': plugin.loaded_at.isoformat() if plugin.loaded_at else None,
                'error': plugin.error_message
            })
        
        return plugins
    
    def add_hook(self, event: str, callback: Callable):
        """Add event hook"""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)
    
    def _execute_hooks(self, event: str, *args, **kwargs):
        """Execute event hooks"""
        if event in self.hooks:
            for callback in self.hooks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing hook {callback.__name__}: {e}")
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get comprehensive plugin system status"""
        active_count = sum(1 for p in self.plugins.values() if p.status == PluginStatus.ACTIVE)
        error_count = sum(1 for p in self.plugins.values() if p.status == PluginStatus.ERROR)
        
        return {
            'total_plugins': len(self.plugins),
            'active_plugins': active_count,
            'error_plugins': error_count,
            'categories': {cat: len(plugins) for cat, plugins in self.categories.items()},
            'health_score': active_count / len(self.plugins) if self.plugins else 1.0
        }
    
    def enable_cross_service_communication(self):
        """Enable intelligent cross-service communication"""
        # Get adaptive AI for learning coordination
        adaptive_ai = self.get_plugin('adaptive_ai_system')
        
        # Get intelligence services for coordination
        predictive = self.get_plugin('predictive_analytics')
        voice = self.get_plugin('enhanced_voice')
        automation = self.get_plugin('intelligent_automation')
        visual = self.get_plugin('visual_intelligence')
        
        if adaptive_ai and predictive and voice and automation and visual:
            logger.info("Cross-service communication enabled")
            return True
        
        logger.warning("Not all services available for cross-communication")
        return False

# Global plugin registry instance
plugin_registry = None

def get_plugin_registry() -> PluginRegistry:
    """Get or create global plugin registry"""
    global plugin_registry
    if plugin_registry is None:
        plugin_registry = PluginRegistry()
    return plugin_registry

def load_plugin(name: str) -> bool:
    """Load a plugin by name"""
    return get_plugin_registry().load_plugin(name)

def get_plugin(name: str) -> Optional[Any]:
    """Get a plugin instance by name"""
    return get_plugin_registry().get_plugin(name)

def register_plugin(name: str, module_path: str, **kwargs) -> bool:
    """Register a new plugin"""
    return get_plugin_registry().register_plugin(name, module_path, **kwargs)

def get_plugin_status() -> Dict[str, Any]:
    """Get plugin system status"""
    return get_plugin_registry().get_plugin_status()