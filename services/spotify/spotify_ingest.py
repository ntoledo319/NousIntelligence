from __future__ import annotations

import os
import time
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from services.spotify.spotify_api import SpotifyAPI
from services.spotify.spotify_store import SpotifyStore
from services.spotify.enrichment_musicbrainz import enrich_recording_by_isrc
from services.spotify.enrichment_lastfm import get_track_top_tags
from services.spotify.lyrics.providers import LyricsOvhProvider, UserProvidedLyricsProvider
from services.spotify.lyrics.analyzer import analyze_lyrics

logger = logging.getLogger(__name__)


def _batched(items: Sequence[str], n: int) -> Iterable[List[str]]:
    buf: List[str] = []
    for x in items:
        if not x:
            continue
        buf.append(x)
        if len(buf) >= n:
            yield buf
            buf = []
    if buf:
        yield buf


def _track_blob(track: Dict[str, Any], *, features: Optional[Dict[str, Any]], mb: Optional[Dict[str, Any]], tags: List[Dict[str, Any]], lyrics_features: Optional[Dict[str, Any]]) -> str:
    artists = ", ".join([a.get("name","") for a in (track.get("artists") or []) if a.get("name")])
    album = (track.get("album") or {}).get("name") or ""
    release = (track.get("album") or {}).get("release_date") or ""
    isrc = ((track.get("external_ids") or {}).get("isrc")) or ""
    lines = []
    lines.append(f"Track: {track.get('name','')}")
    if artists:
        lines.append(f"Artist(s): {artists}")
    if album:
        lines.append(f"Album: {album} ({release})")
    if isrc:
        lines.append(f"ISRC: {isrc}")
    if track.get("explicit") is not None:
        lines.append(f"Explicit: {bool(track.get('explicit'))}")
    if track.get("popularity") is not None:
        lines.append(f"Popularity: {track.get('popularity')}")
    if features:
        # keep only stable + meaningful fields
        keep = ["danceability","energy","valence","tempo","acousticness","instrumentalness","liveness","speechiness"]
        feat_bits = []
        for k in keep:
            v = features.get(k)
            if v is None:
                continue
            feat_bits.append(f"{k}={v}")
        if feat_bits:
            lines.append("AudioFeatures: " + ", ".join(feat_bits))
    if tags:
        lines.append("CrowdTags: " + ", ".join([t["name"] for t in tags if t.get("name")][:15]))
    if mb:
        rid = mb.get("recording_id") or ""
        if rid:
            lines.append(f"MusicBrainzRecording: {rid}")
        ac = mb.get("artist_credit") or []
        ac_names = []
        for a in ac:
            if isinstance(a, dict):
                nm = (a.get("artist") or {}).get("name") or a.get("name")
                if nm:
                    ac_names.append(nm)
        if ac_names:
            lines.append("MusicBrainzArtists: " + ", ".join(ac_names[:10]))
    if lyrics_features and lyrics_features.get("has_lyrics"):
        lines.append(f"LyricsSentiment: {lyrics_features.get('sentiment')}")
        themes = lyrics_features.get("themes") or []
        if themes:
            lines.append("LyricsThemes: " + ", ".join([t.get("theme","") for t in themes if t.get("theme")]))
        kws = lyrics_features.get("top_keywords") or []
        if kws:
            lines.append("LyricsKeywords: " + ", ".join([k.get("word","") for k in kws if k.get("word")][:12]))
        ex = lyrics_features.get("excerpt") or ""
        if ex:
            lines.append("LyricsExcerpt: " + ex)
    return "\n".join([l for l in lines if l.strip()])


def sync_recently_played(
    *,
    rt: Dict[str, Any],
    spotify: SpotifyAPI,
    store: SpotifyStore,
    user_id: str,
    limit: int = 50,
    enrich: bool = True,
    include_audio_features: bool = True,
    include_lyrics: bool = True,
    allow_store_full_lyrics: bool = False,
    user_provided_lyrics: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Pull recently played tracks and ingest into:
      - EventBus (spotify.track.played)
      - SemanticIndex (spotify:track:<id>)
      - MemoryGraph (track->artist, track->tags, etc)

    user_provided_lyrics: optional {track_id: "lyrics text"} to avoid external fetching.
    """
    sem = rt["semantic"]
    graph = rt["graph"]
    bus = rt["bus"]

    rec = spotify.recently_played(limit=limit)
    items = rec.get("items") or []

    # Collect track IDs
    track_ids: List[str] = []
    track_by_id: Dict[str, Dict[str, Any]] = {}
    played_ctx: List[Dict[str, Any]] = []

    for it in items:
        tr = it.get("track") or {}
        tid = tr.get("id")
        if not tid:
            continue
        track_ids.append(tid)
        track_by_id[tid] = tr
        played_at = it.get("played_at")
        played_ctx.append({"track_id": tid, "played_at": played_at, "context": it.get("context")})

    # Audio features in batches
    features_by_id: Dict[str, Dict[str, Any]] = {}
    if include_audio_features and track_ids:
        for batch in _batched(track_ids, 100):
            try:
                feats = spotify.audio_features(batch)
            except Exception as e:
                logger.warning(f"audio_features batch failed: {e}")
                continue
            for f in (feats.get("audio_features") or []):
                if not f:
                    continue
                tid = f.get("id")
                if tid:
                    features_by_id[tid] = f

    lastfm_key = os.environ.get("LASTFM_API_KEY", "").strip()

    ingested = 0
    enriched = 0
    lyrics_done = 0

    for tid in track_ids:
        tr = track_by_id.get(tid) or {}
        store.put_track(tid, tr)

        # Enrichment: MusicBrainz via ISRC
        mb = None
        tags: List[Dict[str, Any]] = []
        isrc = ((tr.get("external_ids") or {}).get("isrc")) or ""
        if enrich and isrc:
            cached = store.get_enrichment(tid, "musicbrainz")
            if cached:
                mb = cached
            else:
                mb = enrich_recording_by_isrc(isrc)
                if mb:
                    store.put_enrichment(tid, "musicbrainz", mb)
                    enriched += 1

        # Enrichment: Last.fm tags
        if enrich and lastfm_key:
            cached_tags = store.get_enrichment(tid, "lastfm_tags")
            if cached_tags and isinstance(cached_tags.get("tags"), list):
                tags = cached_tags["tags"]
            else:
                artists = tr.get("artists") or []
                artist0 = (artists[0].get("name") if artists else "") or ""
                title = tr.get("name") or ""
                tags = get_track_top_tags(artist=artist0, track=title, api_key=lastfm_key, limit=12)
                store.put_enrichment(tid, "lastfm_tags", {"tags": tags})
                if tags:
                    enriched += 1

        # Lyrics
        lyrics_features = None
        if include_lyrics:
            cached_ly = store.get_lyrics_analysis(tid)
            if cached_ly:
                lyrics_features = cached_ly.get("analysis")
            else:
                artists = tr.get("artists") or []
                artist0 = (artists[0].get("name") if artists else "") or ""
                title = tr.get("name") or ""
                lp = None

                # Prefer user-provided lyrics if supplied
                if user_provided_lyrics and user_provided_lyrics.get(tid):
                    lp = UserProvidedLyricsProvider(user_provided_lyrics[tid])
                    fetched = lp.fetch(artist=artist0, title=title)
                else:
                    fetched = LyricsOvhProvider().fetch(artist=artist0, title=title)

                if fetched and fetched.get("lyrics"):
                    analysis = analyze_lyrics(fetched["lyrics"])
                    lyrics_features = analysis
                    payload = {"provider": fetched.get("provider"), "analysis": analysis}
                    if allow_store_full_lyrics:
                        payload["lyrics"] = fetched["lyrics"]
                    store.put_lyrics_analysis(tid, payload)
                    lyrics_done += 1

        feat = features_by_id.get(tid)
        blob = _track_blob(tr, features=feat, mb=mb, tags=tags, lyrics_features=lyrics_features)

        # Semantic doc
        doc_id = f"spotify:track:{tid}"
        meta = {
            "source": "spotify",
            "kind": "track",
            "spotify_id": tid,
            "name": tr.get("name"),
            "artists": [a.get("name") for a in (tr.get("artists") or []) if a.get("name")],
            "album": (tr.get("album") or {}).get("name"),
            "release_date": (tr.get("album") or {}).get("release_date"),
            "isrc": isrc,
            "ingested_ts": time.time(),
            "user_id": user_id,
        }
        sem.upsert(doc_id, blob, meta)

        # Graph nodes + edges (doc node already ok)
        graph.upsert_node(doc_id, kind="doc", meta=meta)

        # Track -> artist edges
        for a in (tr.get("artists") or []):
            aid = a.get("id")
            an = a.get("name")
            if not aid and not an:
                continue
            artist_node = f"spotify:artist:{aid or an}"
            graph.upsert_node(artist_node, kind="artist", meta={"source": "spotify", "spotify_id": aid, "name": an})
            graph.add_edge(doc_id, artist_node, rel="by", weight=1.0)

        # Track -> crowd tags
        for t in tags[:20]:
            nm = t.get("name")
            if not nm:
                continue
            tag_node = f"tag:{nm.lower().strip()}"
            graph.upsert_node(tag_node, kind="tag", meta={"name": nm, "source": "lastfm"})
            graph.add_edge(doc_id, tag_node, rel="tagged", weight=float(t.get("count") or 1))

        # MusicBrainz link
        if mb and mb.get("recording_id"):
            mb_node = f"musicbrainz:recording:{mb['recording_id']}"
            graph.upsert_node(mb_node, kind="recording", meta={"source": "musicbrainz", "isrc": isrc, "title": mb.get("title")})
            graph.add_edge(doc_id, mb_node, rel="maps_to", weight=1.0)

        # Publish play events
        for p in played_ctx:
            if p.get("track_id") != tid:
                continue
            bus.publish("spotify.track.played", {"user_id": user_id, "track_id": tid, "played_at": p.get("played_at")})
            break

        ingested += 1

    return {
        "ok": True,
        "user_id": user_id,
        "fetched": len(items),
        "unique_tracks": len(track_ids),
        "ingested": ingested,
        "enriched": enriched,
        "lyrics_analyzed": lyrics_done,
    }
