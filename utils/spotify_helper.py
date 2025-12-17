from __future__ import annotations

import os
import secrets
from typing import Any, Dict, Optional, Sequence, Tuple

from flask import current_app

from services.spotify.spotify_store import SpotifyStore
from services.spotify.spotify_api import SpotifyAPI, SpotifyConfig, DEFAULT_SCOPES, SpotifyAuthError


def _instance_db_path() -> str:
    try:
        inst = current_app.instance_path
    except Exception:
        inst = os.getcwd()
    os.makedirs(inst, exist_ok=True)
    return os.path.join(inst, "spotify.db")


def get_spotify_client(
    session_obj,
    client_id: Optional[str],
    client_secret: Optional[str],
    redirect_uri: Optional[str],
    user_id: str,
    scopes: Optional[Sequence[str]] = None,
) -> Tuple[Optional[SpotifyAPI], Optional[str]]:
    """
    Compatibility helper used around the repo.

    Returns:
      (spotify_client, auth_url)
        - spotify_client is a SpotifyAPI instance with spotipy-ish methods (search/devices/start_playback/etc)
        - auth_url is a direct Spotify authorization URL (optional)

    Notes:
      - If tokens exist in the local SpotifyStore, spotify_client is returned.
      - If not connected, spotify_client is None and auth_url is returned.
      - We also stash oauth 'state' in the session (spotify_oauth_state).
    """
    cid = (client_id or os.environ.get("SPOTIFY_CLIENT_ID") or "").strip()
    sec = (client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET") or "").strip()
    red = (redirect_uri or os.environ.get("SPOTIFY_REDIRECT_URI") or os.environ.get("SPOTIFY_REDIRECT") or "").strip()
    if not red:
        red = "http://localhost:5000/callback/spotify"

    if not cid or not sec:
        # Missing config; treat as "not connected" but don't explode the whole app
        return None, None

    sc = list(scopes) if scopes else list(DEFAULT_SCOPES)
    store = SpotifyStore(_instance_db_path())
    api = SpotifyAPI(store, str(user_id or "anon"), SpotifyConfig(client_id=cid, client_secret=sec, redirect_uri=red, scopes=sc))

    if api.is_connected():
        return api, None

    state = secrets.token_urlsafe(24)
    try:
        session_obj["spotify_oauth_state"] = state
    except Exception:
        pass

    try:
        auth_url = api.get_authorize_url(state=state, show_dialog=False)
    except Exception:
        auth_url = None
    return None, auth_url


def spotify_is_connected(user_id: str) -> bool:
    try:
        store = SpotifyStore(_instance_db_path())
        api = SpotifyAPI.from_env(store, str(user_id or "anon"))
        return api.is_connected()
    except Exception:
        return False
