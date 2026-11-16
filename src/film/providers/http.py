"""Shared HTTP helpers: retries with exponential backoff, downloads, data URIs."""
from __future__ import annotations

import base64
import mimetypes
import random
import time
from pathlib import Path

import requests

from .base import ContentRejected, TransientError

RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


def call(method: str, url: str, *, attempts: int = 5, base: float = 4.0, cap: float = 120.0,
         timeout: float = 300, **kw) -> requests.Response:
    last: Exception | None = None
    for i in range(attempts):
        try:
            r = requests.request(method, url, timeout=timeout, **kw)
            if r.status_code in RETRY_STATUS:
                raise TransientError(f"{r.status_code} {r.text[:200]}")
            if r.status_code in (400, 422) and any(
                w in r.text.lower() for w in ("safety", "content policy", "moderation", "nsfw", "blocked")
            ):
                raise ContentRejected(r.text[:400])
            r.raise_for_status()
            return r
        except (TransientError, requests.ConnectionError, requests.Timeout) as e:
            last = e
            delay = min(cap, base * 2 ** i) * (0.5 + random.random() / 2)
            time.sleep(delay)
    raise TransientError(f"gave up after {attempts} attempts: {last}")


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with call("GET", url, stream=True) as r, dest.open("wb") as fh:
        for chunk in r.iter_content(1 << 20):
            fh.write(chunk)
    return dest


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()
