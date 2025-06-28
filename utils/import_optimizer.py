"""
Import Optimizer - Lazy Loading and Performance Enhancement
Reduces startup time by implementing lazy imports for heavy modules
"""

import sys
import importlib
from functools import wraps
from typing import Dict, Any, Optional

class LazyImport:
    """Lazy import helper to defer expensive imports until needed"""
    
    def __init__(self, module_name: str, fallback=None):
        self.module_name = module_name
        self.module = None
        self.fallback = fallback
        self.import_attempted = False
    
    def __getattr__(self, name):
        if self.module is None and not self.import_attempted:
            try:
                self.module = importlib.import_module(self.module_name)
            except ImportError:
                self.import_attempted = True
                if self.fallback:
                    self.module = self.fallback
                else:
                    raise ImportError(f"Failed to import {self.module_name}")
        
        if self.module is None:
            raise AttributeError(f"Module {self.module_name} not available")
        
        return getattr(self.module, name)

# Lazy imports for heavy dependencies
numpy = LazyImport('numpy')
pandas = LazyImport('pandas') 
requests = LazyImport('requests')
celery = LazyImport('celery')
prometheus_client = LazyImport('prometheus_client')
zstandard = LazyImport('zstandard')

def lazy_import_decorator(module_name: str):
    """Decorator to lazy import modules only when function is called"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                module = importlib.import_module(module_name)
                return func(*args, **kwargs)
            except ImportError:
                # Graceful degradation
                return None
        return wrapper
    return decorator

def optimize_imports():
    """Optimize imports for faster startup"""
    # Remove unused modules from sys.modules to free memory
    unused_modules = []
    for module_name in list(sys.modules.keys()):
        if any(pattern in module_name for pattern in ['test', 'unittest', 'pytest']):
            unused_modules.append(module_name)
    
    for module_name in unused_modules:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    return len(unused_modules)