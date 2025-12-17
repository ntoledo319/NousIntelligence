from __future__ import annotations

"""
Spotify Visualizer (Minimal)

The old visualizer file had syntax errors and mixed UI concerns into backend code.
This replacement provides simple "viz-ready" aggregations as JSON.

If you want charts: do it in the frontend. Backend should just return data.
"""

from collections import Counter
from typing import Any, Dict

from services.spotify.spotify_api import SpotifyAPI


def summarize_recently_played(sp: SpotifyAPI, *, limit: int = 50) -> Dict[str, Any]:
    data = sp.recently_played(limit=limit)
    items = data.get("items") or []
    artists = Counter()
    tracks = Counter()
    hours = Counter()

    for it in items:
        tr = it.get("track") or {}
        name = tr.get("name") or ""
        tid = tr.get("id") or ""
        if name:
            tracks[f"{name} ({tid})"] += 1
        for a in (tr.get("artists") or []):
            an = a.get("name")
            if an:
                artists[an] += 1
        played_at = (it.get("played_at") or "")
        # crude hour extraction: YYYY-MM-DDTHH:
        if "T" in played_at:
            hh = played_at.split("T", 1)[1][:2]
            if hh.isdigit():
                hours[int(hh)] += 1

    return {
        "total_events": len(items),
        "top_artists": artists.most_common(15),
        "top_tracks": tracks.most_common(15),
        "plays_by_hour": sorted(hours.items(), key=lambda x: x[0]),
    }
