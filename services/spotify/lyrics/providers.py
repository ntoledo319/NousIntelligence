from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from utils.http import http_get_json, HTTPError

logger = logging.getLogger(__name__)


class LyricsProvider:
    name = "base"

    def fetch(self, *, artist: str, title: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class LyricsOvhProvider(LyricsProvider):
    """
    Free, no-key lyrics endpoint.
    Not perfect coverage, but good enough as a default.
    """
    name = "lyrics_ovh"

    def fetch(self, *, artist: str, title: str) -> Optional[Dict[str, Any]]:
        artist = (artist or "").strip()
        title = (title or "").strip()
        if not artist or not title:
            return None
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        try:
            data = http_get_json(url, headers={"User-Agent": "NOUSIntelligence/1.0 (lyrics)"})
        except HTTPError as e:
            logger.info(f"Lyrics.ovh miss for {artist} - {title}: {e}")
            return None
        lyrics = (data.get("lyrics") or "").strip()
        if not lyrics:
            return None
        return {"provider": self.name, "artist": artist, "title": title, "lyrics": lyrics}


@dataclass
class UserProvidedLyricsProvider(LyricsProvider):
    """
    Use lyrics supplied by the user (upload/paste).
    """
    lyrics_text: str
    name: str = "user_provided"

    def fetch(self, *, artist: str, title: str) -> Optional[Dict[str, Any]]:
        lyrics = (self.lyrics_text or "").strip()
        if not lyrics:
            return None
        return {"provider": self.name, "artist": (artist or "").strip(), "title": (title or "").strip(), "lyrics": lyrics}
