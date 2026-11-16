"""Google Gemini API direct adapter for image generation (Nano Banana Pro / Gemini 3 Pro Image).

Alternative to the fal route: same model, slightly cheaper, and the Batch API
halves the price for non-urgent jobs (bible sheets, keyframe candidates).
"""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

from . import http
from .base import ImageProvider, Request, Result

API = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiImage(ImageProvider):
    def required_keys(self):
        return ["GEMINI_API_KEY"]

    def run(self, req: Request, out: Path) -> Result:
        parts = [{"text": req.prompt}]
        for r in req.refs:
            parts.append({"inline_data": {"mime_type": mimetypes.guess_type(str(r))[0] or "image/png",
                                          "data": base64.b64encode(Path(r).read_bytes()).decode()}})
        body = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": req.params.get("aspect", "16:9"),
                                "imageSize": req.params.get("resolution", "2K")},
            },
        }
        r = http.call("POST", f"{API}/{self.model}:generateContent", json=body,
                      headers={"x-goog-api-key": self.p.env["GEMINI_API_KEY"]})
        data = r.json()
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                blob = part.get("inlineData") or part.get("inline_data")
                if blob:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(base64.b64decode(blob["data"]))
                    units, cost = self.estimate(req)
                    return Result([out], units, cost, {})
        raise RuntimeError(f"no image in response: {str(data)[:400]}")
