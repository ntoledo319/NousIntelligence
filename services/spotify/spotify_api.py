from __future__ import annotations

import base64
import os
import time
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlencode

import requests

from services.spotify.spotify_store import SpotifyStore
from utils.http import http_post_form_json

logger = logging.getLogger(__name__)

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

DEFAULT_SCOPES = [
    # Playback control
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    # Library / history
    "user-read-recently-played",
    "user-top-read",
    # Playlists
    "playlist-read-private",
    "playlist-modify-private",
    "playlist-modify-public",
    # Profile
    "user-read-email",
    "user-read-private",
]


class SpotifyAuthError(RuntimeError):
    pass


class SpotifyAPIError(RuntimeError):
    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


@dataclass
class SpotifyConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str]


def _now() -> float:
    return time.time()


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


class SpotifyAPI:
    """
    Minimal Spotify Web API client with:
      - OAuth auth URL generation
      - code exchange + refresh
      - automatic token refresh
      - a thin set of commonly-used endpoints (search, devices, playback, recent, top, etc)

    It intentionally avoids spotipy so behavior is predictable and debuggable.
    """

    def __init__(self, store: SpotifyStore, user_id: str, cfg: SpotifyConfig) -> None:
        self.store = store
        self.user_id = user_id
        self.cfg = cfg

    @staticmethod
    def from_env(store: SpotifyStore, user_id: str, *, scopes: Optional[Sequence[str]] = None) -> "SpotifyAPI":
        client_id = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
        redirect_uri = (os.environ.get("SPOTIFY_REDIRECT_URI") or os.environ.get("SPOTIFY_REDIRECT") or "").strip()
        if not redirect_uri:
            # Common local dev default. Your deployed URL must be registered in Spotify dashboard.
            redirect_uri = "http://localhost:5000/callback/spotify"
        if not client_id or not client_secret:
            raise SpotifyAuthError("Missing SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET environment variables")
        sc = list(scopes) if scopes else list(DEFAULT_SCOPES)
        return SpotifyAPI(store, user_id, SpotifyConfig(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scopes=sc))

    # ── OAuth ──────────────────────────────────────────────────────────

    def get_authorize_url(self, *, state: str, show_dialog: bool = False) -> str:
        q = {
            "client_id": self.cfg.client_id,
            "response_type": "code",
            "redirect_uri": self.cfg.redirect_uri,
            "scope": " ".join(self.cfg.scopes),
            "state": state,
        }
        if show_dialog:
            q["show_dialog"] = "true"
        return SPOTIFY_AUTH_URL + "?" + urlencode(q)

    def exchange_code(self, code: str) -> Dict[str, Any]:
        headers = {"Authorization": _basic_auth_header(self.cfg.client_id, self.cfg.client_secret)}
        token = http_post_form_json(
            SPOTIFY_TOKEN_URL,
            data={"grant_type": "authorization_code", "code": code, "redirect_uri": self.cfg.redirect_uri},
            headers=headers,
        )
        token["expires_at"] = _now() + float(token.get("expires_in") or 0.0)
        self.store.save_tokens(self.user_id, token)
        return token

    def refresh(self) -> Dict[str, Any]:
        tok = self.store.get_tokens(self.user_id)
        if not tok or not tok.get("refresh_token"):
            raise SpotifyAuthError("No refresh_token available. Reconnect Spotify.")
        headers = {"Authorization": _basic_auth_header(self.cfg.client_id, self.cfg.client_secret)}
        token = http_post_form_json(
            SPOTIFY_TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]},
            headers=headers,
        )
        # Spotify may omit refresh_token on refresh; keep existing.
        if not token.get("refresh_token"):
            token["refresh_token"] = tok.get("refresh_token")
        token["expires_at"] = _now() + float(token.get("expires_in") or 0.0)
        self.store.save_tokens(self.user_id, token)
        return token

    def disconnect(self) -> None:
        self.store.delete_tokens(self.user_id)

    def is_connected(self) -> bool:
        tok = self.store.get_tokens(self.user_id)
        return bool(tok and tok.get("access_token"))

    # ── Core request ───────────────────────────────────────────────────

    def _get_access_token(self) -> str:
        tok = self.store.get_tokens(self.user_id)
        if not tok:
            raise SpotifyAuthError("Spotify not connected. Run 'connect spotify' or /api/v2/spotify/auth/url.")
        if float(tok.get("expires_at") or 0.0) <= _now() + 30.0:
            tok = self.refresh()
        return str(tok["access_token"])

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        allow_204: bool = False,
    ) -> Any:
        url = path if path.startswith("http") else (SPOTIFY_API_BASE + path)
        headers = {"Authorization": f"Bearer {self._get_access_token()}"}

        try:
            r = requests.request(method, url, params=params, json=json_body, data=data, headers=headers, timeout=(5.0, 20.0))
        except Exception as e:
            raise SpotifyAPIError(0, f"Spotify request failed: {e}") from e

        if allow_204 and r.status_code == 204:
            return None

        if r.status_code >= 400:
            try:
                details = r.json()
            except Exception:
                details = {"raw": (r.text or "")[:500]}
            msg = details.get("error", {}).get("message") if isinstance(details, dict) else None
            raise SpotifyAPIError(r.status_code, msg or f"Spotify API error {r.status_code}", details=details)

        if not r.text:
            return None
        return r.json()

    # ── Convenience endpoints (spotipy-ish) ────────────────────────────

    def me(self) -> Dict[str, Any]:
        return self.request("GET", "/me")

    def devices(self) -> Dict[str, Any]:
        return self.request("GET", "/me/player/devices")

    def current_playback(self) -> Optional[Dict[str, Any]]:
        return self.request("GET", "/me/player", allow_204=True)

    def currently_playing(self) -> Optional[Dict[str, Any]]:
        return self.request("GET", "/me/player/currently-playing", allow_204=True)

    def search(self, *, q: str, type: str = "track", limit: int = 5) -> Dict[str, Any]:
        return self.request("GET", "/search", params={"q": q, "type": type, "limit": int(limit)})

    def start_playback(
        self,
        *,
        uris: Optional[List[str]] = None,
        context_uri: Optional[str] = None,
        device_id: Optional[str] = None,
        position_ms: Optional[int] = None,
    ) -> None:
        body: Dict[str, Any] = {}
        if uris:
            body["uris"] = uris
        if context_uri:
            body["context_uri"] = context_uri
        if position_ms is not None:
            body["position_ms"] = int(position_ms)
        params = {"device_id": device_id} if device_id else None
        self.request("PUT", "/me/player/play", params=params, json_body=body, allow_204=True)

    def pause_playback(self, *, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("PUT", "/me/player/pause", params=params, allow_204=True)

    def next_track(self, *, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("POST", "/me/player/next", params=params, allow_204=True)

    def previous_track(self, *, device_id: Optional[str] = None) -> None:
        params = {"device_id": device_id} if device_id else None
        self.request("POST", "/me/player/previous", params=params, allow_204=True)

    def set_volume(self, volume_percent: int, *, device_id: Optional[str] = None) -> None:
        params = {"volume_percent": int(volume_percent)}
        if device_id:
            params["device_id"] = device_id
        self.request("PUT", "/me/player/volume", params=params, allow_204=True)

    def recently_played(self, *, limit: int = 50, after: Optional[int] = None, before: Optional[int] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": int(limit)}
        if after is not None:
            params["after"] = int(after)
        if before is not None:
            params["before"] = int(before)
        return self.request("GET", "/me/player/recently-played", params=params)

    def top_tracks(self, *, limit: int = 50, time_range: str = "medium_term") -> Dict[str, Any]:
        return self.request("GET", "/me/top/tracks", params={"limit": int(limit), "time_range": time_range})

    def top_artists(self, *, limit: int = 50, time_range: str = "medium_term") -> Dict[str, Any]:
        return self.request("GET", "/me/top/artists", params={"limit": int(limit), "time_range": time_range})

    def get_track(self, track_id: str) -> Dict[str, Any]:
        return self.request("GET", f"/tracks/{track_id}")

    def audio_features(self, track_ids: Sequence[str]) -> Dict[str, Any]:
        ids = ",".join([t for t in track_ids if t])
        return self.request("GET", "/audio-features", params={"ids": ids})

    def create_playlist(self, user_spotify_id: str, name: str, *, description: str = "", public: bool = False) -> Dict[str, Any]:
        return self.request(
            "POST",
            f"/users/{user_spotify_id}/playlists",
            json_body={"name": name, "description": description, "public": bool(public)},
        )

    def add_tracks_to_playlist(self, playlist_id: str, uris: Sequence[str]) -> Dict[str, Any]:
        # Spotify limit is 100 per call
        return self.request("POST", f"/playlists/{playlist_id}/tracks", json_body={"uris": list(uris)})

    # ── Compatibility wrappers (legacy code expects spotipy-ish names) ─────────────

    def track(self, track_id: str) -> Dict[str, Any]:
        return self.get_track(track_id)

    def get_recently_played(self, *, limit: int = 50, after: Optional[int] = None, before: Optional[int] = None) -> Dict[str, Any]:
        return self.recently_played(limit=limit, after=after, before=before)

    def get_top_tracks(self, *, limit: int = 50, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        data = self.top_tracks(limit=limit, time_range=time_range)
        return list((data.get("items") or []))

    def get_top_artists(self, *, limit: int = 50, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        data = self.top_artists(limit=limit, time_range=time_range)
        return list((data.get("items") or []))

    def get_audio_features(self, track_ids: Sequence[str]) -> List[Optional[Dict[str, Any]]]:
        data = self.audio_features(track_ids)
        # Spotify returns list aligned to ids (may include nulls)
        feats = data.get("audio_features") or []
        return list(feats)

    def search_playlists(self, query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
        data = self.request("GET", "/search", params={"q": query, "type": "playlist", "limit": int(limit)})
        return list(((data.get("playlists") or {}).get("items")) or [])

    def get_available_genre_seeds(self) -> List[str]:
        data = self.request("GET", "/recommendations/available-genre-seeds")
        return list(data.get("genres") or [])

    def get_recommendations(
        self,
        *,
        seed_artists: Optional[Sequence[str]] = None,
        seed_tracks: Optional[Sequence[str]] = None,
        seed_genres: Optional[Sequence[str]] = None,
        limit: int = 20,
        **tuneables: Any,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": int(limit)}
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists)
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks)
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres)
        # pass through tuneables (target_danceability, min_energy, etc)
        for k, v in tuneables.items():
            if v is None:
                continue
            params[k] = v
        return self.request("GET", "/recommendations", params=params)

    def get_artist_related_artists(self, artist_id: str) -> List[Dict[str, Any]]:
        data = self.request("GET", f"/artists/{artist_id}/related-artists")
        return list(data.get("artists") or [])

    def user_playlist_create(self, user: str, name: str, public: bool = False, description: str = "") -> Dict[str, Any]:
        return self.create_playlist(user, name, description=description, public=public)

    def user_playlist_add_tracks(self, user: str, playlist_id: str, tracks: Sequence[str]) -> Dict[str, Any]:
        # spotipy passes uris in "tracks"
        return self.add_tracks_to_playlist(playlist_id, tracks)
