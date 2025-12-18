from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional


class SpotifyStore:
    """SQLite store for Spotify auth + caches.

    Tables:
      - tokens: OAuth tokens per user
      - track_cache: raw Spotify track objects
      - enrichment_cache: (track_id, source) -> payload
      - lyrics_cache: lyrics analysis (optionally full lyrics if you insist)

    Designed to work on Render/Fly/local with zero external services.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tokens (
                    user_id TEXT PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    expires_at REAL NOT NULL,
                    scope TEXT,
                    token_type TEXT,
                    created_ts REAL NOT NULL,
                    updated_ts REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS track_cache (
                    track_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_ts REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS enrichment_cache (
                    track_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_ts REAL NOT NULL,
                    PRIMARY KEY (track_id, source)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS lyrics_cache (
                    track_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_ts REAL NOT NULL
                )
                """
            )
            conn.commit()

    # ── Tokens ─────────────────────────────────────────────────────────

    def get_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT access_token, refresh_token, expires_at, scope, token_type FROM tokens WHERE user_id=?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        access_token, refresh_token, expires_at, scope, token_type = row
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": float(expires_at),
            "scope": scope,
            "token_type": token_type or "Bearer",
        }

    def save_tokens(self, user_id: str, token: Dict[str, Any]) -> None:
        now = time.time()
        expires_at = float(token.get("expires_at") or 0.0)
        if not expires_at and token.get("expires_in") is not None:
            expires_at = now + float(token["expires_in"])
        access_token = str(token["access_token"])
        refresh_token = token.get("refresh_token")
        scope = token.get("scope")
        token_type = token.get("token_type") or "Bearer"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tokens(user_id,access_token,refresh_token,expires_at,scope,token_type,created_ts,updated_ts)
                VALUES(?,?,?,?,?,?, COALESCE((SELECT created_ts FROM tokens WHERE user_id=?), ?), ?)
                """,
                (user_id, access_token, refresh_token, expires_at, scope, token_type, user_id, now, now),
            )
            conn.commit()

    def delete_tokens(self, user_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tokens WHERE user_id=?", (user_id,))
            conn.commit()

    # ── Track cache ────────────────────────────────────────────────────

    def get_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT payload FROM track_cache WHERE track_id=?", (track_id,)).fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return None

    def put_track(self, track_id: str, payload: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO track_cache(track_id,payload,updated_ts) VALUES(?,?,?)",
                (track_id, json.dumps(payload, ensure_ascii=False), time.time()),
            )
            conn.commit()

    # ── Enrichment cache ───────────────────────────────────────────────

    def get_enrichment(self, track_id: str, source: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM enrichment_cache WHERE track_id=? AND source=?",
                (track_id, source),
            ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return None

    def put_enrichment(self, track_id: str, source: str, payload: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO enrichment_cache(track_id,source,payload,updated_ts) VALUES(?,?,?,?)",
                (track_id, source, json.dumps(payload, ensure_ascii=False), time.time()),
            )
            conn.commit()

    # ── Lyrics cache ───────────────────────────────────────────────────

    def get_lyrics_analysis(self, track_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT payload FROM lyrics_cache WHERE track_id=?", (track_id,)).fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return None

    def put_lyrics_analysis(self, track_id: str, payload: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO lyrics_cache(track_id,payload,updated_ts) VALUES(?,?,?)",
                (track_id, json.dumps(payload, ensure_ascii=False), time.time()),
            )
            conn.commit()
