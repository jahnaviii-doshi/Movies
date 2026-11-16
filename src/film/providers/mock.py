"""Offline placeholder provider: lets every pipeline stage run end to end with zero spend.

Images: a card with the prompt text. Video: the first frame held with a slow zoom.
Audio: silence of the requested length. Used for tests and for timing animatics
before any keys exist.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

from .base import (ImageProvider, LipSyncProvider, MusicProvider, QCProvider, Request, Result,
                   SfxProvider, VideoProvider, VoiceProvider)


def _card(text: str, out: Path, size=(1920, 1080)) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", size, (24, 28, 52))
    d = ImageDraw.Draw(im)
    d.multiline_text((60, 60), "\n".join(textwrap.wrap(text, 90)[:30]), fill=(235, 220, 190), spacing=8)
    im.save(out)
    return out


def _silence(out: Path, seconds: float) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "anullsrc=r=48000:cl=stereo", "-t", f"{seconds:.2f}", str(out)], check=True)
    return out


class MockImage(ImageProvider):
    def run(self, req: Request, out: Path) -> Result:
        return Result([_card(req.prompt, out)], 1, 0.0, {"mock": True})


class MockVideo(VideoProvider):
    def run(self, req: Request, out: Path) -> Result:
        d = float(req.params.get("duration_s", 5))
        src = req.refs[0] if req.refs else _card(req.prompt, out.with_suffix(".png"))
        out.parent.mkdir(parents=True, exist_ok=True)
        fps = self.p.config.get("fps", 24)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(src), "-t", f"{d}",
            "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0008,1.08)':d={int(d*fps)}:s=1920x1080:fps={fps}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True)
        return Result([out], d, 0.0, {"mock": True})


class MockVoice(VoiceProvider):
    def run(self, req: Request, out: Path) -> Result:
        return Result([_silence(out, max(1.0, len(req.prompt) / 14))], 0, 0.0, {"mock": True})


class MockMusic(MusicProvider):
    def run(self, req: Request, out: Path) -> Result:
        return Result([_silence(out, req.params.get("duration_s", 30))], 0, 0.0, {"mock": True})


class MockSfx(SfxProvider):
    def run(self, req: Request, out: Path) -> Result:
        return Result([_silence(out, req.params.get("duration_s", 3))], 0, 0.0, {"mock": True})


class MockLipSync(LipSyncProvider):
    def run(self, req: Request, out: Path) -> Result:
        out.write_bytes(Path(req.refs[0]).read_bytes())
        return Result([out], 0, 0.0, {"mock": True})


class SessionQC(QCProvider):
    """QC scored by Claude Code in the working session (frames + reference sheets are
    rendered to a contact sheet and reviewed). No API spend; produces no file by itself."""

    def run(self, req: Request, out: Path) -> Result:
        raise NotImplementedError("session QC is interactive: use `python -m film qc` (Phase 6)")
