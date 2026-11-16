"""fal.ai adapter: one key reaches Nano Banana Pro, Kling 3.0, Veo 3.1, Seedream, FLUX, sync lipsync.

Uses fal's queue REST API. Parameter names differ per model, so each model's
argument mapping lives in PARAM_MAPS (and can be overridden in config.yaml with
`param_map:`). `python -m film doctor` checks these names against fal's live
OpenAPI schema once a key is present.
"""
from __future__ import annotations

import time
from pathlib import Path

from . import http
from .base import (ContentRejected, ImageProvider, LipSyncProvider, Request, Result,
                   TransientError, VideoProvider)

QUEUE = "https://queue.fal.run"

# logical field -> fal argument name, per endpoint family
PARAM_MAPS = {
    "nano-banana": {"refs": "image_urls", "aspect": "aspect_ratio", "num_images": "num_images",
                    "resolution": "resolution"},
    "seedream": {"refs": "image_urls", "num_images": "num_images", "size": "image_size"},
    "flux": {"refs": "image_urls", "num_images": "num_images"},
    "kling-video": {"first_frame": "start_image_url", "last_frame": "end_image_url",
                    "duration_s": "duration", "negative": "negative_prompt", "audio": "generate_audio"},
    "veo3": {"first_frame": "image_url", "last_frame": "last_frame_url", "duration_s": "duration",
             "negative": "negative_prompt", "audio": "generate_audio", "resolution": "resolution"},
    "sync-lipsync": {"video": "video_url", "audio": "audio_url"},
}


def _family(model: str) -> str:
    for k in PARAM_MAPS:
        if k in model:
            return k
    return ""


class _FalMixin:
    def required_keys(self):
        return ["FAL_KEY"]

    def _headers(self):
        return {"Authorization": f"Key {self.p.env['FAL_KEY']}", "Content-Type": "application/json"}

    def _pmap(self) -> dict:
        m = dict(PARAM_MAPS.get(_family(self.model), {}))
        m.update(self.cfg.get("param_map", {}))
        return m

    def _submit_and_wait(self, args: dict, poll_s: float = 4.0, max_wait_s: float = 1800) -> dict:
        r = http.call("POST", f"{QUEUE}/{self.model}", json=args, headers=self._headers()).json()
        status_url, response_url = r["status_url"], r["response_url"]
        t0 = time.time()
        while time.time() - t0 < max_wait_s:
            s = http.call("GET", status_url, headers=self._headers()).json()
            st = s.get("status")
            if st == "COMPLETED":
                resp = http.call("GET", response_url, headers=self._headers())
                body = resp.json()
                if isinstance(body, dict) and body.get("detail"):
                    detail = str(body["detail"])
                    if any(w in detail.lower() for w in ("safety", "policy", "nsfw", "content")):
                        raise ContentRejected(detail[:400])
                    raise RuntimeError(detail[:400])
                body["_request_id"] = r.get("request_id")
                return body
            if st in ("FAILED", "ERROR"):
                raise RuntimeError(str(s)[:400])
            time.sleep(poll_s)
        raise TransientError(f"fal job timed out after {max_wait_s}s")


class FalImage(_FalMixin, ImageProvider):
    def run(self, req: Request, out: Path) -> Result:
        pm = self._pmap()
        args = {"prompt": req.prompt}
        if req.refs:
            args[pm.get("refs", "image_urls")] = [http.data_uri(r) for r in req.refs]
        for k in ("aspect", "num_images", "resolution", "size"):
            if k in req.params and k in pm:
                args[pm[k]] = req.params[k]
        if "seed" in req.params:
            args["seed"] = req.params["seed"]
        body = self._submit_and_wait(args)
        files = []
        for i, img in enumerate(body.get("images", [])):
            dest = out if i == 0 else out.with_name(f"{out.stem}_{i}{out.suffix}")
            files.append(http.download(img["url"], dest))
        if not files:
            raise RuntimeError(f"no images returned: {str(body)[:300]}")
        units, cost = self.estimate(req)
        return Result(files, units, cost, {"seed": body.get("seed"), "request_id": body.get("_request_id")})


class FalVideo(_FalMixin, VideoProvider):
    def run(self, req: Request, out: Path) -> Result:
        pm = self._pmap()
        args = {"prompt": req.prompt}
        if req.negative and "negative" in pm:
            args[pm["negative"]] = req.negative
        if req.refs:
            args[pm["first_frame"]] = http.data_uri(req.refs[0])
        if req.params.get("last_frame") and "last_frame" in pm:
            args[pm["last_frame"]] = http.data_uri(Path(req.params["last_frame"]))
        if "duration_s" in req.params:
            d = req.params["duration_s"]
            args[pm["duration_s"]] = str(d) if "veo3" not in self.model else f"{int(d)}s"
        if "audio" in pm:
            args[pm["audio"]] = False   # silent: dialogue, music and SFX are produced separately
        if "resolution" in pm and "resolution" in req.params:
            args[pm["resolution"]] = req.params["resolution"]
        if "seed" in req.params:
            args["seed"] = req.params["seed"]
        body = self._submit_and_wait(args)
        vid = body.get("video") or {}
        if not vid.get("url"):
            raise RuntimeError(f"no video returned: {str(body)[:300]}")
        units, cost = self.estimate(req)
        return Result([http.download(vid["url"], out)], units, cost,
                      {"seed": body.get("seed"), "request_id": body.get("_request_id")})


class FalLipSync(_FalMixin, LipSyncProvider):
    def run(self, req: Request, out: Path) -> Result:
        pm = self._pmap()
        video, audio = req.refs[0], req.refs[1]
        body = self._submit_and_wait({pm["video"]: http.data_uri(video), pm["audio"]: http.data_uri(audio)})
        units, cost = self.estimate(req)
        return Result([http.download(body["video"]["url"], out)], units, cost,
                      {"request_id": body.get("_request_id")})
