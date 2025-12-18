from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from flask import Blueprint, jsonify, request, g, current_app

from services.runtime_service import init_runtime
from utils.unified_auth import demo_allowed, get_demo_user


mood_bp = Blueprint("mood_api", __name__)


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _user_id() -> str:
    u = getattr(g, "user", None) or get_demo_user()
    return str((u or {}).get("id") or "demo_user")


@mood_bp.route("/api/v2/mood/log", methods=["POST"])
@demo_allowed
def mood_log():
    rt = init_runtime(current_app)
    data = request.get_json(silent=True) or {}
    try:
        mood = float(data.get("mood"))
    except Exception:
        return jsonify({"ok": False, "error": "mood must be a number 1-10"}), 400
    if mood < 1 or mood > 10:
        return jsonify({"ok": False, "error": "mood must be between 1 and 10"}), 400

    payload: Dict[str, Any] = {
        "mood": mood,
        "note": str(data.get("note") or ""),
        "tags": data.get("tags") if isinstance(data.get("tags"), list) else [],
        "ts": _now_iso(),
        "user_id": _user_id(),
    }

    try:
        rt["bus"].publish("mood.logged", payload)
    except Exception:
        pass

    try:
        txt = f"Mood log: {mood}/10. Note: {payload['note']}".strip()
        rt["semantic"].upsert(f"mood:{payload['user_id']}:{payload['ts']}", txt, {"kind": "mood", **payload})
    except Exception:
        pass

    try:
        nid = f"mood:{payload['user_id']}:{payload['ts']}"
        rt["graph"].upsert_node(nid, kind="mood_entry", meta=payload)
        rt["graph"].upsert_node(payload["user_id"], kind="user", meta={"user_id": payload["user_id"]})
        rt["graph"].add_edge(payload["user_id"], nid, rel="logged")
    except Exception:
        pass

    return jsonify({"ok": True, "mood": payload})


@mood_bp.route("/api/v2/mood/recent", methods=["GET"])
@demo_allowed
def mood_recent():
    rt = init_runtime(current_app)
    limit = int(request.args.get("limit", 20))
    limit = max(1, min(limit, 200))
    user_id = _user_id()

    events = []
    try:
        all_ev = rt["store"].recent(limit=500, topic_prefix="mood.logged")
        for e in all_ev:
            p = e.get("payload") or {}
            if str(p.get("user_id") or "") == user_id:
                events.append(p)
            if len(events) >= limit:
                break
    except Exception:
        events = []

    return jsonify({"ok": True, "user_id": user_id, "items": events})
