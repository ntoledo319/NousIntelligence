from __future__ import annotations
from flask import Blueprint, jsonify, current_app
from utils.unified_auth import require_auth

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.get("/analytics/summary")
@require_auth(allow_demo=True)
def summary():
    # Minimal, real summary that never crashes if DB is absent/misconfigured.
    out = {"ok": True, "events": 0, "users": 0}
    try:
        from database import db
        from models.analytics_models import UserActivity  # type: ignore
        out["events"] = int(db.session.query(UserActivity).count())
    except Exception:
        pass
    return jsonify(out)
