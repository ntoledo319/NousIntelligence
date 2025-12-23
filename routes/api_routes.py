from __future__ import annotations

import html
import time
import re
from typing import Any, Dict

from flask import Blueprint, jsonify, request, session

from utils.unified_auth import require_auth

api_bp = Blueprint("api", __name__)

MAX_MESSAGE_LEN = 10000


def _escape_text(s: str) -> str:
    """
    Normalize and escape user-controlled text for safe display.

    - HTML-escape content to prevent tag injection.
    - Strip dangerous URL schemes like ``javascript:``.
    - Remove inline JS event handlers such as ``onload=``.
    - Drop any embedded null bytes.
    """
    text = s or ""
    # Remove null bytes that can confuse downstream parsers
    text = text.replace("\x00", "")

    # Strip dangerous protocols and inline event handlers
    dangerous_patterns = [
        r"javascript\s*:",
        r"vbscript\s*:",
        r"data\s*:",
        r"on\w+\s*=",  # onload=, onclick=, etc.
    ]
    for pat in dangerous_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)

    # Finally, HTML-escape for safe rendering
    return html.escape(text, quote=True)

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

    # Use DialogueManager for processing
    try:
        from services.dialogue_manager import DialogueManager
        # In a real app, instantiate once or via factory
        dm = DialogueManager()

        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
             # Handle demo user / guest case
             # For now, if no user_id, we might need a dummy user or return error
             # But the PDF implies logged-in state for therapy.
             # We'll rely on the existing auth check. If guest, maybe 0?
             # Let's check session structure.
             user = session.get('user')
             if user and isinstance(user, dict):
                 user_id = user.get('id')

        if not user_id:
            # Create a temporary guest user if none exists (for demo)
            # This requires database write access which might be tricky in pure GET/POST flow without login
            # Fallback to demo response if no user context
             return jsonify({"response": _demo_response(msg)})

        response_data = dm.process_message(int(user_id), msg)

        # Format for frontend
        return jsonify({
            "ok": True,
            "response": response_data.get('text', ''),
            "type": response_data.get('type'),
            "suggested_actions": response_data.get('suggested_actions', []),
            "resources": response_data.get('resources', [])
        })

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Dialogue processing error: {e}")
        return jsonify({"ok": False, "error": "internal_error", "details": str(e)}), 500
