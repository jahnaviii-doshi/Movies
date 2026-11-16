"""Adapter registry and the one code path every generation goes through: `produce()`."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .. import ledger
from ..manifest import Manifest, input_hash
from ..project import Project
from .base import ContentRejected, Provider, Request, Result, TransientError  # noqa: F401
from .elevenlabs import ElevenMusic, ElevenSfx, ElevenVoice
from .fal import FalImage, FalLipSync, FalVideo
from .gemini import GeminiImage
from .mock import (MockImage, MockLipSync, MockMusic, MockSfx, MockVideo, MockVoice, SessionQC)

# (adapter, role kind) -> class
REGISTRY: dict[tuple[str, str], type[Provider]] = {
    ("fal", "image"): FalImage,
    ("fal", "video"): FalVideo,
    ("fal", "lipsync"): FalLipSync,
    ("gemini", "image"): GeminiImage,
    ("elevenlabs", "voice"): ElevenVoice,
    ("elevenlabs", "music"): ElevenMusic,
    ("elevenlabs", "sfx"): ElevenSfx,
    ("mock", "image"): MockImage,
    ("mock", "video"): MockVideo,
    ("mock", "voice"): MockVoice,
    ("mock", "music"): MockMusic,
    ("mock", "sfx"): MockSfx,
    ("mock", "lipsync"): MockLipSync,
    ("session", "qc"): SessionQC,
}

ROLE_KIND = {"image": "image", "video": "video", "video_hero": "video", "voice": "voice",
             "voice_scratch": "voice", "music": "music", "sfx": "sfx", "lipsync": "lipsync", "qc": "qc"}


def get(project: Project, role: str, override_adapter: str | None = None) -> Provider:
    cfg = project.provider_cfg(role)
    adapter = override_adapter or cfg["adapter"]
    cls = REGISTRY.get((adapter, ROLE_KIND[role]))
    if cls is None:
        raise KeyError(f"no adapter {adapter!r} for role {role!r}")
    prov = cls(project, role)
    if override_adapter:
        prov.adapter = override_adapter
    return prov


def produce(project: Project, *, role: str, key: str, phase: str, shot_id: str, req: Request,
            out: Path, guard: ledger.BudgetGuard, dry_run: bool = False, force: bool = False,
            mock: bool = False) -> dict:
    """Idempotent, budget-guarded, logged generation of one asset.

    Returns a dict: {status: cached|approved|dry-run|generated|rejected|failed, cost, files, reason}
    """
    prov = get(project, role, "mock" if mock else None)
    man = Manifest(project)
    h = input_hash(req.hash_inputs(prov.adapter, prov.model))
    should, reason = man.decide(key, h)
    if not should and not force:
        rec = man.get(key)
        return {"status": "approved" if "approved" in reason else "cached", "reason": reason,
                "files": rec["files"], "cost": 0.0}

    units, est = prov.estimate(req)
    if mock:
        est = 0.0
    if dry_run:
        return {"status": "dry-run", "reason": reason, "files": [], "cost": est, "units": units}

    guard.reserve(est, f"{phase}/{shot_id}/{key}")  # budget halts first, before anything else
    ok, why = prov.ready()
    if not ok:
        guard.release(est)
        raise RuntimeError(f"{role} provider not ready: {why}")
    try:
        res: Result = prov.run(req, out)
    except ContentRejected as e:
        guard.release(est)
        man.record(key, h=h, files=[], cost=0.0, status="rejected", error=str(e)[:300])
        return {"status": "rejected", "reason": str(e)[:300], "files": [], "cost": 0.0}
    except Exception:
        guard.release(est)
        raise

    cost = 0.0 if mock else res.cost_usd
    ledger.log(project, phase=phase, shot_id=shot_id, provider=prov.adapter, model=prov.model,
               units=res.units, cost=cost, note=key)
    guard.release(est)  # after logging, so the spend is never invisible to other workers
    sidecar = {
        "key": key, "input_hash": h, "role": role, "adapter": prov.adapter, "model": prov.model,
        "prompt": req.prompt, "negative": req.negative, "params": req.params,
        "reference_files": [str(r) for r in req.refs], "files": [str(f) for f in res.files],
        "units": res.units, "cost_usd": cost, "meta": res.meta,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    for f in res.files:
        Path(f).with_suffix(Path(f).suffix + ".json").write_text(json.dumps(sidecar, indent=2, ensure_ascii=False))
    man.record(key, h=h, files=res.files, cost=cost, role=role, phase=phase, shot_id=shot_id)
    return {"status": "generated", "reason": reason, "files": [str(f) for f in res.files], "cost": cost}
