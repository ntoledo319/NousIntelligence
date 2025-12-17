from __future__ import annotations

"""
Spotify Client (Compatibility)

This repo historically had multiple half-finished Spotify clients and a bunch of features depended on
"spotipy-like" method names. The previous version of this file had syntax errors and could not be imported.

This module now provides:
  - SpotifyClient: thin wrapper around services.spotify.SpotifyAPI
  - get_spotify_client(): factory returning SpotifyClient for a user_id

Prefer importing from utils.spotify_helper in new code.
"""

import os
from typing import Any, Dict, Optional, Sequence

from flask import current_app

from services.spotify.spotify_api import SpotifyAPI, SpotifyConfig, DEFAULT_SCOPES
from services.spotify.spotify_store import SpotifyStore


def _db_path() -> str:
    inst = getattr(current_app, "instance_path", None) or os.getcwd()
    os.makedirs(inst, exist_ok=True)
    return os.path.join(inst, "spotify.db")


class SpotifyClient(SpotifyAPI):
    """
    Inherit SpotifyAPI so all methods + compatibility wrappers are available.
    """
    pass


def get_spotify_client(*, user_id: str, scopes: Optional[Sequence[str]] = None) -> SpotifyClient:
    cid = (os.environ.get("SPOTIFY_CLIENT_ID") or "").strip()
    sec = (os.environ.get("SPOTIFY_CLIENT_SECRET") or "").strip()
    red = (os.environ.get("SPOTIFY_REDIRECT_URI") or os.environ.get("SPOTIFY_REDIRECT") or "").strip()
    if not red:
        red = "http://localhost:5000/callback/spotify"
    sc = list(scopes) if scopes else list(DEFAULT_SCOPES)

    store = SpotifyStore(_db_path())
    cfg = SpotifyConfig(client_id=cid, client_secret=sec, redirect_uri=red, scopes=sc)
    return SpotifyClient(store, str(user_id or "anon"), cfg)
