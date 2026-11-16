"""Provider-agnostic adapter interfaces.

Each role in config.yaml (image, video, video_hero, voice, voice_scratch, music,
sfx, lipsync, qc) names an adapter + model + price ref. Swapping a vendor means
editing one line of config, or adding one small adapter module.
"""
from __future__ import annotations

import abc
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..project import Project


@dataclass
class Request:
    """Everything that determines an output. Hashed for idempotency, saved in the sidecar."""
    prompt: str
    refs: list[Path] = field(default_factory=list)       # reference images / first frame / audio in
    params: dict[str, Any] = field(default_factory=dict) # duration_s, aspect, seed, voice_id, ...
    negative: str = ""

    def hash_inputs(self, adapter: str, model: str) -> dict:
        return {"adapter": adapter, "model": model, "prompt": self.prompt, "negative": self.negative,
                "refs": [str(r) for r in self.refs], "params": self.params}


@dataclass
class Result:
    files: list[Path]
    units: float
    cost_usd: float
    meta: dict[str, Any] = field(default_factory=dict)   # seed actually used, vendor request id, ...


class TransientError(RuntimeError):
    """Retryable (rate limit, 5xx, timeout)."""


class ContentRejected(RuntimeError):
    """The provider's safety filter refused the request. Not retried as-is."""


class Provider(abc.ABC):
    role_kind = "generic"

    def __init__(self, project: Project, role: str):
        self.p = project
        self.role = role
        self.cfg = project.provider_cfg(role)
        self.adapter = self.cfg["adapter"]
        self.model = self.cfg.get("model", self.adapter)
        self.price = project.price(self.cfg["price"])

    # ---- cost --------------------------------------------------------
    def units_for(self, req: Request) -> float:
        unit = self.price["unit"]
        if unit == "image":
            return float(req.params.get("num_images", 1))
        if unit == "second":
            return float(math.ceil(req.params.get("duration_s", 5)))
        if unit == "kchar":
            return len(req.prompt) / 1000.0
        if unit == "minute":
            return req.params.get("duration_s", 30) / 60.0
        return 1.0

    def estimate(self, req: Request) -> tuple[float, float]:
        u = self.units_for(req)
        return u, round(u * float(self.price["usd"]), 4)

    # ---- capability --------------------------------------------------
    def required_keys(self) -> list[str]:
        return []

    def ready(self) -> tuple[bool, str]:
        missing = [k for k in self.required_keys() if not self.p.has_key(k)]
        return (not missing, "missing " + ", ".join(missing) if missing else "ok")

    @abc.abstractmethod
    def run(self, req: Request, out: Path) -> Result:
        """Perform the call and write the output file(s) next to `out` (same stem)."""


class ImageProvider(Provider):
    role_kind = "image"


class VideoProvider(Provider):
    role_kind = "video"


class VoiceProvider(Provider):
    role_kind = "voice"


class MusicProvider(Provider):
    role_kind = "music"


class SfxProvider(Provider):
    role_kind = "sfx"


class LipSyncProvider(Provider):
    role_kind = "lipsync"


class QCProvider(Provider):
    role_kind = "qc"
