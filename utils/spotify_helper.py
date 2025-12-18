from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

from flask import session

from integrations.spotify import SpotifyAPI, SpotifyOAuth


@dataclass
class SpotifyClientBundle:
    """Compatibility wrapper.

    Allows:
      client, auth = get_spotify_client()
    AND:
      client = get_spotify_client()
    """

    client: SpotifyAPI
    auth: SpotifyOAuth

    def __iter__(self) -> Iterator[Any]:
        yield self.client
        yield self.auth

    def __getattr__(self, name: str) -> Any:
        return getattr(self.client, name)

    def is_authenticated(self) -> bool:
        try:
            self.client.get_me()
            return True
        except Exception:
            return False


def get_spotify_client(user_id: Optional[str] = None) -> SpotifyClientBundle:
    """Return a Spotify client bundle using session user id by default."""
    uid = user_id or (session.get("user", {}) or {}).get("id") or "demo_user"
    oauth = SpotifyOAuth.from_env()
    client = SpotifyAPI(oauth=oauth, user_id=str(uid))
    return SpotifyClientBundle(client=client, auth=oauth)
