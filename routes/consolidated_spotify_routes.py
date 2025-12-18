"""
Legacy Spotify routes (compat layer).

This file used to be broken enough to qualify as performance art.
Now it stays import-safe and points developers to the v2 Spotify API.

Preferred endpoints:
  - /api/v2/spotify/auth
  - /api/v2/spotify/callback
  - /api/v2/spotify/status
  - /api/v2/spotify/now
"""

from __future__ import annotations

from flask import Blueprint, redirect

legacy_spotify_bp = Blueprint("legacy_spotify", __name__)

@legacy_spotify_bp.get("/spotify/auth")
def legacy_auth_redirect():
    return redirect("/api/v2/spotify/auth")

@legacy_spotify_bp.get("/spotify/callback")
def legacy_callback_redirect():
    return redirect("/api/v2/spotify/callback")
