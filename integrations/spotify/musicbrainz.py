from __future__ import annotations

import time
from typing import Any, Dict, Optional

import requests


MB_BASE = "https://musicbrainz.org/ws/2"


def _headers() -> Dict[str, str]:
    return {
        "User-Agent": "NOUSIntelligence/spotify-enrichment (contact: you@example.com)",
        "Accept": "application/json",
    }


def lookup_isrc(isrc: str, timeout_s: int = 10) -> Optional[Dict[str, Any]]:
    if not isrc:
        return None
    url = f"{MB_BASE}/isrc/{isrc}"
    params = {"fmt": "json", "inc": "recordings+artists+releases+tags"}
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=timeout_s)
    except Exception:
        return None
    if r.status_code == 404:
        return None
    if r.status_code < 200 or r.status_code >= 300:
        return None
    try:
        return r.json()
    except Exception:
        return None


def search_recording(artist: str, title: str, timeout_s: int = 10) -> Optional[Dict[str, Any]]:
    if not artist or not title:
        return None
    q = f'artist:"{artist}" AND recording:"{title}"'
    url = f"{MB_BASE}/recording"
    params = {"fmt": "json", "query": q, "limit": 5}
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=timeout_s)
    except Exception:
        return None
    if r.status_code < 200 or r.status_code >= 300:
        return None
    try:
        return r.json()
    except Exception:
        return None


def now_ts() -> float:
    return time.time()
