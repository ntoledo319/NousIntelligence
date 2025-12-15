from __future__ import annotations
import time
from typing import Dict
import psutil

def snapshot() -> Dict:
    return {
        "ts": time.time(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "mem_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }

