"""
NOUS Extensions Module
Enhanced functionality and plugin system for NOUS Personal Assistant
"""

try:
    from .plugins import PluginRegistry, plugin_registry
except ImportError:
    PluginRegistry = None
    plugin_registry = None

try:
    from .async_processor import init_async_processing
except ImportError:
    init_async_processing = None

try:
    from .monitoring import init_monitoring
except ImportError:
    init_monitoring = None

try:
    from .learning import init_learning_system
except ImportError:
    init_learning_system = None

try:
    from .compression import init_compression
except ImportError:
    init_compression = None

__version__ = "1.0.0"
__all__ = [
    'PluginRegistry',
    'plugin_registry',
    'init_async_processing',
    'init_monitoring', 
    'init_learning_system',
    'init_compression'
]