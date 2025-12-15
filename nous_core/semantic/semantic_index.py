from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAS_EMBED = True
except Exception:
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore
    _HAS_EMBED = False

class SemanticIndex:
    """
    SQLite semantic index.
    - Always works in keyword mode.
    - If sentence-transformers is installed, uses embeddings too.
    """
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.model = SentenceTransformer(model_name) if _HAS_EMBED else None

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS docs (
                    doc_id TEXT PRIMARY KEY,
                    text   TEXT NOT NULL,
                    meta   TEXT NOT NULL,
                    emb    BLOB
                )
            """)
            conn.commit()

    def _embed(self, text: str) -> Optional[bytes]:
        if not _HAS_EMBED or self.model is None:
            return None
        v = self.model.encode([text], normalize_embeddings=True)[0].astype("float32")
        return v.tobytes()

    def upsert(self, doc_id: str, text: str, meta: Dict[str, Any]) -> None:
        emb = self._embed(text)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO docs(doc_id,text,meta,emb) VALUES(?,?,?,?)",
                (doc_id, text, json.dumps(meta, ensure_ascii=False), emb),
            )
            conn.commit()

    def bulk_upsert(self, items: Iterable[Tuple[str, str, Dict[str, Any]]]) -> int:
        n = 0
        with sqlite3.connect(self.db_path) as conn:
            for doc_id, text, meta in items:
                emb = self._embed(text)
                conn.execute(
                    "INSERT OR REPLACE INTO docs(doc_id,text,meta,emb) VALUES(?,?,?,?)",
                    (doc_id, text, json.dumps(meta, ensure_ascii=False), emb),
                )
                n += 1
            conn.commit()
        return n

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT doc_id,text,meta,emb FROM docs").fetchall()

        q = (query or "").strip()
        if not q:
            return []

        # Keyword fallback
        if not _HAS_EMBED or self.model is None:
            ql = q.lower()
            scored = []
            for doc_id, text, meta, _emb in rows:
                score = text.lower().count(ql)
                if score:
                    scored.append((float(score), doc_id, text, meta))
            scored.sort(reverse=True)
            out = []
            for score, doc_id, text, meta in scored[:top_k]:
                out.append({"doc_id": doc_id, "score": score, "text": text, "meta": json.loads(meta)})
            return out

        # Embedding similarity
        qv = self.model.encode([q], normalize_embeddings=True)[0].astype("float32")
        out2 = []
        for doc_id, text, meta, emb in rows:
            if emb is None:
                continue
            dv = np.frombuffer(emb, dtype="float32")
            score = float(np.dot(qv, dv))
            out2.append((score, doc_id, text, meta))
        out2.sort(reverse=True)
        res = []
        for score, doc_id, text, meta in out2[:top_k]:
            res.append({"doc_id": doc_id, "score": score, "text": text, "meta": json.loads(meta)})
        return res

