from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from integrations.spotify import SpotifyAPI, SpotifyAuthRequired, SpotifyOAuth, get_token_store, lookup_isrc, search_recording
from integrations.spotify.lyrics import LRCLibProvider, analyze_lyrics

# Type checking guard to prevent circular imports during runtime
if TYPE_CHECKING:
    from integrations.spotify.token_store import TokenData


class SpotifyService:
    """Unified Spotify service:
    - OAuth flow helpers
    - Spotify API wrapper
    - MusicBrainz enrichment
    - Lyrics ingestion + analysis
    - Writes to SemanticIndex + MemoryGraph (if runtime service exists)
    """

    def __init__(self):
        self.oauth = SpotifyOAuth.from_env()
        self.store = get_token_store()
        self.lyrics_provider = LRCLibProvider()

    def is_configured(self) -> bool:
        return self.oauth.is_configured()

    def get_client(self, user_id: str) -> SpotifyAPI:
        return SpotifyAPI(oauth=self.oauth, user_id=str(user_id))

    def build_auth_url(self, state: str) -> str:
        return self.oauth.build_authorize_url(state=state)

    def exchange_code(self, user_id: str, code: str) -> Dict[str, Any]:
        token = self.oauth.exchange_code(code)
        from integrations.spotify.token_store import TokenData
        td = TokenData.from_mapping(str(user_id), token)
        self.store.save(td)
        return token

    def disconnect(self, user_id: str) -> None:
        self.store.delete(str(user_id))

    def is_authenticated(self, user_id: str) -> bool:
        try:
            self.get_client(user_id).get_me()
            return True
        except Exception:
            return False

    def now_playing(self, user_id: str, enrich: bool = True) -> Dict[str, Any]:
        client = self.get_client(user_id)
        pb = client.get_current_playback()
        if not pb:
            return {"ok": True, "playing": False}
        item = pb.get("item") or {}
        if not enrich or not item.get("id"):
            return {"ok": True, "playing": True, "playback": pb}
        enriched = self.enrich_track(user_id, item["id"], include_lyrics=False)
        return {"ok": True, "playing": True, "playback": pb, "enriched_track": enriched}

    def enrich_track(self, user_id: str, track_id: str, include_lyrics: bool = False) -> Dict[str, Any]:
        client = self.get_client(user_id)
        track = client.get_track(track_id)
        features = None
        try:
            feats = client.get_audio_features([track_id]) or {}
            arr = feats.get("audio_features") or []
            features = arr[0] if arr else None
        except Exception:
            features = None

        isrc = ((track.get("external_ids") or {}).get("isrc") or "").strip()
        mb = None
        if isrc:
            mb = lookup_isrc(isrc) or None
        if mb is None:
            artist = (track.get("artists") or [{}])[0].get("name") or ""
            title = track.get("name") or ""
            mb = search_recording(artist=artist, title=title) or None

        lyrics = None
        if include_lyrics:
            lyrics = self.fetch_lyrics_and_analyze(track)

        return {
            "track": track,
            "audio_features": features,
            "musicbrainz": mb,
            "lyrics": lyrics,
        }

    def fetch_lyrics_and_analyze(self, track_obj: Dict[str, Any]) -> Dict[str, Any]:
        title = track_obj.get("name") or ""
        artists = track_obj.get("artists") or []
        artist = artists[0].get("name") if artists else ""
        album = ((track_obj.get("album") or {}).get("name")) or None
        duration_ms = int(track_obj.get("duration_ms") or 0) or None
        track_id = track_obj.get("id") or None

        res = self.lyrics_provider.fetch(
            track_name=title,
            artist_name=artist,
            album_name=album,
            duration_ms=duration_ms,
        )
        if not res:
            return {"ok": False, "found": False, "provider": "lrclib"}

        raw_lyrics = res.plain_lyrics or ""
        analysis = analyze_lyrics(raw_lyrics) if raw_lyrics else None

        payload = {
            "ok": True,
            "found": True,
            "provider": res.provider,
            "track_id": track_id,
            "title": res.track_name,
            "artist": res.artist_name,
            "album": res.album_name,
            "duration_ms": res.duration_ms,
            "instrumental": res.is_instrumental,
            "analysis": analysis.__dict__ if analysis else None,
        }

        include_full = os.environ.get("LYRICS_INDEX_FULL_TEXT", "false").lower() in {"1", "true", "yes"}
        if include_full:
            payload["plain_lyrics"] = res.plain_lyrics
            payload["synced_lyrics"] = res.synced_lyrics

        self._ingest_lyrics_analysis(track_id=track_id, title=title, artist=artist, lyrics=raw_lyrics, analysis=analysis)
        return payload

    def _ingest_lyrics_analysis(self, track_id: Optional[str], title: str, artist: str, lyrics: str, analysis: Any) -> None:
        if not analysis:
            return
        try:
            from services.runtime_service import init_runtime
            from flask import current_app
            rt = init_runtime(current_app)
            runtime_service = rt.get("runtime")
        except Exception:
            runtime_service = None

        if runtime_service is None:
            return

        themes = analysis.themes
        keywords = analysis.top_keywords
        summary = analysis.summary

        text_parts = [
            f"Lyrics analysis for {title} — {artist}",
            f"Themes: {', '.join(themes) if themes else 'n/a'}",
            f"Top keywords: {', '.join(keywords[:20]) if keywords else 'n/a'}",
            f"Summary: {summary}",
        ]

        include_full = os.environ.get("LYRICS_INDEX_FULL_TEXT", "false").lower() in {"1", "true", "yes"}
        if include_full and lyrics:
            text_parts.append("\nLyrics (full text):\n" + lyrics)

        doc_text = "\n".join(text_parts)
        doc_id = f"lyrics:{track_id}" if track_id else f"lyrics:{title}:{artist}"

        try:
            runtime_service.semantic_index.upsert_document(
                doc_id=doc_id,
                content=doc_text,
                metadata={
                    "type": "lyrics_analysis",
                    "source": "lrclib",
                    "track_id": track_id,
                    "title": title,
                    "artist": artist,
                    "themes": themes,
                    "keywords": keywords[:50],
                },
            )
        except Exception:
            pass

        try:
            runtime_service.memory_graph.add_memory(
                content=summary,
                memory_type="lyrics_analysis",
                metadata={
                    "track_id": track_id,
                    "title": title,
                    "artist": artist,
                    "themes": themes,
                    "keywords": keywords[:20],
                },
            )
        except Exception:
            pass

    def sync_recently_played(self, user_id: str, limit: int = 25) -> Dict[str, Any]:
        client = self.get_client(user_id)
        data = client.get_recently_played(limit=limit)
        items = data.get("items") or []

        ingested: List[Dict[str, Any]] = []
        for it in items:
            track = (it.get("track") or {})
            tid = track.get("id")
            if not tid:
                continue
            enriched = self.enrich_track(user_id, tid, include_lyrics=False)
            self._ingest_track_summary(track, enriched)
            ingested.append({"track_id": tid, "name": track.get("name"), "artists": [a.get("name") for a in track.get("artists") or []]})

        return {"ok": True, "count": len(ingested), "items": ingested}

    def _ingest_track_summary(self, track: Dict[str, Any], enriched: Dict[str, Any]) -> None:
        try:
            from services.runtime_service import init_runtime
            from flask import current_app
            rt = init_runtime(current_app)
            runtime_service = rt.get("runtime")
        except Exception:
            runtime_service = None
        if runtime_service is None:
            return

        tid = track.get("id") or ""
        title = track.get("name") or ""
        artist = ((track.get("artists") or [{}])[0].get("name")) or ""
        feats = enriched.get("audio_features") or {}
        mb = enriched.get("musicbrainz")

        text = f"Track: {title} — {artist}\n"
        if feats:
            text += f"AudioFeatures: danceability={feats.get('danceability')} energy={feats.get('energy')} valence={feats.get('valence')} tempo={feats.get('tempo')}\n"
        if mb:
            text += "MusicBrainz enrichment present.\n"

        doc_id = f"track:{tid}" if tid else f"track:{title}:{artist}"
        try:
            runtime_service.semantic_index.upsert_document(
                doc_id=doc_id,
                content=text,
                metadata={
                    "type": "spotify_track",
                    "track_id": tid,
                    "title": title,
                    "artist": artist,
                    "spotify": {"id": tid},
                    "audio_features": feats,
                },
            )
        except Exception:
            pass

        try:
            runtime_service.memory_graph.add_memory(
                content=text.strip(),
                memory_type="spotify_track",
                metadata={"track_id": tid, "title": title, "artist": artist},
            )
        except Exception:
            pass


spotify_service = SpotifyService()
