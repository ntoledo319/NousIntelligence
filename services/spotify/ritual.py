from __future__ import annotations

from typing import Any, Dict, Optional

from services.spotify.spotify_api import SpotifyAPI
from services.spotify.spotify_store import SpotifyStore
from services.spotify.spotify_ingest import sync_recently_played
from services.spotify.playlist_engine import PlaylistEngine


def run_spotify_ritual(
    *,
    spotify: SpotifyAPI,
    store: SpotifyStore,
    access_token: str,
    runtime: Dict[str, Any],
    user_id: str,
    target: Optional[str] = None,
    limit: int = 50,
    create_playlist: bool = True,
    playlist_name: Optional[str] = None,
    playlist_public: bool = False,
    enrich: bool = True,
    lyrics: bool = True,
) -> Dict[str, Any]:
    sync = sync_recently_played(
        spotify=spotify,
        store=store,
        access_token=access_token,
        runtime=runtime,
        user_id=user_id,
        limit=50,
        enrich=enrich,
        lyrics=lyrics,
    )

    engine = PlaylistEngine(spotify=spotify, store=store)
    plan = engine.build_plan(runtime=runtime, target=target)
    recs = engine.recommend_tracks(access_token=access_token, plan=plan, limit=limit)

    out: Dict[str, Any] = {
        "ok": True,
        "sync": sync,
        "plan": {
            "target": plan.target,
            "time_bucket": plan.time_bucket,
            "mood_avg": plan.mood_avg,
            "seed_tracks": plan.seed_tracks,
            "tuneables": plan.tuneables,
        },
        "recommendations_count": len(recs),
        "recommendations": [
            {
                "id": tr.get("id"),
                "name": tr.get("name"),
                "artists": [a.get("name") for a in (tr.get("artists") or []) if isinstance(a, dict)],
                "uri": tr.get("uri"),
                "preview_url": tr.get("preview_url"),
            }
            for tr in recs
        ],
    }

    if create_playlist:
        created = engine.create_playlist_from_recs(
            access_token=access_token,
            runtime=runtime,
            recs=recs,
            plan=plan,
            name=playlist_name,
            public=playlist_public,
        )
        out["playlist"] = created.get("playlist")
        out["playlist_track_ids"] = created.get("track_ids")

    return out
