from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from utils.http import http_get_json, HTTPError


class LyricsError(RuntimeError):
    pass


def _clean(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("\r", "")
    return s


@dataclass
class LyricsResult:
    provider: str
    lyrics: str


class LyricsProvider:
    name: str = "base"

    def fetch(self, artist: str, title: str) -> Optional[LyricsResult]:
        raise NotImplementedError


class LyricsOvhProvider(LyricsProvider):
    name = "lyrics.ovh"

    def fetch(self, artist: str, title: str) -> Optional[LyricsResult]:
        try:
            data = http_get_json(f"https://api.lyrics.ovh/v1/{artist}/{title}")
        except HTTPError:
            return None
        lyr = _clean(str(data.get("lyrics") or ""))
        if not lyr:
            return None
        return LyricsResult(provider=self.name, lyrics=lyr)


class MusixmatchProvider(LyricsProvider):
    name = "musixmatch"

    def __init__(self) -> None:
        self.key = os.environ.get("MUSIXMATCH_API_KEY", "").strip()

    def fetch(self, artist: str, title: str) -> Optional[LyricsResult]:
        if not self.key:
            return None
        try:
            track_search = http_get_json(
                "https://api.musixmatch.com/ws/1.1/track.search",
                params={"q_artist": artist, "q_track": title, "page_size": 1, "apikey": self.key},
            )
            track_list = (track_search.get("message") or {}).get("body", {}).get("track_list") or []
            if not track_list:
                return None
            track = (track_list[0].get("track") or {})
            tid = track.get("track_id")
            if not tid:
                return None
            lyr_data = http_get_json(
                "https://api.musixmatch.com/ws/1.1/track.lyrics.get",
                params={"track_id": tid, "apikey": self.key},
            )
            lyr_body = (lyr_data.get("message") or {}).get("body", {})
            lyrics = ((lyr_body.get("lyrics") or {}).get("lyrics_body") or "")
            lyrics = _clean(lyrics)
            lyrics = re.sub(r"\*\*\*\*\*.*$", "", lyrics, flags=re.DOTALL).strip()
            if not lyrics:
                return None
            return LyricsResult(provider=self.name, lyrics=lyrics)
        except HTTPError:
            return None


class GeniusProvider(LyricsProvider):
    name = "genius"

    def __init__(self) -> None:
        self.token = os.environ.get("GENIUS_ACCESS_TOKEN", "").strip()

    def fetch(self, artist: str, title: str) -> Optional[LyricsResult]:
        if not self.token:
            return None
        # No scraping here.
        return None


def default_providers() -> List[LyricsProvider]:
    return [
        LyricsOvhProvider(),
        MusixmatchProvider(),
        GeniusProvider(),
    ]


def analyze_lyrics(lyrics: str) -> Dict[str, Any]:
    text = _clean(lyrics)
    low = text.lower()

    THEMES = {
        "love": ["love", "heart", "kiss", "darling", "baby"],
        "grief": ["cry", "tears", "gone", "miss you", "loss", "goodbye"],
        "anxiety": ["anxious", "panic", "worry", "fear", "nervous"],
        "anger": ["hate", "rage", "mad", "fire", "kill"],
        "hope": ["hope", "light", "rise", "tomorrow", "faith"],
        "party": ["dance", "party", "club", "drink", "tonight"],
        "sex": ["touch", "body", "naked", "bed"],
        "loneliness": ["alone", "lonely", "empty", "no one"],
        "resilience": ["strong", "fight", "survive", "again"],
        "nature": ["ocean", "river", "sky", "rain", "sun"],
    }

    themes: List[str] = []
    for theme, kws in THEMES.items():
        score = 0
        for kw in kws:
            if kw in low:
                score += 1
        if score:
            themes.append(theme)

    POS = ["love", "joy", "happy", "smile", "hope", "light", "free"]
    NEG = ["sad", "cry", "hate", "fear", "alone", "pain", "die"]

    pos = sum(low.count(w) for w in POS)
    neg = sum(low.count(w) for w in NEG)
    sentiment = 0.0
    if pos + neg > 0:
        sentiment = (pos - neg) / float(pos + neg)

    return {
        "len_chars": len(text),
        "len_lines": len([l for l in text.split("\n") if l.strip()]),
        "themes": themes,
        "sentiment": sentiment,
    }
