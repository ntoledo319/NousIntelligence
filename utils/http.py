from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: Tuple[float, float] = (5.0, 20.0)  # (connect, read)


class HTTPError(RuntimeError):
    pass


def http_get_json(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Tuple[float, float] = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except Exception as e:
        raise HTTPError(f"GET {url} failed: {e}") from e

    if r.status_code >= 400:
        body = (r.text or "").strip()
        raise HTTPError(f"GET {r.url} -> {r.status_code}: {body[:500]}")
    try:
        return r.json()
    except Exception as e:
        raise HTTPError(f"GET {r.url} -> non-JSON response: {e}") from e


def http_post_form_json(
    url: str,
    *,
    data: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: Tuple[float, float] = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    h = {"Content-Type": "application/x-www-form-urlencoded"}
    if headers:
        h.update(headers)
    try:
        r = requests.post(url, data=data, headers=h, timeout=timeout)
    except Exception as e:
        raise HTTPError(f"POST {url} failed: {e}") from e

    if r.status_code >= 400:
        body = (r.text or "").strip()
        raise HTTPError(f"POST {r.url} -> {r.status_code}: {body[:500]}")
    try:
        return r.json()
    except Exception as e:
        raise HTTPError(f"POST {r.url} -> non-JSON response: {e}") from e
