from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List


_WORD_RE = re.compile(r"[A-Za-z']+")

_COMMON = {
    "the", "and", "that", "this", "with", "from", "your", "you", "me", "my", "mine",
    "our", "ours", "their", "they", "them", "she", "her", "him", "he", "its", "i",
    "im", "we", "us", "a", "an", "to", "of", "in", "on", "for", "is", "are", "was",
    "were", "be", "been", "being", "do", "does", "did", "not", "no", "yes"
}

_POS = {"love", "hope", "free", "strong", "brave", "light", "happy", "joy", "smile", "peace", "grace", "heal", "healing", "safe", "home", "better", "beautiful"}
_NEG = {"hate", "pain", "hurt", "broken", "cry", "tears", "lonely", "alone", "fear", "anxiety", "die", "dead", "kill", "angry", "ashamed", "guilty"}

_THEME_SETS = {
    "love": {"love", "kiss", "heart", "baby", "darling"},
    "breakup": {"goodbye", "leave", "left", "gone", "alone", "apart", "missing"},
    "motivation": {"rise", "strong", "fight", "winning", "champion", "brave"},
    "anger": {"anger", "angry", "rage", "fight", "burn"},
    "anxiety": {"fear", "anxiety", "panic", "worry", "nervous"},
    "recovery": {"sober", "recovery", "clean", "drink", "drinking", "relapse", "bottle", "meeting"},
}


@dataclass
class LyricsAnalysis:
    fingerprint: str
    num_chars: int
    num_words: int
    top_keywords: List[str]
    sentiment: float
    themes: List[str]
    summary: str


def normalize(text: str) -> str:
    t = (text or "").strip()
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def fingerprint(text: str) -> str:
    h = hashlib.sha256()
    h.update((text or "").encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _tokens(text: str) -> List[str]:
    words = _WORD_RE.findall((text or "").lower())
    out: List[str] = []
    for w in words:
        if len(w) < 3:
            continue
        if w in _COMMON:
            continue
        out.append(w)
    return out


def extract_keywords(text: str, k: int = 20) -> List[str]:
    toks = _tokens(text)
    if not toks:
        return []
    c = Counter(toks)
    return [w for w, _ in c.most_common(k)]


def sentiment(text: str) -> float:
    toks = _tokens(text)
    if not toks:
        return 0.0
    pos = sum(1 for t in toks if t in _POS)
    neg = sum(1 for t in toks if t in _NEG)
    denom = max(1, pos + neg)
    return (pos - neg) / float(denom)


def detect_themes(text: str) -> List[str]:
    toks = set(_tokens(text))
    hits: List[str] = []
    for theme, kws in _THEME_SETS.items():
        if toks.intersection(kws):
            hits.append(theme)
    return hits


def analyze_lyrics(text: str) -> LyricsAnalysis:
    norm = normalize(text)
    fp = fingerprint(norm)
    toks = _tokens(norm)
    keys = extract_keywords(norm, k=20)
    sent = sentiment(norm)
    themes = detect_themes(norm)

    mood = "neutral"
    if sent > 0.25:
        mood = "positive"
    elif sent < -0.25:
        mood = "negative"

    summary = f"mood={mood}, themes={themes if themes else ['none']}, keywords={keys[:8] if keys else []}"

    return LyricsAnalysis(
        fingerprint=fp,
        num_chars=len(norm),
        num_words=len(toks),
        top_keywords=keys,
        sentiment=sent,
        themes=themes,
        summary=summary,
    )


def to_dict(a: LyricsAnalysis) -> Dict[str, Any]:
    return {
        "fingerprint": a.fingerprint,
        "num_chars": a.num_chars,
        "num_words": a.num_words,
        "top_keywords": a.top_keywords,
        "sentiment": a.sentiment,
        "themes": a.themes,
        "summary": a.summary or "",
    }
