from __future__ import annotations
import time
from typing import Any, Dict
from flask import current_app
from services.runtime_service import init_runtime
from services.workflows.engine import run_workflow

def _snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    rt = init_runtime(current_app)
    try:
        from nous_core.monitoring import snapshot
        snap = snapshot()
    except Exception:
        snap = {"ts": time.time()}
    rt["store"].append("system.snapshot", snap)
    return {"snapshot": snap}

def _rollup(state: Dict[str, Any]) -> Dict[str, Any]:
    rt = init_runtime(current_app)
    recent = rt["store"].recent(limit=200)
    return {"events_last_200": len(recent)}

def run_daily_workflow() -> Dict[str, Any]:
    return run_workflow("daily_reset", steps=[_snapshot, _rollup], payload={"ts": time.time()})
