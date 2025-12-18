from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from services.spotify.spotify_api import SpotifyAPI
from services.spotify.spotify_store import SpotifyStore


def _utcnow_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _time_bucket(ts: Optional[float] = None) -> str:
    dt = datetime.utcfromtimestamp(ts or time.time())
    h = dt.hour
    if 5 <= h <= 10:
        return "morning"
    if 11 <= h <= 16:
        return "day"
    if 17 <= h <= 21:
        return "evening"
    return "night"


TARGETS = ("uplift", "calm", "focus", "sleep", "reflect")


def _default_target(mood_avg: Optional[float], bucket: str) -> str:
    if mood_avg is None:
        return {"morning": "focus", "day": "focus", "evening": "calm", "night": "sleep"}.get(bucket, "focus")
    if mood_avg <= 3.5:
        return "uplift"
    if mood_avg <= 6.0:
        return {"morning": "focus", "day": "focus", "evening": "calm", "night": "sleep"}.get(bucket, "calm")
    if mood_avg <= 8.5:
        return "reflect"
    return "uplift"


def tuneables_for(target: str) -> Dict[str, Any]:
    t = (target or "").strip().lower()
    if t == "uplift":
        return {
            "min_valence": 0.60,
            "min_energy": 0.55,
            "target_danceability": 0.65,
            "max_speechiness": 0.18,
        }
    if t == "calm":
        return {
            "max_energy": 0.45,
            "target_valence": 0.55,
            "target_acousticness": 0.55,
            "max_tempo": 120,
        }
    if t == "focus":
        return {
            "target_energy": 0.58,
            "target_instrumentalness": 0.35,
            "max_speechiness": 0.12,
            "min_valence": 0.35,
        }
    if t == "sleep":
        return {
            "max_energy": 0.35,
            "target_acousticness": 0.70,
            "max_tempo": 110,
            "max_liveness": 0.35,
        }
    return {
        "max_energy": 0.55,
        "target_acousticness": 0.55,
        "target_valence": 0.45,
        "max_speechiness": 0.18,
    }


THEME_ALLOWLIST: Dict[str, List[str]] = {
    "uplift": ["hope", "resilience", "party", "love", "nature"],
    "calm": ["nature", "love", "hope"],
    "focus": ["resilience", "hope", "nature"],
    "sleep": ["nature", "love"],
    "reflect": ["love", "grief", "loneliness", "hope", "nature", "resilience"],
}

THEME_BLOCKLIST: Dict[str, List[str]] = {
    "uplift": ["grief", "anxiety", "anger"],
    "calm": ["anger", "party", "sex"],
    "focus": ["party", "sex", "anger"],
    "sleep": ["party", "anger", "sex"],
    "reflect": ["sex"],
}


def _get_track_themes(store: SpotifyStore, track_id: str) -> List[str]:
    a = store.get_lyrics_analysis(track_id) or {}
    analysis = (a.get("analysis") or {}) if isinstance(a, dict) else {}
    themes = analysis.get("themes") or []
    out: List[str] = []
    if isinstance(themes, list):
        for t in themes:
            if isinstance(t, str) and t.strip():
                out.append(t.strip().lower())
    return out


def _pick_seed_tracks(store: SpotifyStore, recent_track_ids: List[str], *, target: str, max_seeds: int = 5) -> List[str]:
    allow = set(THEME_ALLOWLIST.get(target, []))
    block = set(THEME_BLOCKLIST.get(target, []))

    scored: List[Tuple[int, str]] = []
    for tid in recent_track_ids:
        themes = _get_track_themes(store, tid)
        if themes:
            if any(t in block for t in themes):
                continue
            score = sum(1 for t in themes if t in allow)
            scored.append((score, tid))
        else:
            scored.append((0, tid))

    scored.sort(key=lambda x: x[0], reverse=True)
    seeds = [tid for _, tid in scored[: max_seeds * 2]]
    random.shuffle(seeds)
    return seeds[:max_seeds] if seeds else []


def _spotify_track_uri(track_id: str) -> str:
    return f"spotify:track:{track_id}"


@dataclass
class PlaylistPlan:
    target: str
    time_bucket: str
    mood_avg: Optional[float]
    seed_tracks: List[str]
    tuneables: Dict[str, Any]


class PlaylistEngine:
    def __init__(self, *, spotify: SpotifyAPI, store: SpotifyStore) -> None:
        self.spotify = spotify
        self.store = store

    def build_plan(self, *, runtime: Dict[str, Any], target: Optional[str] = None) -> PlaylistPlan:
        bucket = _time_bucket()

        mood_avg: Optional[float] = None
        ev_store = runtime.get("store")
        if ev_store:
            try:
                moods = ev_store.recent(limit=50, topic_prefix="mood.logged")
                vals: List[float] = []
                for e in moods:
                    payload = e.get("payload") or {}
                    v = payload.get("mood")
                    try:
                        v = float(v)
                    except Exception:
                        continue
                    if 1.0 <= v <= 10.0:
                        vals.append(v)
                if vals:
                    mood_avg = sum(vals) / len(vals)
            except Exception:
                mood_avg = None

        t = (target or "").strip().lower()
        if t not in TARGETS:
            t = _default_target(mood_avg, bucket)

        recent_ids: List[str] = []
        if ev_store:
            try:
                plays = ev_store.recent(limit=200, topic_prefix="spotify.track.played")
                for e in plays:
                    tid = (e.get("payload") or {}).get("track_id")
                    if tid and tid not in recent_ids:
                        recent_ids.append(str(tid))
            except Exception:
                pass

        seeds = _pick_seed_tracks(self.store, recent_ids, target=t)
        tune = tuneables_for(t)
        return PlaylistPlan(target=t, time_bucket=bucket, mood_avg=mood_avg, seed_tracks=seeds, tuneables=tune)

    def recommend_tracks(self, *, access_token: str, plan: PlaylistPlan, limit: int = 50) -> List[Dict[str, Any]]:
        seed_tracks = plan.seed_tracks
        if not seed_tracks:
            top = self.spotify.top_tracks(access_token, limit=10, time_range="short_term")
            seed_tracks = []
            for tr in top:
                tid = str(tr.get("id") or "")
                if tid:
                    seed_tracks.append(tid)
                    self.store.put_track(tid, tr)
            seed_tracks = seed_tracks[:5]

        recs = self.spotify.recommendations(
            access_token,
            seed_tracks=seed_tracks[:5],
            limit=int(limit),
            tuneables=plan.tuneables,
        )

        for tr in recs:
            tid = str(tr.get("id") or "")
            if tid:
                self.store.put_track(tid, tr)

        return recs

    def create_playlist_from_recs(
        self,
        *,
        access_token: str,
        runtime: Dict[str, Any],
        recs: List[Dict[str, Any]],
        plan: PlaylistPlan,
        name: Optional[str] = None,
        public: bool = False,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        me = self.spotify.me(access_token)
        uid = str(me.get("id") or "")
        if not uid:
            raise RuntimeError("Spotify /me did not return user id")

        playlist_name = name or f"NOUS Ritual: {plan.target.title()} ({plan.time_bucket})"
        desc = description or f"Generated by NOUS on {_utcnow_iso()}. Target={plan.target}. MoodAvg={plan.mood_avg}."
        pl = self.spotify.create_playlist(access_token, user_id=uid, name=playlist_name, description=desc, public=public)
        pl_id = str(pl.get("id") or "")
        if not pl_id:
            raise RuntimeError("Spotify create playlist failed (no id returned)")

        uris: List[str] = []
        track_ids: List[str] = []
        for tr in recs:
            tid = str(tr.get("id") or "")
            if not tid:
                continue
            track_ids.append(tid)
            uris.append(_spotify_track_uri(tid))

        if uris:
            self.spotify.add_tracks_to_playlist(access_token, playlist_id=pl_id, track_uris=uris)

        semantic = runtime.get("semantic")
        graph = runtime.get("graph")
        bus = runtime.get("bus")

        meta = {
            "source": "spotify",
            "kind": "playlist",
            "playlist_id": pl_id,
            "name": playlist_name,
            "target": plan.target,
            "time_bucket": plan.time_bucket,
            "mood_avg": plan.mood_avg,
            "created_at": _utcnow_iso(),
            "track_count": len(track_ids),
        }
        text = f"Spotify playlist created: {playlist_name} (target={plan.target}, bucket={plan.time_bucket})"

        if semantic:
            try:
                semantic.upsert(f"spotify:playlist:{pl_id}", text, meta)
            except Exception:
                pass

        if graph:
            try:
                graph.upsert_node(f"spotify:playlist:{pl_id}", kind="spotify_playlist", meta=meta)
                for tid in track_ids[:200]:
                    graph.upsert_node(f"spotify:track:{tid}", kind="spotify_track", meta={"track_id": tid})
                    graph.add_edge(f"spotify:playlist:{pl_id}", f"spotify:track:{tid}", rel="contains")
            except Exception:
                pass

        if bus:
            try:
                bus.publish("spotify.playlist.created", meta)
            except Exception:
                pass

        return {
            "ok": True,
            "playlist": pl,
            "track_ids": track_ids,
            "plan": {
                "target": plan.target,
                "time_bucket": plan.time_bucket,
                "mood_avg": plan.mood_avg,
                "seed_tracks": plan.seed_tracks,
                "tuneables": plan.tuneables,
            },
        }
