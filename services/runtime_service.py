from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from flask import Flask
from nous_core.eventing import EventStore, EventBus
from nous_core.semantic import SemanticIndex
from nous_core.policy import PolicyEngine

def init_runtime(app: Flask) -> Dict[str, Any]:
    """
    Initialize NOUS core runtime and attach to app.extensions["nous_runtime"].
    Safe to call multiple times.
    """
    if "nous_runtime" in app.extensions:
        return app.extensions["nous_runtime"]

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    events_db = str(Path(app.instance_path) / "nous_events.db")
    semantic_db = str(Path(app.instance_path) / "nous_semantic.db")

    store = EventStore(events_db)
    bus = EventBus(store=store)
    sem = SemanticIndex(semantic_db)
    policy = PolicyEngine()

    rt = {"store": store, "bus": bus, "semantic": sem, "policy": policy}
    app.extensions["nous_runtime"] = rt
    return rt
