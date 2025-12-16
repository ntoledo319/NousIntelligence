from __future__ import annotations
import time
from flask import Blueprint, Response, current_app
from services.runtime_service import init_runtime

metrics_bp = Blueprint("metrics", __name__)

@metrics_bp.get("/metrics")
def metrics():
    rt = init_runtime(current_app)
    events = rt["store"].recent(limit=1)
    lines = []
    lines.append("# HELP nous_up 1 if running")
    lines.append("# TYPE nous_up gauge")
    lines.append("nous_up 1")
    lines.append("# HELP nous_events_recent_count number of events sampled")
    lines.append("# TYPE nous_events_recent_count gauge")
    lines.append(f"nous_events_recent_count {len(events)}")
    lines.append("# HELP nous_ts unix time")
    lines.append("# TYPE nous_ts gauge")
    lines.append(f"nous_ts {time.time()}")
    return Response("\n".join(lines) + "\n", mimetype="text/plain")
