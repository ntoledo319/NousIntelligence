from __future__ import annotations

import time
from typing import Any, Dict

try:
    from database import db
except Exception:
    db = None


if db is not None:

    class SpotifyToken(db.Model):
        """Per-user Spotify OAuth tokens (user_id is string to support demo users)."""

        __tablename__ = "spotify_tokens"

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(128), nullable=False, index=True, unique=True)
        access_token = db.Column(db.Text, nullable=False)
        refresh_token = db.Column(db.Text, nullable=True)
        token_type = db.Column(db.String(32), nullable=True, default="Bearer")
        scope = db.Column(db.Text, nullable=True, default="")
        expires_at = db.Column(db.Float, nullable=True, default=0.0)
        created_at = db.Column(db.Float, nullable=False, default=lambda: float(time.time()))
        updated_at = db.Column(db.Float, nullable=False, default=lambda: float(time.time()))

        def to_dict(self) -> Dict[str, Any]:
            return {
                "user_id": self.user_id,
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_type": self.token_type,
                "scope": self.scope,
                "expires_at": float(self.expires_at or 0),
                "created_at": float(self.created_at or 0),
                "updated_at": float(self.updated_at or 0),
            }

        def update_from_token(self, token: Dict[str, Any]) -> None:
            self.access_token = str(token.get("access_token") or "")
            if token.get("refresh_token"):
                self.refresh_token = str(token.get("refresh_token"))
            self.token_type = str(token.get("token_type") or "Bearer")
            self.scope = str(token.get("scope") or "")
            self.expires_at = float(token.get("expires_at") or 0)
            self.updated_at = float(time.time())

else:
    SpotifyToken = None  # type: ignore
