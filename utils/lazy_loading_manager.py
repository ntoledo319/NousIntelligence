"""
Lazy Loading Manager
Implements lazy loading for heavy dependencies to improve startup performance
"""

import importlib
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class LazyLoadingManager:
    """Manager for lazy loading heavy dependencies"""
    
    def __init__(self):
        self.loaded_modules = {}
        self.loading_cache = {}
    
    def lazy_import(self, module_name: str, fallback: Optional[Callable] = None):
        """Decorator for lazy importing modules"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if module_name not in self.loaded_modules:
                    try:
                        self.loaded_modules[module_name] = importlib.import_module(module_name)
                        logger.info(f"Lazy loaded module: {module_name}")
                    except ImportError as e:
                        logger.warning(f"Failed to lazy load {module_name}: {e}")
                        if fallback:
                            return fallback(*args, **kwargs)
                        raise
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_module(self, module_name: str):
        """Get lazily loaded module"""
        if module_name not in self.loaded_modules:
            try:
                self.loaded_modules[module_name] = importlib.import_module(module_name)
            except ImportError:
                return None
        return self.loaded_modules[module_name]
    
    def preload_critical_modules(self):
        """Preload critical modules in background"""
        critical_modules = [
            'flask',
            'sqlalchemy', 
            'werkzeug',
            'jinja2'
        ]
        
        for module in critical_modules:
            try:
                self.loaded_modules[module] = importlib.import_module(module)
            except ImportError:
                logger.warning(f"Could not preload critical module: {module}")
    
    def get_loading_stats(self) -> Dict[str, Any]:
        """Get lazy loading statistics"""
        return {
            'loaded_modules': len(self.loaded_modules),
            'modules': list(self.loaded_modules.keys()),
            'cache_size': len(self.loading_cache)
        }

# Global lazy loading manager
lazy_manager = LazyLoadingManager()

# Convenience decorator
def lazy_import(module_name: str, fallback: Optional[Callable] = None):
    """Convenience decorator for lazy importing"""
    return lazy_manager.lazy_import(module_name, fallback)
