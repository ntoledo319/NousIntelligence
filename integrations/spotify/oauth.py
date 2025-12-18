from __future__ import annotations

import base64
import os
import time
from typing import Any, Dict, Optional

import requests

# FIXED: Replaced placeholder/proxy URLs with official Spotify endpoints
SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


class SpotifyOAuthError(RuntimeError):
    pass


class SpotifyOAuth:
    """Lightweight Spotify OAuth manager (authorization code + refresh token)."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str,
        timeout_s: int = 12,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.timeout_s = int(timeout_s)

    @classmethod
    def from_env(cls) -> "SpotifyOAuth":
        client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
        redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "")
        raw_scopes = os.environ.get(
            "SPOTIFY_SCOPES",
            "user-read-email user-read-private user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played user-top-read playlist-read-private playlist-modify-public playlist-modify-private",
        )
        scope = " ".join([s.strip() for s in raw_scopes.replace(",", " ").split() if s.strip()])
        return cls(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    def _basic_auth_header(self) -> str:
        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("utf-8")

    def build_authorize_url(self, state: str) -> str:
        if not self.is_configured():
            raise SpotifyOAuthError("Spotify OAuth not configured: missing env vars")

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
            "show_dialog": "false",
        }
        req = requests.Request("GET", SPOTIFY_AUTHORIZE_URL, params=params).prepare()
        return str(req.url)

    def exchange_code(self, code: str) -> Dict[str, Any]:
        if not code:
            raise SpotifyOAuthError("Missing code")

        headers = {
            "Authorization": self._basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        r = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=self.timeout_s)
        if r.status_code < 200 or r.status_code >= 300:
            raise SpotifyOAuthError(f"Token exchange failed: {r.status_code} {r.text}")

        token = r.json()
        expires_in = float(token.get("expires_in") or 3600)
        token["expires_at"] = time.time() + expires_in
        return token

    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        if not refresh_token:
            raise SpotifyOAuthError("Missing refresh_token")

        headers = {
            "Authorization": self._basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        r = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=self.timeout_s)
        if r.status_code < 200 or r.status_code >= 300:
            raise SpotifyOAuthError(f"Token refresh failed: {r.status_code} {r.text}")

        token = r.json()
        expires_in = float(token.get("expires_in") or 3600)
        token["expires_at"] = time.time() + expires_in
        if "refresh_token" not in token:
            token["refresh_token"] = refresh_token
        return token
