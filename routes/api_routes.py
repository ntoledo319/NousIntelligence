from __future__ import annotations

import html
import time
from typing import Any, Dict

from flask import Blueprint, jsonify, request, session

from utils.unified_auth import require_auth

api_bp = Blueprint("api", __name__)

MAX_MESSAGE_LEN = 10000

def _escape_text(s: str) -> str:
    # Prevent XSS by escaping any user-controlled content
    return html.escape(s or "", quote=True)

def _demo_response(message: str) -> str:
    # Deterministic, safe fallback response (no external model required)
    m = message.strip()
    if not m:
        return "Say something and I'll respond. Telepathy isn't in the repo yet."
    return f"✅ Got it. You said: {_escape_text(m)}"

@api_bp.get("/health")
def health_v1():
    return jsonify({"ok": True, "ts": time.time()})

@api_bp.get("/status")
def status():
    return jsonify({"ok": True, "status": "running", "ts": time.time()})

@api_bp.get("/user")
def get_user():
    # Unauthenticated returns guest (keeps old behavior), but tests also check auth flows elsewhere.
    u = session.get("user")
    if isinstance(u, dict):
        return jsonify({"user": u})
    if session.get("user_id"):
        return jsonify({"user": {"id": str(session.get("user_id")), "name": session.get("username") or "User"}})
    return jsonify({"user": {"id": "guest", "name": "Guest"}})

@api_bp.route("/chat", methods=["GET", "POST"])
def chat_compat():
    # Back-compat endpoint used by some generated tests and demo HTML.
    if request.method == "GET":
        return jsonify({"ok": True, "message": "POST JSON {message: ...} to chat."})
    return chat_api()

@api_bp.post("/chat")
@require_auth(allow_demo=True)
def chat_api():
    if not request.is_json:
        return jsonify({"ok": False, "error": "json_required"}), 400

    data = request.get_json(silent=False) or {}
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "invalid_json"}), 400

    msg = str(data.get("message", "") or "")
    if not msg.strip():
        return jsonify({"ok": False, "error": "message_required"}), 400
    if len(msg) > MAX_MESSAGE_LEN:
        return jsonify({"ok": False, "error": "message_too_long", "limit": MAX_MESSAGE_LEN}), 413

    # Optional: store to nous_core runtime if present
    try:
        from services.runtime_service import init_runtime
        from flask import current_app
        rt = init_runtime(current_app)
        rt["bus"].publish("chat.message", {"message": msg})
        rt["semantic"].upsert(f"chat:{time.time()}", msg, {"kind": "chat"})
    except Exception:
        pass

    return jsonify({"response": _demo_response(msg)})
