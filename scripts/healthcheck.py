#!/usr/bin/env python3
import requests, sys

def main():
    base = "http://127.0.0.1:5000"
    for path in ("/health", "/api/v2/health"):
        r = requests.get(base + path, timeout=2)
        print(path, r.status_code, r.text[:200])
        if r.status_code != 200:
            return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

