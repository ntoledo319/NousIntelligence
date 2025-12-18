from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests

from .oauth import SpotifyOAuth
from .token_store import TokenData, get_token_store


class SpotifyAuthRequired(RuntimeError):
    pass


class SpotifyAPI:
    """Thin Spotify Web API client with auto-refresh."""

    # FIXED: Replaced placeholder/proxy URL with official API endpoint
    BASE = "https://api.spotify.com/v1"

    def __init__(self, oauth: SpotifyOAuth, user_id: str, timeout_s: int = 12):
        self.oauth = oauth
        self.user_id = user_id
        self.timeout_s = int(timeout_s)
        self.store = get_token_store()

    def _token(self) -> TokenData:
        token = self.store.get(self.user_id)
        if not token or not token.access_token:
            raise SpotifyAuthRequired("Spotify not connected for this user")
        if token.is_expired():
            if not token.refresh_token:
                raise SpotifyAuthRequired("Spotify token expired and no refresh token available")
            refreshed = self.oauth.refresh(token.refresh_token)
            token = TokenData.from_mapping(self.user_id, refreshed)
            self.store.save(token)
        return token

    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json_body: Any = None) -> Any:
        tok = self._token()
        url = path if path.startswith("http") else f"{self.BASE}{path}"
        headers = {"Authorization": f"{tok.token_type} {tok.access_token}"}
        r = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=self.timeout_s)
        if r.status_code == 401 and tok.refresh_token:
            refreshed = self.oauth.refresh(tok.refresh_token)
            tok = TokenData.from_mapping(self.user_id, refreshed)
            self.store.save(tok)
            headers["Authorization"] = f"{tok.token_type} {tok.access_token}"
            r = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=self.timeout_s)

        if r.status_code == 204:
            return None
        if r.status_code < 200 or r.status_code >= 300:
            raise RuntimeError(f"Spotify API error {r.status_code}: {r.text}")

        return r.json()

    def get_me(self) -> Dict[str, Any]:
        return self.request("GET", "/me")

    def get_current_playback(self) -> Optional[Dict[str, Any]]:
        return self.request("GET", "/me/player")

    def get_recently_played(self, limit: int = 50) -> Dict[str, Any]:
        return self.request("GET", "/me/player/recently-played", params={"limit": int(limit)})

    def get_top_tracks(self, limit: int = 20, time_range: str = "medium_term") -> Dict[str, Any]:
        return self.request("GET", "/me/top/tracks", params={"limit": int(limit), "time_range": time_range})

    def get_track(self, track_id: str) -> Dict[str, Any]:
        return self.request("GET", f"/tracks/{track_id}")

    def get_audio_features(self, track_ids: List[str]) -> Dict[str, Any]:
        ids = ",".join(track_ids)
        return self.request("GET", "/audio-features", params={"ids": ids})

    def search(self, query: str, types: str = "track", limit: int = 10) -> Dict[str, Any]:
        return self.request("GET", "/search", params={"q": query, "type": types, "limit": int(limit)})

    def play(self, device_id: Optional[str] = None, uris: Optional[List[str]] = None, context_uri: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        body: Dict[str, Any] = {}
        if uris:
            body["uris"] = uris
        if context_uri:
            body["context_uri"] = context_uri
        self.request("PUT", "/me/player/play", params=params, json_body=body)

    def pause(self, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("PUT", "/me/player/pause", params=params)

    def next(self, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("POST", "/me/player/next", params=params)

    def previous(self, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("POST", "/me/player/previous", params=params)
