from __future__ import annotations

"""
Deprecated Spotify routes.

This file existed in older versions of the repo but had syntax errors and was never reliably registered.
To avoid breaking imports and to preserve backwards compatibility, we now expose a tiny blueprint that
points people to the new /api/v2/spotify/* endpoints.

If you have a frontend calling these old endpoints, update it.
"""

from flask import Blueprint, jsonify

consolidated_spotify_bp = Blueprint("consolidated_spotify", __name__)


@consolidated_spotify_bp.get("/api/v2/spotify")
def spotify_root():
    return jsonify(
        {
            "ok": True,
            "deprecated": True,
            "message": "Use /api/v2/spotify/status, /api/v2/spotify/auth/url, /api/v2/spotify/sync, etc.",
        }
    )
