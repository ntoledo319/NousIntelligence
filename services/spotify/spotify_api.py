from __future__ import annotations

import base64
import os
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from utils.http import http_get_json, http_post_form_json, HTTPError


class SpotifyAuthError(RuntimeError):
    pass


class SpotifyAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class SpotifyConfig:
    client_id: str
    client_secret: str
    redirect_uri: str


SPOTIFY_ACCOUNTS = "https://accounts.spotify.com"
SPOTIFY_API = "https://api.spotify.com/v1"

DEFAULT_SCOPES = [
    "user-read-email",
    "user-read-private",
    "user-read-recently-played",
    "user-top-read",
    "user-read-playback-state",
    "user-read-currently-playing",
    "playlist-read-private",
    "playlist-modify-private",
    "playlist-modify-public",
    "user-library-read",
]


def _basic_auth_header(client_id: str, client_secret: str) -> Dict[str, str]:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    return {"Authorization": f"Basic {b64}"}


class SpotifyAPI:
    def __init__(self, config: SpotifyConfig) -> None:
        self.config = config

    @staticmethod
    def from_env() -> "SpotifyAPI":
        cid = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
        sec = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
        redir = os.environ.get("SPOTIFY_REDIRECT_URI", "").strip()
        if not cid or not sec or not redir:
            raise SpotifyAuthError(
                "Missing Spotify OAuth env vars. Need SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI."
            )
        return SpotifyAPI(SpotifyConfig(client_id=cid, client_secret=sec, redirect_uri=redir))

    # ── OAuth ──────────────────────────────────────────────────────────

    def build_authorize_url(self, state: str, scopes: Optional[List[str]] = None, show_dialog: bool = True) -> str:
        scopes = scopes or list(DEFAULT_SCOPES)
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "show_dialog": "true" if show_dialog else "false",
        }
        return f"{SPOTIFY_ACCOUNTS}/authorize?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str) -> Dict[str, Any]:
        try:
            tok = http_post_form_json(
                f"{SPOTIFY_ACCOUNTS}/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                },
                headers=_basic_auth_header(self.config.client_id, self.config.client_secret),
            )
        except HTTPError as e:
            raise SpotifyAuthError(str(e)) from e

        expires_in = int(tok.get("expires_in", 3600))
        tok["expires_at"] = time.time() + expires_in - 30
        return tok

    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        try:
            tok = http_post_form_json(
                f"{SPOTIFY_ACCOUNTS}/api/token",
                data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                headers=_basic_auth_header(self.config.client_id, self.config.client_secret),
            )
        except HTTPError as e:
            raise SpotifyAuthError(str(e)) from e

        expires_in = int(tok.get("expires_in", 3600))
        tok["expires_at"] = time.time() + expires_in - 30
        if "refresh_token" not in tok:
            tok["refresh_token"] = refresh_token
        return tok

    # ── Core request helper ────────────────────────────────────────────

    def _auth_headers(self, access_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    def api_get(self, access_token: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = path if path.startswith("http") else f"{SPOTIFY_API}{path}"
        try:
            return http_get_json(url, params=params, headers=self._auth_headers(access_token))
        except HTTPError as e:
            raise SpotifyAPIError(str(e)) from e

    def api_post_json(self, access_token: str, path: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        import requests

        url = path if path.startswith("http") else f"{SPOTIFY_API}{path}"
        try:
            r = requests.post(
                url,
                headers={**self._auth_headers(access_token), "Content-Type": "application/json"},
                json=json_body,
                timeout=(5.0, 20.0),
            )
        except Exception as e:
            raise SpotifyAPIError(f"POST {url} failed: {e}") from e
        if r.status_code >= 400:
            body = (r.text or "").strip()
            raise SpotifyAPIError(f"POST {r.url} -> {r.status_code}: {body[:500]}")
        try:
            return r.json()
        except Exception:
            return {}

    # ── Spotify endpoints we care about ────────────────────────────────

    def me(self, access_token: str) -> Dict[str, Any]:
        return self.api_get(access_token, "/me")

    def recently_played(self, access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
        data = self.api_get(access_token, "/me/player/recently-played", params={"limit": int(limit)})
        return list(data.get("items") or [])

    def top_tracks(self, access_token: str, limit: int = 20, time_range: str = "short_term") -> List[Dict[str, Any]]:
        data = self.api_get(access_token, "/me/top/tracks", params={"limit": int(limit), "time_range": time_range})
        return list(data.get("items") or [])

    def audio_features(self, access_token: str, track_ids: List[str]) -> List[Dict[str, Any]]:
        ids = ",".join([t for t in track_ids if t])
        if not ids:
            return []
        data = self.api_get(access_token, "/audio-features", params={"ids": ids})
        feats = list(data.get("audio_features") or [])
        return [f for f in feats if isinstance(f, dict)]

    def recommendations(
        self,
        access_token: str,
        *,
        seed_tracks: Optional[List[str]] = None,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 50,
        tuneables: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": int(limit)}
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])
        if tuneables:
            for k, v in tuneables.items():
                if v is None:
                    continue
                params[k] = v
        data = self.api_get(access_token, "/recommendations", params=params)
        return list(data.get("tracks") or [])

    def create_playlist(
        self,
        access_token: str,
        *,
        user_id: str,
        name: str,
        description: str,
        public: bool = False,
    ) -> Dict[str, Any]:
        return self.api_post_json(
            access_token,
            f"/users/{urllib.parse.quote(user_id)}/playlists",
            {"name": name, "description": description, "public": bool(public)},
        )

    def add_tracks_to_playlist(self, access_token: str, *, playlist_id: str, track_uris: List[str]) -> Dict[str, Any]:
        uris = [u for u in track_uris if u]
        return self.api_post_json(
            access_token, f"/playlists/{urllib.parse.quote(playlist_id)}/tracks", {"uris": uris}
        )
