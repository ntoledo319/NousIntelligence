#!/usr/bin/env python3
from __future__ import annotations
import os, re, sys

ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")
EXCLUDE_DIRS = {".git","node_modules","dist","build",".venv","venv","__pycache__","instance"}

PATTERNS = [
    re.compile(r"(API[_-]?KEY|SECRET|PRIVATE[_-]?KEY|BEGIN (RSA|OPENSSH)|PASSWORD\s*=|TOKEN\s*=)", re.I),
    re.compile(r"(sk-[A-Za-z0-9]{20,})", re.I),
]

def is_binary(b: bytes) -> bool:
    return b"\x00" in b[:4096]

def should_skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS

def scan_file(fp: str) -> list[str]:
    try:
        with open(fp, "rb") as f:
            raw = f.read()
        if is_binary(raw):
            return []
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        return []
    hits = []
    for pat in PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits

def main() -> int:
    bad = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for fn in files:
            if fn.endswith((".png",".jpg",".jpeg",".gif",".pdf",".zip",".tar",".gz",".sqlite",".db",".mp3",".mp4",".mov")):
                continue
            fp = os.path.join(root, fn)
            hits = scan_file(fp)
            if hits:
                bad.append((fp, hits))

    if bad:
        print("❌ Potential secrets detected:")
        for fp, hits in bad[:200]:
            print(f" - {fp}: {hits}")
        return 1

    print("✅ No obvious secrets detected.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

