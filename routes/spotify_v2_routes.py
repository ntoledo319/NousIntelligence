from __future__ import annotations

import secrets
from typing import Any, Dict

from flask import Blueprint, jsonify, redirect, request, session

from utils.unified_auth import get_current_user
from utils.unified_spotify_services import spotify_service


spotify_v2_bp = Blueprint("spotify_v2", __name__)


def _user_id() -> str:
    user = get_current_user() or {}
    return str(user.get("id") or "demo_user")


@spotify_v2_bp.get("/status")
def spotify_status():
    uid = _user_id()
    return jsonify({
        "ok": True,
        "configured": spotify_service.is_configured(),
        "authenticated": spotify_service.is_authenticated(uid) if spotify_service.is_configured() else False,
        "user_id": uid
    })


@spotify_v2_bp.get("/auth")
def spotify_auth():
    if not spotify_service.is_configured():
        return jsonify({"ok": False, "error": "Spotify not configured"}), 400

    state = secrets.token_urlsafe(24)
    session["spotify_oauth_state"] = state
    session.modified = True

    url = spotify_service.build_auth_url(state)
    return redirect(url)


@spotify_v2_bp.get("/callback")
def spotify_callback():
    if not spotify_service.is_configured():
        return jsonify({"ok": False, "error": "Spotify not configured"}), 400

    err = request.args.get("error")
    if err:
        return jsonify({"ok": False, "error": err}), 400

    code = request.args.get("code")
    state = request.args.get("state")
    expected = session.pop("spotify_oauth_state", None)

    if not state or not expected or state != expected:
        return jsonify({"ok": False, "error": "Invalid state"}), 400

    if not code:
        return jsonify({"ok": False, "error": "Missing code"}), 400

    uid = _user_id()
    token = spotify_service.exchange_code(uid, code)
    return jsonify({"ok": True, "user_id": uid, "expires_at": token.get("expires_at"), "scope": token.get("scope")})


@spotify_v2_bp.post("/disconnect")
def spotify_disconnect():
    uid = _user_id()
    spotify_service.disconnect(uid)
    return jsonify({"ok": True})


@spotify_v2_bp.get("/now")
def spotify_now():
    uid = _user_id()
    try:
        return jsonify(spotify_service.now_playing(uid, enrich=True))
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@spotify_v2_bp.post("/sync/recent")
def spotify_sync_recent():
    uid = _user_id()
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    limit = int(payload.get("limit") or 25)
    try:
        return jsonify(spotify_service.sync_recently_played(uid, limit=limit))
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@spotify_v2_bp.post("/lyrics")
def spotify_lyrics():
    uid = _user_id()
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    track_id = payload.get("track_id")
    if not track_id:
        return jsonify({"ok": False, "error": "track_id required"}), 400
    try:
        enriched = spotify_service.enrich_track(uid, str(track_id), include_lyrics=True)
        return jsonify({"ok": True, "track_id": track_id, "enriched": enriched})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
