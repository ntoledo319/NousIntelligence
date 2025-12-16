from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from flask import current_app
from services.runtime_service import init_runtime

StepFn = Callable[[Dict[str, Any]], Dict[str, Any]]

@dataclass
class Workflow:
    name: str
    steps: List[StepFn]

def _emit(topic: str, payload: Dict[str, Any]) -> None:
    rt = init_runtime(current_app)
    rt["bus"].publish(topic, payload)

def run_workflow(name: str, steps: List[StepFn], payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    _emit("workflow.start", {"name": name, "payload": payload, "ts": time.time()})
    state = dict(payload)
    for idx, step in enumerate(steps):
        out = step(state)
        if not isinstance(out, dict):
            out = {"result": out}
        state.update(out)
        _emit("workflow.step", {"name": name, "idx": idx, "state": out, "ts": time.time()})
    _emit("workflow.done", {"name": name, "state": state, "ts": time.time()})
    return state
