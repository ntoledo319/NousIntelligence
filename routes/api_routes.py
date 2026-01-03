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

def _get_ai_response(message: str, user_id: str) -> Dict[str, Any]:
    """Get response from EmotionAwareTherapeuticAssistant"""
    try:
        from services.emotion_aware_therapeutic_assistant import EmotionAwareTherapeuticAssistant
        assistant = EmotionAwareTherapeuticAssistant()
        response = assistant.get_therapeutic_response(
            user_input=message,
            user_id=user_id,
            context={}
        )
        return response
    except Exception as e:
        import logging
        logging.error(f"AI response error: {e}")
        # Fallback
        return {
            'response': f"I hear you. You said: {_escape_text(message)}",
            'emotion': None,
            'skill_recommendations': []
        }

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

    user_id = session.get("user_id", "demo")
    
    # Get AI response
    ai_response = _get_ai_response(msg, user_id)
    
    # Optional: store to nous_core runtime if present
    try:
        from services.runtime_service import init_runtime
        from flask import current_app
        rt = init_runtime(current_app)
        rt["bus"].publish("chat.message", {"message": msg, "response": ai_response})
        rt["semantic"].upsert(f"chat:{time.time()}", msg, {"kind": "chat"})
    except Exception:
        pass

    return jsonify(ai_response)
