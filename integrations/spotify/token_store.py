from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TokenData:
    """Represents Spotify OAuth token state."""

    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    scope: str = ""
    expires_at: float = 0.0

    def is_expired(self, skew_seconds: int = 60) -> bool:
        return time.time() >= float(self.expires_at or 0) - skew_seconds

    @classmethod
    def from_mapping(cls, user_id: str, data: Dict[str, Any]) -> "TokenData":
        return cls(
            user_id=user_id,
            access_token=str(data.get("access_token") or ""),
            refresh_token=(data.get("refresh_token") or None),
            token_type=str(data.get("token_type") or "Bearer"),
            scope=str(data.get("scope") or ""),
            expires_at=float(data.get("expires_at") or 0),
        )


class BaseTokenStore:
    def get(self, user_id: str) -> Optional[TokenData]:
        raise NotImplementedError

    def save(self, token: TokenData) -> None:
        raise NotImplementedError

    def delete(self, user_id: str) -> None:
        raise NotImplementedError


class FileTokenStore(BaseTokenStore):
    """Token store for environments where DB is down/misconfigured."""

    def __init__(self, path: Optional[str] = None):
        base = Path(os.environ.get("INSTANCE_PATH") or "instance")
        base.mkdir(parents=True, exist_ok=True)
        self.path = Path(path) if path else (base / "spotify_tokens.json")
        self._lock = threading.Lock()

    def _load_all(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_all(self, data: Dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def get(self, user_id: str) -> Optional[TokenData]:
        with self._lock:
            all_data = self._load_all()
            raw = all_data.get(user_id)
            if not isinstance(raw, dict):
                return None
            return TokenData.from_mapping(user_id, raw)

    def save(self, token: TokenData) -> None:
        with self._lock:
            all_data = self._load_all()
            all_data[token.user_id] = asdict(token)
            self._write_all(all_data)

    def delete(self, user_id: str) -> None:
        with self._lock:
            all_data = self._load_all()
            if user_id in all_data:
                del all_data[user_id]
                self._write_all(all_data)


class SQLAlchemyTokenStore(BaseTokenStore):
    """Token store using the app's SQLAlchemy session (preferred when available)."""

    def __init__(self):
        from database import db
        from models.spotify_models import SpotifyToken

        self.db = db
        self.SpotifyToken = SpotifyToken

    def get(self, user_id: str) -> Optional[TokenData]:
        row = self.SpotifyToken.query.filter_by(user_id=user_id).first()
        if not row:
            return None
        return TokenData(
            user_id=row.user_id,
            access_token=row.access_token,
            refresh_token=row.refresh_token,
            token_type=row.token_type or "Bearer",
            scope=row.scope or "",
            expires_at=float(row.expires_at or 0),
        )

    def save(self, token: TokenData) -> None:
        row = self.SpotifyToken.query.filter_by(user_id=token.user_id).first()
        if not row:
            row = self.SpotifyToken(user_id=token.user_id)
            self.db.session.add(row)
        row.access_token = token.access_token
        row.refresh_token = token.refresh_token
        row.token_type = token.token_type
        row.scope = token.scope
        row.expires_at = float(token.expires_at)
        self.db.session.commit()

    def delete(self, user_id: str) -> None:
        row = self.SpotifyToken.query.filter_by(user_id=user_id).first()
        if row:
            self.db.session.delete(row)
            self.db.session.commit()


_token_store_singleton: Optional[BaseTokenStore] = None


def get_token_store() -> BaseTokenStore:
    """Choose DB store when possible; otherwise fall back to file store."""
    global _token_store_singleton
    if _token_store_singleton is not None:
        return _token_store_singleton

    try:
        _token_store_singleton = SQLAlchemyTokenStore()
        return _token_store_singleton
    except Exception:
        _token_store_singleton = FileTokenStore()
        return _token_store_singleton
