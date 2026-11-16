"""Final assembly: picture + mix -> deliverables.

  python -m anim.assemble            # film mp4 (+ -23 LUFS broadcast), srt, poster, thumbnail, stills, trailer
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import skia

from . import core as K
from .timeline import FILM_DIR, FPS, W, H, Ctx, build_film

FINAL = FILM_DIR / "edit" / "final"
import yaml as _yaml
TITLE = _yaml.safe_load((FILM_DIR / "config.yaml").read_text())["title"].replace(" ", "_")


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


def write_srt(tl: dict, out: Path):
    lines = []
    for i, d in enumerate(sorted(tl["dialogue"], key=lambda d: d["start"]), 1):
        speaker = {"meher": "MEHER", "kabir": "KABIR", "nani": "NANI", "amma": "MISHRI AMMA",
                   "chutney": "CHUTNEY"}.get(d["char"], "")
        text = d["text"]
        lines.append(f"{i}\n{ts(d['start'])} --> {ts(d['start'] + d['duration'] + 0.25)}\n{text}\n")
    out.write_text("\n".join(lines), encoding="utf-8")


def frame_png(shots, sid: str, t: float, out: Path, scale=1.0, overlay=None):
    from .render import draw_frame
    idx = next(i for i, s in enumerate(shots) if s.id == sid)
    w, h = int(W * scale), int(H * scale)
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    draw_frame(cv, shots, idx, int(t * FPS), scale)
    if overlay:
        overlay(cv, w, h)
    surf.makeImageSnapshot().save(str(out))
    return out


def poster(shots, sid, t, out: Path):
    """2:3 poster: render the key frame at 2x, crop a vertical slice, add title lettering."""
    from PIL import Image, ImageDraw, ImageFont
    tmp = FINAL / "_poster_src.png"
    frame_png(shots, sid, t, tmp, scale=2.0)
    im = Image.open(tmp).convert("RGB")
    Wd, Hd = im.size
    pw = int(Hd * 2 / 3)
    cx = getattr(poster, "center_x", 0.5)
    x0 = int(min(max(0, Wd * cx - pw / 2), Wd - pw))
    im = im.crop((x0, 0, x0 + pw, Hd))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf", int(pw * 0.085))
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", int(pw * 0.034))
    except OSError:
        f = f2 = ImageFont.load_default()
    for i, (txt, ff, y) in enumerate([("The Midnight", f, 0.06), ("Sweet Shop", f, 0.15)]):
        w = d.textlength(txt, font=ff)
        d.text(((pw - w) / 2 + 5, Hd * y + 6), txt, font=ff, fill=(10, 6, 20))
        d.text(((pw - w) / 2, Hd * y), txt, font=ff, fill=(255, 226, 160))
    tag = "Pay with one true kindness."
    w = d.textlength(tag, font=f2)
    d.text(((pw - w) / 2, Hd * 0.92), tag, font=f2, fill=(240, 220, 190))
    im.save(out)
    tmp.unlink(missing_ok=True)


def trailer(film: Path, picks: list[tuple[float, float]], out: Path):
    """picks: [(start_s, dur_s), ...] from the finished film; joined with short dissolves."""
    parts = []
    for i, (a, d) in enumerate(picks):
        p = FINAL / f"_tr_{i:02d}.mp4"
        run("-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", str(film), "-c:v", "libx264", "-crf", "18",
            "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-r", str(FPS), str(p))
        parts.append((p, d))
    # xfade chain
    inputs, fc, last_v, last_a, acc = [], [], "0:v", "0:a", parts[0][1]
    for p, _ in parts:
        inputs += ["-i", str(p)]
    xd = 0.4
    for i in range(1, len(parts)):
        off = acc - xd
        fc.append(f"[{last_v}][{i}:v]xfade=transition=fade:duration={xd}:offset={off:.3f}[v{i}]")
        fc.append(f"[{last_a}][{i}:a]acrossfade=d={xd}[a{i}]")
        last_v, last_a = f"v{i}", f"a{i}"
        acc = off + parts[i][1]
    run(*inputs, "-filter_complex", ";".join(fc), "-map", f"[{last_v}]", "-map", f"[{last_a}]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", str(out))
    for p, _ in parts:
        p.unlink(missing_ok=True)


def main():
    FINAL.mkdir(parents=True, exist_ok=True)
    shots = build_film(write=False)
    tl = json.loads((FILM_DIR / "edit" / "timeline.json").read_text())
    pic = FILM_DIR / "edit" / "rough" / "picture.mp4"
    mix16 = FILM_DIR / "edit" / "audio" / "mix_16lufs.wav"
    mix23 = FILM_DIR / "edit" / "audio" / "mix_23lufs.wav"
    film = FINAL / f"{TITLE}_1080p.mp4"
    run("-i", str(pic), "-i", str(mix16), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19",
        "-preset", "slow", "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(film))
    run("-i", str(film), "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-crf", "22", "-preset", "slow",
        "-tune", "animation", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(FINAL / f"{TITLE}_720p_share.mp4"))
    if mix23.exists():
        run("-i", str(film), "-i", str(mix23), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
            str(FINAL / f"{TITLE}_1080p_broadcast_-23LUFS.mp4"))
    write_srt(tl, FINAL / f"{TITLE}_en.srt")
    print("film:", film)
    return film


if __name__ == "__main__":
    main()
