#!/usr/bin/env python3
"""
Lightweight secret scanner for staged changes.

Scans only staged files for common secret patterns to reduce false positives
from documentation and historical artifacts elsewhere in the repository.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")
EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    "instance",
}

PATTERNS = [
    re.compile(
        r"(API[_-]?KEY\s*=|SECRET\s*=|PRIVATE[_-]?KEY\s*=|BEGIN (RSA|OPENSSH)|PASSWORD\s*=|TOKEN\s*=)",
        re.I,
    ),
    re.compile(r"(sk-[A-Za-z0-9]{20,})", re.I),
]


def is_binary(b: bytes) -> bool:
    """Return True if the provided bytes buffer looks like binary data."""
    return b"\x00" in b[:4096]


def should_skip_dir(name: str) -> bool:
    """Determine if a directory should be skipped during scanning."""
    return name in EXCLUDE_DIRS


def scan_file(fp: str) -> list[str]:
    """Scan a single file for secret-like patterns."""
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


def get_staged_files() -> list[str]:
    """Return staged file paths for scanning."""
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], text=True
        )
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    """Scan staged files for potential secrets."""
    targets = get_staged_files()
    if not targets:
        print("INFO: No staged files to scan for secrets.")
        return 0

    bad: list[tuple[str, list[str]]] = []
    for rel_path in targets:
        parts = rel_path.split(os.sep)
        if any(part in EXCLUDE_DIRS for part in parts):
            continue

        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(ROOT, rel_path)
        if not os.path.exists(abs_path) or os.path.isdir(abs_path):
            continue

        if abs_path.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".pdf",
                ".zip",
                ".tar",
                ".gz",
                ".sqlite",
                ".db",
                ".mp3",
                ".mp4",
                ".mov",
            )
        ):
            continue

        hits = scan_file(abs_path)
        if hits:
            bad.append((rel_path, hits))

    if bad:
        print("❌ Potential secrets detected:")
        for fp, hits in bad[:200]:
            print(f" - {fp}: {hits}")
        return 1

    print("✅ No obvious secrets detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
