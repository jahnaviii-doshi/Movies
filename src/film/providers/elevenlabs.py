"""ElevenLabs adapter: dialogue (v3 / flash), music, sound effects."""
from __future__ import annotations

from pathlib import Path

from . import http
from .base import MusicProvider, Request, Result, SfxProvider, VoiceProvider

API = "https://api.elevenlabs.io/v1"


class _ElMixin:
    def required_keys(self):
        return ["ELEVENLABS_API_KEY"]

    def _h(self):
        return {"xi-api-key": self.p.env["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}


class ElevenVoice(_ElMixin, VoiceProvider):
    """req.prompt = the line, with v3 audio tags for performance e.g. "[whispers] Eighty years late."
    req.params: voice_id (required), language_code (optional), stability, style."""

    def run(self, req: Request, out: Path) -> Result:
        body = {"text": req.prompt, "model_id": self.model}
        if req.params.get("language_code"):
            body["language_code"] = req.params["language_code"]
        vs = {k: req.params[k] for k in ("stability", "similarity_boost", "style") if k in req.params}
        if vs:
            body["voice_settings"] = vs
        if "seed" in req.params:
            body["seed"] = req.params["seed"]
        r = http.call("POST", f"{API}/text-to-speech/{req.params['voice_id']}?output_format=mp3_44100_192",
                      json=body, headers=self._h())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        units, cost = self.estimate(req)
        return Result([out], units, cost, {"request_id": r.headers.get("request-id")})


class ElevenMusic(_ElMixin, MusicProvider):
    """Instrumental only: prompts always carry 'instrumental, no vocals'; force_instrumental set."""

    def run(self, req: Request, out: Path) -> Result:
        body = {"prompt": req.prompt, "music_length_ms": int(req.params.get("duration_s", 60) * 1000),
                "model_id": self.model, "force_instrumental": True}
        r = http.call("POST", f"{API}/music?output_format=mp3_44100_192", json=body, headers=self._h())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        units, cost = self.estimate(req)
        return Result([out], units, cost, {"request_id": r.headers.get("request-id")})


class ElevenSfx(_ElMixin, SfxProvider):
    def run(self, req: Request, out: Path) -> Result:
        body = {"text": req.prompt, "model_id": self.model,
                "duration_seconds": req.params.get("duration_s"),
                "prompt_influence": req.params.get("prompt_influence", 0.5),
                "loop": bool(req.params.get("loop", False))}
        body = {k: v for k, v in body.items() if v is not None}
        r = http.call("POST", f"{API}/sound-generation?output_format=mp3_44100_192", json=body, headers=self._h())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        units, cost = self.estimate(req)
        return Result([out], units, cost, {"request_id": r.headers.get("request-id")})
