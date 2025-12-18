from __future__ import annotations

import functools
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from flask import current_app, jsonify, redirect, request, session, url_for, g

DEMO_USER: Dict[str, Any] = {
    "id": "demo_user",
    "name": "Demo User",
    "email": "demo@nous.app",
    "demo_mode": True,
    "is_guest": True,
}

SessionUser = Dict[str, Any]
ViewFn = Callable[..., Any]


def init_auth(app) -> None:
    """Optional init hook. Keep it harmless and compatible."""
    app.config.setdefault("SESSION_TIMEOUT_SECONDS", 60 * 60 * 6)  # 6 hours
    app.config.setdefault("AUTH_DEMO_ALLOWED", True)


def _is_testing() -> bool:
    try:
        return bool(current_app.config.get("TESTING") or current_app.config.get("TESTING_MODE"))
    except Exception:
        return False


def _now_ts() -> float:
    return datetime.utcnow().timestamp()


def _session_timeout_seconds() -> int:
    try:
        return int(current_app.config.get("SESSION_TIMEOUT_SECONDS", 60 * 60 * 6))
    except Exception:
        return 60 * 60 * 6


def _rotate_session() -> None:
    # Flask cookie sessions "rotate" by clearing and changing contents.
    session.clear()
    session["session_rotated_at"] = _now_ts()
    session.modified = True


def _touch_last_activity() -> None:
    session["last_activity"] = _now_ts()
    session.modified = True


def _is_expired() -> bool:
    last = session.get("last_activity")
    if not isinstance(last, (int, float)):
        return False
    return (_now_ts() - float(last)) > float(_session_timeout_seconds())


def _build_user_from_session() -> Optional[SessionUser]:
    # Support legacy keys used across this repo.
    if isinstance(session.get("user"), dict):
        return session["user"]
    user_id = session.get("user_id")
    if user_id:
        return {
            "id": str(user_id),
            "name": session.get("username") or session.get("name") or "User",
            "email": session.get("email") or "",
            "demo_mode": bool(session.get("demo_mode", False)),
        }
    return None


def _extract_bearer_token() -> Optional[str]:
    h = request.headers.get("Authorization", "")
    if not h:
        return None
    parts = h.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def _auth_user_from_bearer(token: str) -> Optional[SessionUser]:
    if not token:
        return None

    # In tests accept any token so fixtures can authenticate without DB.
    if _is_testing():
        return {"id": "api_test_user", "name": "API Test User", "email": "", "api": True}

    # Production: if an API key validator exists, try it.
    try:
        from utils.api_key_manager import APIKeyManager  # type: ignore
        mgr = APIKeyManager()
        if mgr.validate_api_key(token):
            return {"id": "api_key_user", "name": "API User", "email": "", "api": True}
    except Exception:
        pass

    return None


def is_authenticated() -> bool:
    if _is_expired():
        _rotate_session()
        return False
    return bool(_build_user_from_session())


def get_demo_user() -> SessionUser:
    return dict(DEMO_USER)


def get_current_user() -> Optional[SessionUser]:
    """Get current user from session or bearer token."""
    if _is_expired():
        _rotate_session()
    
    # Try bearer token first
    tok = _extract_bearer_token()
    if tok and not _build_user_from_session():
        u = _auth_user_from_bearer(tok)
        if u:
            session["user"] = u
            _touch_last_activity()
            return u
    
    # Return session user
    user = _build_user_from_session()
    if user:
        _touch_last_activity()
    return user


def _wants_json() -> bool:
    p = request.path or ""
    accept = request.headers.get("Accept") or ""
    return p.startswith("/api") or request.is_json or "application/json" in accept


def require_auth(allow_demo: bool = False) -> Callable[[ViewFn], ViewFn]:
    """
    Enforce auth for browser + API routes.
    - Session auth supports: session['user'] dict OR session['user_id']
    - API auth supports: Authorization: Bearer <token>
    - Demo allowed only if allow_demo=True and request explicitly asks for demo.
    """
    def decorator(fn: ViewFn) -> ViewFn:
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            # Session timeout
            if _is_expired():
                _rotate_session()

            # Bearer token auth (API clients)
            tok = _extract_bearer_token()
            if tok and not _build_user_from_session():
                u = _auth_user_from_bearer(tok)
                if u:
                    session["user"] = u
                    _touch_last_activity()

            user = _build_user_from_session()

            # Explicit demo request
            demo_requested = False
            if str(request.args.get("demo", "")).lower() in ("1", "true", "yes"):
                demo_requested = True
            if str(request.headers.get("X-Demo-Mode", "")).lower() in ("1", "true", "yes"):
                demo_requested = True
            if not demo_requested and request.is_json:
                d = request.get_json(silent=True) or {}
                if isinstance(d, dict) and bool(d.get("demo_mode")):
                    demo_requested = True

            if not user and allow_demo and demo_requested and current_app.config.get("AUTH_DEMO_ALLOWED", True):
                user = get_demo_user()
                session["user"] = user
                _touch_last_activity()

            if not user:
                if _wants_json():
                    return jsonify({"ok": False, "error": "auth_required"}), 401
                return redirect(url_for("auth.login"))

            g.user = user
            _touch_last_activity()
            return fn(*args, **kwargs)

        return wrapped  # type: ignore[misc]
    return decorator


# Aliases used around the repo
login_required = require_auth(allow_demo=False)

def demo_allowed(fn: ViewFn) -> ViewFn:
    return require_auth(allow_demo=True)(fn)
