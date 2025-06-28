"""
MTM-CE (Medical Technology Management - Clinical Enterprise) Integration Module
Ultra-secure, AI-driven therapeutic assistant with next-gen protections
"""

__version__ = "1.0.0"
__author__ = "NOUS Team"
__description__ = "MTM-CE Integration for NOUS Personal Assistant"

from .plugins import PluginRegistry
from .features.parallel import init_parallel
from .features.compress import init_compression
from .features.brain import init_brain
from .features.selflearn import init_selflearn
from .features.security.monitor import init_security_monitor

__all__ = [
    'PluginRegistry',
    'init_parallel',
    'init_compression', 
    'init_brain',
    'init_selflearn',
    'init_security_monitor'
]