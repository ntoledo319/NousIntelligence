from __future__ import annotations
import re
from typing import Dict, List

_BANNED = [
    r"\b(as an ai)\b",
    r"\bi can't\b",
    r"\bi cannot\b",
    r"\bclick here\b",
    r"\bsit tight\b",
]

def lint(text: str) -> List[str]:
    issues: List[str] = []
    t = (text or "").strip()
    if not t:
        return ["empty_output"]
    if len(t) < 20:
        issues.append("too_short")
    if len(t) > 12000:
        issues.append("too_long")
    for pat in _BANNED:
        if re.search(pat, t, re.I):
            issues.append(f"banned_phrase:{pat}")
    return issues

def score(text: str) -> Dict:
    issues = lint(text)
    s = 1.0
    s -= 0.25 * sum(1 for i in issues if i.startswith("banned_phrase"))
    s -= 0.10 * sum(1 for i in issues if i in ("too_short", "too_long", "empty_output"))
    s = max(0.0, min(1.0, s))
    return {"score": s, "issues": issues}

