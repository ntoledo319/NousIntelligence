from __future__ import annotations

import os
import secrets
import logging
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, redirect, request, session, url_for, g

from utils.unified_auth import require_auth, demo_allowed, get_demo_user, is_authenticated
from services.runtime_service import init_runtime
from services.spotify.spotify_store import SpotifyStore
from services.spotify.spotify_api import SpotifyAPI, SpotifyAuthError, SpotifyAPIError
from services.spotify.spotify_ingest import sync_recently_played

logger = logging.getLogger(__name__)

spotify_bp = Blueprint("spotify", __name__)


def _store() -> SpotifyStore:
    db_path = os.path.join(current_app.instance_path, "spotify.db")
    return SpotifyStore(db_path)


def _user_id() -> str:
    u = getattr(g, "user", None) or session.get("user") or {}
    uid = u.get("id") or u.get("user_id") or session.get("user_id")
    return str(uid or "anon")


def _spotify() -> SpotifyAPI:
    return SpotifyAPI.from_env(_store(), _user_id())


def _wants_json() -> bool:
    accept = (request.headers.get("Accept") or "").lower()
    return "application/json" in accept or request.path.startswith("/api/")


def _json_error(msg: str, status: int = 400, *, details: Optional[Dict[str, Any]] = None):
    payload = {"ok": False, "error": msg}
    if details:
        payload["details"] = details
    return jsonify(payload), status


@spotify_bp.get("/api/v2/spotify/status")
@demo_allowed
def spotify_status():
    try:
        sp = _spotify()
        return jsonify(
            {
                "ok": True,
                "connected": sp.is_connected(),
                "redirect_uri": sp.cfg.redirect_uri,
                "scopes": sp.cfg.scopes,
            }
        )
    except SpotifyAuthError as e:
        return jsonify({"ok": True, "connected": False, "error": str(e)})


@spotify_bp.get("/api/v2/spotify/auth/url")
@demo_allowed
def spotify_auth_url():
    """
    Returns an authorization URL (JSON) or redirects (browser).
    """
    try:
        sp = _spotify()
    except SpotifyAuthError as e:
        return _json_error(str(e), 500)

    state = secrets.token_urlsafe(24)
    session["spotify_oauth_state"] = state
    url = sp.get_authorize_url(state=state, show_dialog=False)

    if _wants_json():
        return jsonify({"ok": True, "url": url})
    return redirect(url)


@spotify_bp.get("/callback/spotify")
@demo_allowed
def spotify_callback():
    """
    Spotify OAuth redirect target.
    Make sure SPOTIFY_REDIRECT_URI matches this URL in Spotify dashboard.
    """
    # Demo mode: just pretend success.
    if (getattr(g, "user", None) or {}).get("demo_mode"):
        return redirect(url_for("main.index"))

    err = request.args.get("error")
    if err:
        return _json_error(f"spotify_oauth_error:{err}", 400)

    code = request.args.get("code")
    state = request.args.get("state")
    expected = session.get("spotify_oauth_state")

    if not code:
        return _json_error("missing_code", 400)
    if expected and state and state != expected:
        return _json_error("state_mismatch", 400)

    try:
        sp = _spotify()
        sp.exchange_code(code)
    except Exception as e:
        logger.exception("Spotify code exchange failed")
        return _json_error(f"token_exchange_failed:{e}", 500)

    # Landing: back to UI root
    if _wants_json():
        return jsonify({"ok": True, "connected": True})
    return redirect(url_for("main.index"))


@spotify_bp.post("/api/v2/spotify/disconnect")
@demo_allowed
def spotify_disconnect():
    try:
        sp = _spotify()
        sp.disconnect()
        return jsonify({"ok": True, "connected": False})
    except Exception as e:
        return _json_error(str(e), 500)


@spotify_bp.get("/api/v2/spotify/devices")
@demo_allowed
def spotify_devices():
    try:
        sp = _spotify()
        return jsonify({"ok": True, "devices": sp.devices()})
    except SpotifyAuthError as e:
        return _json_error(str(e), 401)
    except SpotifyAPIError as e:
        return _json_error(str(e), 502, details=e.details)


@spotify_bp.get("/api/v2/spotify/search")
@demo_allowed
def spotify_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return _json_error("missing_q", 400)
    typ = (request.args.get("type") or "track").strip()
    limit = int(request.args.get("limit") or 5)
    try:
        sp = _spotify()
        return jsonify({"ok": True, "results": sp.search(q=q, type=typ, limit=limit)})
    except SpotifyAuthError as e:
        return _json_error(str(e), 401)
    except SpotifyAPIError as e:
        return _json_error(str(e), 502, details=e.details)


@spotify_bp.post("/api/v2/spotify/play")
@demo_allowed
def spotify_play():
    """
    Play by URI(s) or by search query.
    Body:
      { "uris": ["spotify:track:..."], "device_id": "...", "position_ms": 0 }
    or
      { "query": "artist - song", "device_id": "..." }
    """
    d = request.get_json(force=True, silent=True) or {}
    uris = d.get("uris")
    query = (d.get("query") or "").strip()
    device_id = d.get("device_id")
    position_ms = d.get("position_ms")

    try:
        sp = _spotify()
        if query and not uris:
            res = sp.search(q=query, type="track", limit=1)
            items = ((res.get("tracks") or {}).get("items")) or []
            if not items:
                return _json_error(f"no_tracks_found:{query}", 404)
            uris = [items[0]["uri"]]
        if not uris:
            return _json_error("missing_uris_or_query", 400)

        sp.start_playback(uris=list(uris), device_id=device_id, position_ms=position_ms)
        return jsonify({"ok": True})
    except SpotifyAuthError as e:
        return _json_error(str(e), 401)
    except SpotifyAPIError as e:
        return _json_error(str(e), 502, details=e.details)


@spotify_bp.post("/api/v2/spotify/pause")
@demo_allowed
def spotify_pause():
    d = request.get_json(force=True, silent=True) or {}
    device_id = d.get("device_id")
    try:
        sp = _spotify()
        sp.pause_playback(device_id=device_id)
        return jsonify({"ok": True})
    except SpotifyAuthError as e:
        return _json_error(str(e), 401)
    except SpotifyAPIError as e:
        return _json_error(str(e), 502, details=e.details)


@spotify_bp.post("/api/v2/spotify/sync")
@demo_allowed
def spotify_sync():
    """
    Ingest recently played tracks into NOUS runtime.
    Body:
      { "limit": 50, "enrich": true, "audio_features": true, "lyrics": true, "store_full_lyrics": false }
    """
    d = request.get_json(force=True, silent=True) or {}
    limit = int(d.get("limit") or 50)
    enrich = bool(d.get("enrich", True))
    audio_features = bool(d.get("audio_features", True))
    lyrics = bool(d.get("lyrics", True))
    store_full_lyrics = bool(d.get("store_full_lyrics", False))

    # Optional: user-provided lyrics dict {track_id: lyrics}
    user_lyrics = d.get("user_lyrics")
    if user_lyrics is not None and not isinstance(user_lyrics, dict):
        return _json_error("user_lyrics_must_be_object", 400)

    try:
        sp = _spotify()
        st = _store()
        rt = init_runtime(current_app)
        out = sync_recently_played(
            rt=rt,
            spotify=sp,
            store=st,
            user_id=_user_id(),
            limit=limit,
            enrich=enrich,
            include_audio_features=audio_features,
            include_lyrics=lyrics,
            allow_store_full_lyrics=store_full_lyrics,
            user_provided_lyrics=user_lyrics,
        )
        return jsonify(out)
    except SpotifyAuthError as e:
        return _json_error(str(e), 401)
    except SpotifyAPIError as e:
        return _json_error(str(e), 502, details=e.details)
    except Exception as e:
        logger.exception("spotify_sync failed")
        return _json_error(str(e), 500)


@spotify_bp.post("/api/v2/spotify/lyrics/upload")
@demo_allowed
def spotify_lyrics_upload():
    """
    Body:
      { "track_id": "...", "lyrics": "...", "store_full_lyrics": false }
    Stores lyrics analysis for later ingestion/sync.
    """
    d = request.get_json(force=True, silent=True) or {}
    track_id = (d.get("track_id") or "").strip()
    lyrics = (d.get("lyrics") or "").strip()
    store_full = bool(d.get("store_full_lyrics", False))
    if not track_id or not lyrics:
        return _json_error("missing_track_id_or_lyrics", 400)

    from services.spotify.lyrics.analyzer import analyze_lyrics

    analysis = analyze_lyrics(lyrics)
    payload: Dict[str, Any] = {"provider": "user_upload", "analysis": analysis}
    if store_full:
        payload["lyrics"] = lyrics
    _store().put_lyrics_analysis(track_id, payload)
    return jsonify({"ok": True, "track_id": track_id, "analysis": analysis})


@spotify_bp.get("/api/v2/spotify/track/<track_id>")
@demo_allowed
def spotify_track_detail(track_id: str):
    st = _store()
    tr = st.get_track(track_id) or {}
    mb = st.get_enrichment(track_id, "musicbrainz")
    tags = st.get_enrichment(track_id, "lastfm_tags")
    ly = st.get_lyrics_analysis(track_id)
    return jsonify({"ok": True, "track": tr, "musicbrainz": mb, "lastfm": tags, "lyrics": ly})


# ── Compatibility aliases ─────────────────────────────────────────────

def register_aliases(app):
    """
    Old parts of the repo call url_for("authorize_spotify") and expect /callback/spotify.

    Instead of touching every ancient file, we create global endpoint aliases.
    """
    # Avoid double-registration if called twice
    if "authorize_spotify" not in app.view_functions:
        app.add_url_rule("/authorize_spotify", endpoint="authorize_spotify", view_func=spotify_auth_url, methods=["GET"])
    if "spotify_callback" not in app.view_functions:
        app.add_url_rule("/callback/spotify", endpoint="spotify_callback", view_func=spotify_callback, methods=["GET"])
