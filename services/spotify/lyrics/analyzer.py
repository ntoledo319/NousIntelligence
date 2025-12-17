from __future__ import annotations

import re
from typing import Any, Dict

_WORD = re.compile(r"[A-Za-z']{2,}")
_LINE = re.compile(r"\r?\n+")

# Tiny, dumb lexicons. Good enough for a first pass; replace with real NLP later.
_POS = {
    "love","hope","bright","happy","peace","calm","safe","strong","free","alive","dream","shine","warm","light","heal","healing",
    "hold","home","okay","better","rise","rising","grace","smile","blessing","beautiful","courage",
}
_NEG = {
    "hate","pain","hurt","broken","dead","die","cry","alone","lost","dark","fear","scared","fall","falling","ash","cold","empty",
    "regret","guilt","shame","sick","kill","bleed","tears","burn","burning","numb",
}

_THEME_MAP = {
    "recovery": {"heal","healing","sober","clean","rise","rising","strong","free","alive"},
    "grief": {"dead","die","tears","cry","lost","ash"},
    "anxiety": {"fear","scared","panic","numb","cold","dark"},
    "love": {"love","heart","home","hold"},
    "self-worth": {"strong","okay","better","courage","beautiful"},
}


def analyze_lyrics(lyrics: str, *, max_excerpt_chars: int = 240) -> Dict[str, Any]:
    """
    Returns features you can safely store long-term even if you don't store full lyrics:
      - counts, sentiment-ish
      - keywords
      - themes
      - excerpt
    """
    txt = (lyrics or "").strip()
    words = [w.lower() for w in _WORD.findall(txt)]
    if not words:
        return {"has_lyrics": False}

    total = len(words)
    unique = len(set(words))

    pos = sum(1 for w in words if w in _POS)
    neg = sum(1 for w in words if w in _NEG)
    sentiment = (pos - neg) / max(1, total)

    # Top keywords by frequency (stopword-lite)
    stop = {"the","and","but","that","this","with","for","you","your","me","my","we","our","they","them","a","an","to","of","in","on","at","is","are","was","were","be","been","i","im","it's","its"}
    freq = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1
    top_keywords = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:15]

    themes = []
    wset = set(words)
    for theme, vocab in _THEME_MAP.items():
        score = len(wset.intersection(vocab))
        if score:
            themes.append({"theme": theme, "score": score})
    themes.sort(key=lambda d: d["score"], reverse=True)

    # Excerpt: first non-empty lines stitched.
    lines = [l.strip() for l in _LINE.split(txt) if l.strip()]
    excerpt = ""
    for l in lines[:6]:
        if len(excerpt) + len(l) + 1 > max_excerpt_chars:
            break
        excerpt = (excerpt + " " + l).strip()

    return {
        "has_lyrics": True,
        "word_count": total,
        "unique_word_count": unique,
        "pos_hits": pos,
        "neg_hits": neg,
        "sentiment": round(float(sentiment), 4),
        "top_keywords": [{"word": w, "count": c} for w, c in top_keywords],
        "themes": themes[:8],
        "excerpt": excerpt,
    }
