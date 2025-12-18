from __future__ import annotations

import os
import secrets
import time
from datetime import datetime
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, redirect, request, session, g

from services.runtime_service import init_runtime
from services.spotify.spotify_api import SpotifyAPI, SpotifyAuthError
from services.spotify.spotify_store import SpotifyStore
from services.spotify.spotify_ingest import sync_recently_played
from services.spotify.ritual import run_spotify_ritual
from utils.unified_auth import demo_allowed, get_demo_user


spotify_bp = Blueprint("spotify_api", __name__)


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _user() -> Dict[str, Any]:
    u = getattr(g, "user", None)
    if isinstance(u, dict) and u.get("id"):
        return u
    return get_demo_user()


def _user_id() -> str:
    return str(_user().get("id") or "demo_user")


def _store() -> SpotifyStore:
    db = os.path.join(current_app.instance_path, "spotify.db")
    return SpotifyStore(db)


def _spotify() -> SpotifyAPI:
    return SpotifyAPI.from_env()


def _ritual_secret_ok() -> bool:
    secret = os.environ.get("RITUAL_SECRET", "").strip()
    if not secret:
        return False
    got = request.headers.get("X-Ritual-Secret", "").strip()
    if got and secrets.compare_digest(got, secret):
        return True
    got2 = request.args.get("ritual_secret", "").strip()
    if got2 and secrets.compare_digest(got2, secret):
        return True
    return False


def _ensure_token(store: SpotifyStore, user_id: str) -> Optional[Dict[str, Any]]:
    tok = store.get_tokens(user_id)
    if not tok:
        return None
    if float(tok.get("expires_at") or 0) > time.time():
        return tok
    refresh = tok.get("refresh_token")
    if not refresh:
        return None
    api = _spotify()
    new_tok = api.refresh(str(refresh))
    store.save_tokens(user_id, new_tok)
    return new_tok


@spotify_bp.route("/authorize_spotify")
@demo_allowed
def authorize_spotify():
    api = _spotify()
    state = secrets.token_urlsafe(24)
    session["spotify_oauth_state"] = state
    session["spotify_oauth_user_id"] = _user_id()
    return redirect(api.build_authorize_url(state=state))


@spotify_bp.route("/callback/spotify")
@demo_allowed
def callback_spotify():
    err = request.args.get("error")
    if err:
        return jsonify({"ok": False, "error": err}), 400

    code = request.args.get("code")
    state = request.args.get("state")
    expected = session.get("spotify_oauth_state")

    if not code or not state or not expected or state != expected:
        return jsonify({"ok": False, "error": "invalid oauth state"}), 400

    api = _spotify()
    store = _store()

    try:
        tok = api.exchange_code(code)
    except SpotifyAuthError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    uid = session.get("spotify_oauth_user_id") or _user_id()
    store.save_tokens(str(uid), tok)

    return redirect("/")


@spotify_bp.route("/api/v2/spotify/status")
@demo_allowed
def spotify_status():
    store = _store()
    uid = _user_id()
    tok = store.get_tokens(uid)
    return jsonify(
        {
            "ok": True,
            "user_id": uid,
            "connected": bool(tok),
            "expires_at": (tok or {}).get("expires_at"),
            "scopes": (tok or {}).get("scope"),
        }
    )


@spotify_bp.route("/api/v2/spotify/disconnect", methods=["POST"])
@demo_allowed
def spotify_disconnect():
    store = _store()
    uid = _user_id()
    store.delete_tokens(uid)
    return jsonify({"ok": True, "user_id": uid, "connected": False})


@spotify_bp.route("/api/v2/spotify/sync/recently-played", methods=["POST"])
@demo_allowed
def spotify_sync_recently_played():
    rt = init_runtime(current_app)
    store = _store()
    uid = _user_id()
    tok = _ensure_token(store, uid)
    if not tok:
        return jsonify({"ok": False, "error": "Spotify not connected. Hit /authorize_spotify first."}), 400
    data = request.get_json(silent=True) or {}
    limit = int(data.get("limit", 50))
    limit = max(1, min(limit, 50))
    enrich = bool(data.get("enrich", True))
    lyrics = bool(data.get("lyrics", True))
    out = sync_recently_played(
        spotify=_spotify(),
        store=store,
        access_token=tok["access_token"],
        runtime=rt,
        user_id=uid,
        limit=limit,
        enrich=enrich,
        lyrics=lyrics,
    )
    return jsonify(out)


@spotify_bp.route("/api/v2/spotify/lyrics/<track_id>")
@demo_allowed
def spotify_lyrics(track_id: str):
    store = _store()
    a = store.get_lyrics_analysis(track_id)
    if not a:
        return jsonify({"ok": False, "error": "no lyrics analysis cached for this track yet"}), 404
    return jsonify({"ok": True, "track_id": track_id, "lyrics_analysis": a})


@spotify_bp.route("/api/v2/spotify/ritual/run", methods=["POST"])
def spotify_ritual_run():
    if not _ritual_secret_ok():
        return demo_allowed(_spotify_ritual_run_authed)()
    return _spotify_ritual_run_core()


def _spotify_ritual_run_authed():
    return _spotify_ritual_run_core()


def _spotify_ritual_run_core():
    rt = init_runtime(current_app)
    store = _store()
    data = request.get_json(silent=True) or {}

    uid = _user_id()
    # If this run is triggered via ritual secret (cron), allow explicitly targeting a stored user_id.
    if _ritual_secret_ok():
        req_uid = str((data.get("user_id") or "")).strip()
        if req_uid:
            uid = req_uid

    tok = _ensure_token(store, uid)
    if not tok:
        return jsonify({"ok": False, "error": "Spotify not connected. Hit /authorize_spotify first."}), 400

    target = data.get("target")
    limit = int(data.get("limit", 50))
    limit = max(1, min(limit, 100))
    create_playlist = bool(data.get("create_playlist", True))
    playlist_name = data.get("playlist_name")
    playlist_public = bool(data.get("playlist_public", False))
    enrich = bool(data.get("enrich", True))
    lyrics = bool(data.get("lyrics", True))

    out = run_spotify_ritual(
        spotify=_spotify(),
        store=store,
        access_token=tok["access_token"],
        runtime=rt,
        user_id=uid,
        target=target,
        limit=limit,
        create_playlist=create_playlist,
        playlist_name=playlist_name,
        playlist_public=playlist_public,
        enrich=enrich,
        lyrics=lyrics,
    )
    return jsonify(out)
