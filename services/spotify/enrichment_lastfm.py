from __future__ import annotations

import logging
from typing import Any, Dict, List

from utils.http import http_get_json, HTTPError

logger = logging.getLogger(__name__)

LASTFM_API = "https://ws.audioscrobbler.com/2.0/"


def get_track_top_tags(*, artist: str, track: str, api_key: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch crowd tags for a track from Last.fm.
    Requires LASTFM_API_KEY. If missing, return [].

    Returns: [{"name": "...", "count": N}] (best-effort).
    """
    if not api_key:
        return []
    artist = (artist or "").strip()
    track = (track or "").strip()
    if not artist or not track:
        return []
    try:
        data = http_get_json(
            LASTFM_API,
            params={
                "method": "track.gettoptags",
                "artist": artist,
                "track": track,
                "api_key": api_key,
                "format": "json",
            },
            headers={"User-Agent": "NOUSIntelligence/1.0 (spotify-enrichment)"},
        )
    except HTTPError as e:
        logger.warning(f"Last.fm tags failed for {artist} - {track}: {e}")
        return []
    tags = ((data.get("toptags") or {}).get("tag")) or []
    out = []
    for t in tags[: max(0, int(limit))]:
        name = t.get("name")
        if name:
            try:
                cnt = int(float(t.get("count") or 0))
            except Exception:
                cnt = 0
            out.append({"name": name, "count": cnt})
    return out
