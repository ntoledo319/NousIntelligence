from __future__ import annotations

"""
Unified Spotify Services (Plugin)

This file was previously broken (syntax errors + placeholder code) and prevented the Spotify plugin
from loading reliably. It now provides a stable, minimal integration surface used by:

- utils.plugin_registry (loads get_unified_spotify_services)
- AI / health integrations (expects spotipy-ish client methods)
- /api/v2/spotify/* routes (for OAuth + ingestion)

If you want to expand Spotify features, do it in services/spotify/* and keep this as a thin wrapper.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import current_app

from services.spotify.spotify_api import SpotifyAPI, SpotifyAuthError
from services.spotify.spotify_store import SpotifyStore
from services.spotify.spotify_ingest import sync_recently_played


def _db_path() -> str:
    inst = getattr(current_app, "instance_path", None) or os.getcwd()
    os.makedirs(inst, exist_ok=True)
    return os.path.join(inst, "spotify.db")


@dataclass
class UnifiedSpotifyService:
    name: str = "unified_spotify_services"

    def is_available(self) -> bool:
        return bool(os.environ.get("SPOTIFY_CLIENT_ID") and os.environ.get("SPOTIFY_CLIENT_SECRET"))

    def _store(self) -> SpotifyStore:
        return SpotifyStore(_db_path())

    def get_client(self, user_id: str) -> SpotifyAPI:
        return SpotifyAPI.from_env(self._store(), str(user_id or "anon"))

    def is_connected(self, user_id: str) -> bool:
        try:
            return self.get_client(user_id).is_connected()
        except Exception:
            return False

    def disconnect(self, user_id: str) -> None:
        try:
            self.get_client(user_id).disconnect()
        except Exception:
            pass

    def sync(self, *, rt: Dict[str, Any], user_id: str, limit: int = 50) -> Dict[str, Any]:
        client = self.get_client(user_id)
        return sync_recently_played(rt=rt, spotify=client, store=self._store(), user_id=str(user_id or "anon"), limit=limit)


_service_singleton: Optional[UnifiedSpotifyService] = None


def get_unified_spotify_services() -> UnifiedSpotifyService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = UnifiedSpotifyService()
    return _service_singleton
