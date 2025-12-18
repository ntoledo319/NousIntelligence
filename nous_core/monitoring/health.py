from __future__ import annotations
import time
from typing import Dict

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None  # type: ignore

def snapshot() -> Dict:
    """
    Capture a lightweight system snapshot.

    If the optional ``psutil`` dependency is unavailable, return
    a stub snapshot with zeroed metrics so monitoring endpoints
    remain functional in minimal environments and during tests.
    """
    now = time.time()

    if psutil is None:
        return {
            "ts": now,
            "cpu_percent": 0.0,
            "mem_percent": 0.0,
            "disk_percent": 0.0,
        }

    return {
        "ts": now,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "mem_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
