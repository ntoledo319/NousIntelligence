from __future__ import annotations
from flask import Blueprint, jsonify
from utils.unified_auth import require_auth

notification_bp = Blueprint("notifications", __name__)

@notification_bp.get("/notifications")
@require_auth(allow_demo=True)
def list_notifications():
    # Minimal, real, safe.
    return jsonify({"ok": True, "notifications": []})
