from __future__ import annotations
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ENTITY_PAT = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b")

@dataclass
class Edge:
    src: str
    dst: str
    rel: str
    weight: float = 1.0


class MemoryGraph:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
              CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                meta TEXT NOT NULL,
                created_ts REAL NOT NULL
              )
            """)
            conn.execute("""
              CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src TEXT NOT NULL,
                dst TEXT NOT NULL,
                rel TEXT NOT NULL,
                weight REAL NOT NULL,
                created_ts REAL NOT NULL
              )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel)")
            conn.commit()

    def upsert_node(self, node_id: str, kind: str = "entity", meta: Optional[Dict[str, Any]] = None) -> None:
        meta = meta or {}
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO nodes(id,kind,meta,created_ts) VALUES(?,?,?,?)",
                (node_id, kind, json.dumps(meta, ensure_ascii=False), time.time()),
            )
            conn.commit()

    def add_edge(self, src: str, dst: str, rel: str = "mentions", weight: float = 1.0) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO edges(src,dst,rel,weight,created_ts) VALUES(?,?,?,?,?)",
                (src, dst, rel, float(weight), time.time()),
            )
            conn.commit()
            return int(cur.lastrowid)

    def extract_entities(self, text: str) -> List[str]:
        # naive but deterministic; next-gen can swap this to better NER later
        if not text:
            return []
        ents = [m.group(1).strip() for m in ENTITY_PAT.finditer(text)]
        # de-dupe preserving order
        seen = set()
        out = []
        for e in ents:
            if e.lower() in seen:
                continue
            seen.add(e.lower())
            out.append(e)
        return out[:25]

    def ingest_text(self, doc_id: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        meta = meta or {}
        self.upsert_node(doc_id, kind="doc", meta=meta)
        ents = self.extract_entities(text)
        for e in ents:
            self.upsert_node(e, kind="entity", meta={})
            self.add_edge(doc_id, e, rel="mentions", weight=1.0)
        return {"doc_id": doc_id, "entities": ents, "count": len(ents)}

    def neighborhood(self, node_id: str, limit: int = 50) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            edges = conn.execute(
                "SELECT src,dst,rel,weight,created_ts FROM edges WHERE src=? OR dst=? ORDER BY created_ts DESC LIMIT ?",
                (node_id, node_id, int(limit)),
            ).fetchall()
            nodes = conn.execute(
                "SELECT id,kind,meta,created_ts FROM nodes WHERE id=?",
                (node_id,),
            ).fetchall()
        return {
            "node": node_id,
            "nodes": [{"id": i, "kind": k, "meta": json.loads(m), "created_ts": ts} for i,k,m,ts in nodes],
            "edges": [{"src": s, "dst": d, "rel": r, "weight": w, "created_ts": ts} for s,d,r,w,ts in edges],
        }
