from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from services.spotify.spotify_api import SpotifyAPI
from services.spotify.spotify_store import SpotifyStore
from services.spotify.lyrics import default_providers, analyze_lyrics


def _track_id(track_obj: Dict[str, Any]) -> Optional[str]:
    if not isinstance(track_obj, dict):
        return None
    tid = track_obj.get("id")
    if tid:
        return str(tid)
    uri = str(track_obj.get("uri") or "")
    if uri.startswith("spotify:track:"):
        return uri.split(":")[-1]
    return None


def _artist_title(track_obj: Dict[str, Any]) -> Tuple[str, str]:
    artist = ""
    title = str(track_obj.get("name") or "")
    artists = track_obj.get("artists") or []
    if artists and isinstance(artists, list) and isinstance(artists[0], dict):
        artist = str(artists[0].get("name") or "")
    return artist, title


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def sync_recently_played(
    *,
    spotify: SpotifyAPI,
    store: SpotifyStore,
    access_token: str,
    runtime: Optional[Dict[str, Any]] = None,
    user_id: str = "demo_user",
    limit: int = 50,
    enrich: bool = True,
    lyrics: bool = True,
) -> Dict[str, Any]:
    items = spotify.recently_played(access_token, limit=limit)
    tracks: List[Dict[str, Any]] = []
    for it in items:
        tr = it.get("track") if isinstance(it, dict) else None
        if isinstance(tr, dict):
            tracks.append(tr)

    cached = 0
    track_ids: List[str] = []
    for tr in tracks:
        tid = _track_id(tr)
        if not tid:
            continue
        track_ids.append(tid)
        store.put_track(tid, tr)
        cached += 1

    if enrich and track_ids:
        feats = []
        for i in range(0, len(track_ids), 100):
            feats.extend(spotify.audio_features(access_token, track_ids[i : i + 100]))
        for f in feats:
            tid = str(f.get("id") or "")
            if tid:
                store.put_enrichment(tid, "audio_features", f)

    lyr_analyzed = 0
    if lyrics:
        providers = default_providers()
        for tid in track_ids[: min(len(track_ids), 50)]:
            if store.get_lyrics_analysis(tid):
                continue
            tr = store.get_track(tid) or {}
            artist, title = _artist_title(tr)
            if not artist or not title:
                continue
            lyr_text = None
            used = None
            for prov in providers:
                res = prov.fetch(artist, title)
                if res and res.lyrics:
                    lyr_text = res.lyrics
                    used = res.provider
                    break
            if not lyr_text:
                continue
            analysis = analyze_lyrics(lyr_text)
            payload = {
                "track_id": tid,
                "artist": artist,
                "title": title,
                "provider": used,
                "analysis": analysis,
                "stored_raw_lyrics": False,
                "created_at": _now_iso(),
            }
            store.put_lyrics_analysis(tid, payload)
            lyr_analyzed += 1

    events = 0
    sem = 0
    graph_edges = 0
    if runtime:
        bus = runtime.get("bus")
        semantic = runtime.get("semantic")
        graph = runtime.get("graph")

        for tr in tracks:
            tid = _track_id(tr)
            if not tid:
                continue
            artist, title = _artist_title(tr)
            meta = {
                "source": "spotify",
                "kind": "track",
                "track_id": tid,
                "artist": artist,
                "title": title,
                "user_id": user_id,
                "ts": _now_iso(),
            }
            text = f"Spotify track played: {title} — {artist}"
            if semantic:
                try:
                    semantic.upsert(f"spotify:track:{tid}", text, meta)
                    sem += 1
                except Exception:
                    pass
            if graph:
                try:
                    graph.upsert_node(f"spotify:track:{tid}", kind="spotify_track", meta=meta)
                    if artist:
                        graph.upsert_node(f"artist:{artist}", kind="artist", meta={"name": artist})
                        graph_edges += graph.add_edge(f"spotify:track:{tid}", f"artist:{artist}", rel="by")
                except Exception:
                    pass
            if bus:
                try:
                    bus.publish(
                        "spotify.track.played",
                        {"track_id": tid, "artist": artist, "title": title, "user_id": user_id, "ts": meta["ts"]},
                    )
                    events += 1
                except Exception:
                    pass

    return {
        "ok": True,
        "tracks_seen": len(tracks),
        "tracks_cached": cached,
        "audio_features_cached": bool(enrich),
        "lyrics_analyzed": lyr_analyzed,
        "semantic_upserts": sem,
        "events_published": events,
        "graph_edges_added": graph_edges,
    }
