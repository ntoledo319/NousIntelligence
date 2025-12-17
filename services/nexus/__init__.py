"""
Nexus package.

Keep this __init__ lightweight: importing heavy modules (especially pipeline) here
can create circular imports at app startup.

Import what you need directly from submodules, e.g.:
    from services.nexus.memory_graph import MemoryGraph
    from services.nexus.pipeline import run_pipeline
"""

from services.nexus.memory_graph import MemoryGraph  # noqa: F401

__all__ = ["MemoryGraph"]
