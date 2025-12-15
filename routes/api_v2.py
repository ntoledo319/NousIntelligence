from __future__ import annotations
import os
import time
from functools import wraps
from typing import Any, Dict, List

import requests
from flask import Blueprint, current_app, jsonify, request

api_v2_bp = Blueprint("api_v2", __name__)

def _auth_optional(fn):
    @wraps(fn)
    def w(*args, **kwargs):
        # Bypass auth in tests.
        if current_app.config.get("TESTING") or current_app.config.get("TESTING_MODE"):
            return fn(*args, **kwargs)
        # If unified auth exists, enforce it; otherwise allow.
        try:
            from utils.unified_auth import require_auth
            return require_auth(allow_demo=True)(fn)(*args, **kwargs)
        except Exception:
            return fn(*args, **kwargs)
    return w

def _rt() -> Dict[str, Any]:
    from services.runtime_service import init_runtime
    return init_runtime(current_app)

@api_v2_bp.get("/health")
def health():
    return jsonify({"ok": True})

# ── Plugins ──────────────────────────────────────────────────────────
@api_v2_bp.get("/plugins/status")
@_auth_optional
def plugins_status():
    try:
        from utils.plugin_registry import get_plugin_status
        return jsonify({"ok": True, "plugins": get_plugin_status()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ── Events ───────────────────────────────────────────────────────────
@api_v2_bp.post("/events/publish")
@_auth_optional
def events_publish():
    d = request.get_json(force=True, silent=False) or {}
    topic = (d.get("topic") or "").strip()
    payload = d.get("payload") or {}
    if not topic:
        return jsonify({"ok": False, "error": "missing topic"}), 400
    bus = _rt()["bus"]
    res = bus.publish(topic, payload)
    return jsonify(res)

@api_v2_bp.get("/events/recent")
@_auth_optional
def events_recent():
    prefix = request.args.get("prefix")
    limit = int(request.args.get("limit", "50"))
    store = _rt()["store"]
    return jsonify({"ok": True, "events": store.recent(limit=limit, topic_prefix=prefix)})

# ── Semantic Memory ──────────────────────────────────────────────────
@api_v2_bp.post("/semantic/upsert")
@_auth_optional
def semantic_upsert():
    d = request.get_json(force=True, silent=False) or {}
    doc_id = (d.get("doc_id") or "").strip()
    text = d.get("text") or ""
    meta = d.get("meta") or {}
    if not doc_id or not text:
        return jsonify({"ok": False, "error": "doc_id and text required"}), 400
    sem = _rt()["semantic"]
    sem.upsert(doc_id, text, meta)
    return jsonify({"ok": True, "doc_id": doc_id})

@api_v2_bp.get("/semantic/search")
@_auth_optional
def semantic_search():
    q = request.args.get("q", "")
    k = int(request.args.get("k", "10"))
    sem = _rt()["semantic"]
    return jsonify({"ok": True, "q": q, "results": sem.search(q, top_k=k)})

# ── Quality Gate ─────────────────────────────────────────────────────
@api_v2_bp.post("/quality/score")
@_auth_optional
def quality_score():
    from nous_core.quality import score
    d = request.get_json(force=True, silent=False) or {}
    text = d.get("text") or ""
    return jsonify({"ok": True, **score(text)})

# ── Monitoring ───────────────────────────────────────────────────────
@api_v2_bp.get("/monitoring/snapshot")
@_auth_optional
def monitoring_snapshot():
    from nous_core.monitoring import snapshot
    return jsonify({"ok": True, "snapshot": snapshot()})

# ── Policy ───────────────────────────────────────────────────────────
@api_v2_bp.post("/policy/evaluate")
@_auth_optional
def policy_evaluate():
    d = request.get_json(force=True, silent=False) or {}
    policy = _rt()["policy"]
    return jsonify({"ok": True, "result": policy.evaluate(d)})

# ── FREE API INTEGRATION #1: Open-Meteo ───────────────────────────────
@api_v2_bp.get("/weather/current")
@_auth_optional
def weather_current():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"ok": False, "error": "lat/lon required"}), 400
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,precipitation,wind_speed_10m", "timezone": "auto"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return jsonify({"ok": True, "data": r.json()})

# ── FREE API INTEGRATION #2: OSM Nominatim ─────────────────────────────
@api_v2_bp.get("/maps/geocode")
@_auth_optional
def maps_geocode():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": False, "error": "q required"}), 400
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "json", "limit": 5}
    headers = {"User-Agent": "NOUSIntelligence/1.0 (local dev)"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return jsonify({"ok": True, "results": r.json()})

# ── NEW FEATURE #1: Journal append + semantic index ────────────────────
@api_v2_bp.post("/journal/append")
@_auth_optional
def journal_append():
    d = request.get_json(force=True, silent=False) or {}
    text = (d.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "text required"}), 400
    topic = "journal.entry"
    payload = {"text": text, "tags": d.get("tags") or [], "ts": time.time()}
    rt = _rt()
    rt["store"].append(topic, payload)
    rt["semantic"].upsert(f"journal:{payload['ts']}", text, {"kind": "journal", "tags": payload["tags"]})
    return jsonify({"ok": True, "stored": True})

@api_v2_bp.get("/journal/search")
@_auth_optional
def journal_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": True, "results": []})
    rt = _rt()
    res = rt["semantic"].search(q, top_k=10)
    # Only return journal docs
    res = [r for r in res if (r.get("meta") or {}).get("kind") == "journal"]
    return jsonify({"ok": True, "results": res})

# ── NEW FEATURE #2: Habits check-in + streak summary ───────────────────
@api_v2_bp.post("/habits/checkin")
@_auth_optional
def habits_checkin():
    d = request.get_json(force=True, silent=False) or {}
    habit = (d.get("habit") or "").strip()
    if not habit:
        return jsonify({"ok": False, "error": "habit required"}), 400
    rt = _rt()
    rt["store"].append("habit.checkin", {"habit": habit, "ts": time.time()})
    return jsonify({"ok": True})

@api_v2_bp.get("/habits/streaks")
@_auth_optional
def habits_streaks():
    rt = _rt()
    events = rt["store"].recent(limit=500, topic_prefix="habit.checkin")
    # naive streak: count checkins in last 24h per habit
    now = time.time()
    per: Dict[str, int] = {}
    for e in events:
        ts = float(e["ts"])
        if now - ts > 24 * 3600:
            continue
        h = (e["payload"] or {}).get("habit") or "unknown"
        per[h] = per.get(h, 0) + 1
    return jsonify({"ok": True, "last_24h": per})

# ── NEW FEATURE #3: Random quote (free; fallback) ──────────────────────
@api_v2_bp.get("/quote/random")
@_auth_optional
def quote_random():
    try:
        r = requests.get("https://api.quotable.io/random", timeout=8)
        r.raise_for_status()
        j = r.json()
        return jsonify({"ok": True, "quote": j.get("content"), "author": j.get("author")})
    except Exception:
        return jsonify({"ok": True, "quote": "Do the next right thing. Then do it again.", "author": "NOUS (fallback)"})

# ── NEW FEATURE #4: Daily briefing ────────────────────────────────────
@api_v2_bp.get("/briefing/daily")
@_auth_optional
def briefing_daily():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    rt = _rt()

    weather = None
    if lat and lon:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,precipitation,wind_speed_10m", "timezone": "auto"}
            weather = requests.get(url, params=params, timeout=8).json()
        except Exception:
            weather = None

    habits = habits_streaks().get_json()  # type: ignore
    quote = quote_random().get_json()     # type: ignore

    return jsonify({
        "ok": True,
        "weather": weather,
        "habits": habits.get("last_24h") if isinstance(habits, dict) else {},
        "quote": {"text": quote.get("quote"), "author": quote.get("author")} if isinstance(quote, dict) else {},
    })

# ── NEW FEATURE #5: Copy/paste export bundle ───────────────────────────
@api_v2_bp.get("/export/text")
@_auth_optional
def export_text():
    rt = _rt()
    ev = rt["store"].recent(limit=50)
    lines: List[str] = []
    lines.append("NOUS EXPORT")
    lines.append("────────────────────────")
    for e in ev:
        lines.append(f"- {e['topic']} @ {int(e['ts'])}: {e['payload']}")
    return jsonify({"ok": True, "text": "\n".join(lines)})

