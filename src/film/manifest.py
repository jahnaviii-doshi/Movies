"""Content-addressed asset manifest (logs/manifest.json).

Every asset has a key (e.g. "keyframe:S03_SH014:a") and an input hash computed
from its prompt, model, params and the bytes of every reference file. Rules:

* approved assets are never regenerated, even if the inputs change (a warning
  is printed instead; use `--force` on a command after un-approving).
* generated assets with the same input hash are reused (crash-safe resume).
* anything else is (re)generated.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .project import Project

_lock = threading.RLock()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_hash(inputs: dict[str, Any]) -> str:
    """Hash of request inputs. Any value that is an existing file path is hashed by content."""
    def norm(v):
        if isinstance(v, Path) or (isinstance(v, str) and len(v) < 4096 and os.path.isfile(v)):
            return {"file_sha256": file_hash(Path(v))}
        if isinstance(v, dict):
            return {k: norm(v[k]) for k in sorted(v)}
        if isinstance(v, (list, tuple)):
            return [norm(x) for x in v]
        return v
    blob = json.dumps(norm(inputs), sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


class Manifest:
    def __init__(self, p: Project):
        self.path = p.logs / "manifest.json"
        self.data: dict[str, dict] = {}
        if self.path.exists():
            self.data = json.loads(self.path.read_text() or "{}")

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".manifest.")
        with os.fdopen(fd, "w") as fh:
            json.dump(self.data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)  # atomic: a crash never leaves a half-written manifest

    def get(self, key: str) -> dict | None:
        return self.data.get(key)

    def decide(self, key: str, h: str) -> tuple[bool, str]:
        """Return (should_generate, reason)."""
        rec = self.data.get(key)
        if rec is None:
            return True, "new"
        if rec.get("status") == "approved":
            if rec.get("hash") != h:
                return False, "approved (inputs changed since approval; un-approve to regenerate)"
            return False, "approved"
        if rec.get("hash") == h and rec.get("status") in ("generated", "selected") and all(
            Path(f).exists() for f in rec.get("files", [])
        ):
            return False, "cached"
        return True, "inputs changed" if rec.get("hash") != h else "missing files"

    def record(self, key: str, *, h: str, files: list[Path], cost: float, status: str = "generated",
               **extra: Any) -> None:
        with _lock:
            self.data[key] = {
                "hash": h,
                "status": status,
                "files": [str(f) for f in files],
                "cost_usd": round(cost, 4),
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                **extra,
            }
            self._save()

    def set_status(self, key: str, status: str) -> None:
        with _lock:
            self.data[key]["status"] = status
            self.data[key]["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            self._save()

    def counts(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for k, rec in self.data.items():
            kind = k.split(":", 1)[0]
            out.setdefault(kind, {}).setdefault(rec.get("status", "?"), 0)
            out[kind][rec.get("status", "?")] += 1
        return out
