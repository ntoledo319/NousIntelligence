from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

class EventStore:
    """SQLite-backed append-only event log."""
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_topic ON events(topic)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
            conn.commit()

    def append(self, topic: str, payload: Dict[str, Any]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO events(ts, topic, payload) VALUES (?, ?, ?)",
                (time.time(), topic, json.dumps(payload, ensure_ascii=False)),
            )
            conn.commit()
            return int(cur.lastrowid)

    def recent(self, limit: int = 100, topic_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        q = "SELECT id, ts, topic, payload FROM events"
        args = []
        if topic_prefix:
            q += " WHERE topic LIKE ?"
            args.append(topic_prefix + "%")
        q += " ORDER BY ts DESC LIMIT ?"
        args.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(q, args).fetchall()

        out: List[Dict[str, Any]] = []
        for eid, ts, topic, payload in rows:
            out.append({"id": eid, "ts": ts, "topic": topic, "payload": json.loads(payload)})
        return out

