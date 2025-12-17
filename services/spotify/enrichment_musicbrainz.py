from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from utils.http import http_get_json, HTTPError

logger = logging.getLogger(__name__)

MB_RECORDING_SEARCH = "https://musicbrainz.org/ws/2/recording/"

USER_AGENT = "NOUSIntelligence/1.0 (spotify-enrichment; https://github.com/ntoledo319)"


def enrich_recording_by_isrc(isrc: str) -> Optional[Dict[str, Any]]:
    """
    Given an ISRC, fetch MusicBrainz recording information.
    No API key required, but MusicBrainz requires a User-Agent.

    Returns a compact dict suitable for caching + ingestion.
    """
    isrc = (isrc or "").strip()
    if not isrc:
        return None

    try:
        data = http_get_json(
            MB_RECORDING_SEARCH,
            params={"query": f"isrc:{isrc}", "fmt": "json"},
            headers={"User-Agent": USER_AGENT},
        )
    except HTTPError as e:
        logger.warning(f"MusicBrainz ISRC lookup failed for {isrc}: {e}")
        return None

    recs = data.get("recordings") or []
    if not recs:
        return None

    # Best-effort: choose highest score if present
    recs_sorted = sorted(recs, key=lambda r: float(r.get("score") or 0.0), reverse=True)
    rec = recs_sorted[0]

    out: Dict[str, Any] = {
        "source": "musicbrainz",
        "isrc": isrc,
        "recording_id": rec.get("id"),
        "title": rec.get("title"),
        "length": rec.get("length"),
        "video": rec.get("video"),
        "artist_credit": rec.get("artist-credit"),
        "first_release_date": rec.get("first-release-date"),
        "releases": rec.get("releases"),
        "tags": rec.get("tags"),
    }
    return out
