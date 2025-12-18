from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class LyricsResult:
    provider: str
    track_name: str
    artist_name: str
    album_name: Optional[str] = None
    duration_ms: Optional[int] = None
    is_instrumental: bool = False
    plain_lyrics: Optional[str] = None
    synced_lyrics: Optional[str] = None
    lrclib_id: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


class LRCLibProvider:
    """Fetch lyrics from LRCLIB (no API key)."""

    BASE_URL = "https://lrclib.net/api/get"

    def __init__(self, timeout_s: int = 10):
        self.timeout_s = int(timeout_s)

    def fetch(
        self,
        *,
        track_name: str,
        artist_name: str,
        album_name: Optional[str] = None,
        duration_ms: Optional[int] = None,
        lrclib_id: Optional[int] = None,
    ) -> Optional[LyricsResult]:
        params: Dict[str, Any] = {}
        if lrclib_id is not None:
            params["id"] = int(lrclib_id)
        else:
            if not track_name or not artist_name:
                return None
            params["track_name"] = track_name
            params["artist_name"] = artist_name
            if album_name:
                params["album_name"] = album_name
            if duration_ms is not None:
                params["duration"] = int(duration_ms)

        headers = {
            "User-Agent": "NOUSIntelligence/spotify-lyrics (contact: you@example.com)",
            "Accept": "application/json",
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=self.timeout_s)
        except Exception:
            return None

        if resp.status_code == 404:
            return None
        if resp.status_code < 200 or resp.status_code >= 300:
            return None

        try:
            data = resp.json()
        except Exception:
            return None

        plain = data.get("plainLyrics") or data.get("plain_lyrics")
        synced = data.get("syncedLyrics") or data.get("synced_lyrics")
        instrumental = bool(data.get("instrumental") or data.get("isInstrumental") or False)

        return LyricsResult(
            provider="lrclib",
            track_name=str(data.get("trackName") or track_name),
            artist_name=str(data.get("artistName") or artist_name),
            album_name=data.get("albumName") or album_name,
            duration_ms=(int(data.get("duration")) if data.get("duration") is not None else duration_ms),
            is_instrumental=instrumental,
            plain_lyrics=plain,
            synced_lyrics=synced,
            lrclib_id=(int(data.get("id")) if data.get("id") is not None else lrclib_id),
            raw=data,
        )
