"""
NOUS Tech Integration Module
Ultra-secure, AI-driven therapeutic assistant with next-gen protections
"""

__version__ = "1.0.0"
__author__ = "NOUS Team"
__description__ = "NOUS Tech Integration for NOUS Personal Assistant"

try:
    from .plugins import PluginRegistry
except ImportError:
    PluginRegistry = None

try:
    from .features.parallel import init_parallel
except ImportError:
    def init_parallel(app): pass

try:
    from .features.compress import init_compression
except ImportError:
    def init_compression(app): pass

try:
    from .features.brain import init_brain
except ImportError:
    def init_brain(app): pass

try:
    from .features.selflearn import init_selflearn
except ImportError:
    def init_selflearn(app): pass

try:
    from .features.security.monitor import init_security_monitor
except ImportError:
    def init_security_monitor(app): pass

__all__ = [
    'PluginRegistry',
    'init_parallel',
    'init_compression', 
    'init_brain',
    'init_selflearn',
    'init_security_monitor'
]