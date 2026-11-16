"""Render shots to video segments (parallel), contact sheets, and the assembled picture.

  python -m anim.render                      # all scenes, full quality, cached
  python -m anim.render --scenes sc01 sc03   # some scenes
  python -m anim.render --stills sc02        # contact sheet of 3 frames per shot (fast review)
  python -m anim.render --draft              # half resolution
  python -m anim.render --concat             # join segments -> edit/rough/picture.mp4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import skia

from . import core as K
from .timeline import FILM, FILM_DIR, FPS, H, W, Ctx, build_film, SCENES, SCENE_PKG

SRC = Path(__file__).resolve().parent
SEG_DIR = FILM_DIR / "edit" / "segments"
STILL_DIR = FILM_DIR / "edit" / "stills_review"


def _hash_files(paths) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def engine_hash() -> str:
    files = [SRC / "core.py", SRC / "fx.py", SRC / "timeline.py"] + list((SRC / "rig").glob("*.py")) + \
        list((SRC / "sets").glob("*.py"))
    fdir = SRC / "films" / FILM
    if fdir.exists():   # the film's own rigs/sets/helpers (not its scenes)
        files += [p for p in fdir.rglob("*.py") if "scenes" not in p.parts]
    return _hash_files(files)


def scene_hash(scene: int) -> str:
    import importlib
    name = f"sc{scene:02d}" if scene != 99 else "credits"
    mod = importlib.import_module(f"{SCENE_PKG}.{name}")
    sdir = Path(mod.__file__).parent
    return _hash_files([Path(mod.__file__)] + sorted(sdir.glob("_util*.py")))


# ------------------------------------------------------------------ frame drawing
def draw_frame(cv: skia.Canvas, shots, i: int, frame: int, scale=1.0):
    s = shots[i]
    t = frame / FPS
    K.STYLE["seed"] = int((s.start + t) * K.STYLE["boil_fps"])
    cv.save()
    cv.scale(scale, scale)
    cv.clear(K.C("#000000"))
    s.draw(cv, Ctx(s, frame))
    # incoming dissolve: blend the previous shot continuing past its end
    if s.transition == "dissolve" and i > 0 and t < s.trans_dur:
        prev = shots[i - 1]
        k = K.smooth(t / s.trans_dur)
        rec = skia.PictureRecorder()
        rc = rec.beginRecording(skia.Rect.MakeWH(W, H))
        rc.clear(K.C("#000000"))
        prev.draw(rc, Ctx(prev, int(round(prev.duration * FPS)) + frame))
        pic = rec.finishRecordingAsPicture()
        p = skia.Paint(); p.setAlphaf(1 - k)
        cv.saveLayer(None, p)
        cv.drawPicture(pic)
        cv.restore()
    K.finish(cv, t, grain=0.07, vignette=0.38)
    # dips
    nxt = shots[i + 1] if i + 1 < len(shots) else None
    for tr, col in (("fade_black", "#000000"), ("fade_white", "#fff6e6")):
        if s.transition == tr and t < s.trans_dur / 2 + 1e-6:
            from .fx import fade
            fade(cv, col, 1 - K.smooth(t / (s.trans_dur / 2)))
        if nxt is not None and nxt.transition == tr and t > s.duration - nxt.trans_dur / 2:
            from .fx import fade
            fade(cv, col, K.smooth((t - (s.duration - nxt.trans_dur / 2)) / (nxt.trans_dur / 2)))
    if i == len(shots) - 1 and getattr(s, "fade_out", True) and t > s.duration - 1.0:
        from .fx import fade
        fade(cv, "#000000", K.smooth(t - (s.duration - 1.0)))
    cv.restore()


def _shots_cached():
    global _SHOTS
    try:
        return _SHOTS
    except NameError:
        _SHOTS = build_film(write=False)
        return _SHOTS


def render_segment(args):
    idx, draft = args
    shots = _shots_cached()
    s = shots[idx]
    scale = 0.5 if draft else 1.0
    w, h = int(W * scale), int(H * scale)
    out = SEG_DIR / ("draft" if draft else "full") / f"{s.id}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    prev_tr = shots[idx].transition
    next_tr = shots[idx + 1].transition if idx + 1 < len(shots) else ""
    key = {"engine": engine_hash(), "scene": scene_hash(s.scene), "id": s.id, "dur": s.duration,
           "prev": prev_tr, "next": next_tr, "draft": draft,
           "prev_id": shots[idx - 1].id if idx else "", "is_last": idx == len(shots) - 1}
    meta = out.with_suffix(".json")
    if out.exists() and meta.exists() and json.loads(meta.read_text()) == key:
        return s.id, "cached", 0.0
    t0 = time.time()
    n = int(round(s.duration * FPS))
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium" if not draft else "veryfast",
         "-crf", "17" if not draft else "23", "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)],
        stdin=subprocess.PIPE)
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    for f in range(n):
        draw_frame(cv, shots, idx, f, scale)
        arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        proc.stdin.write(arr.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {s.id}")
    meta.write_text(json.dumps(key))
    return s.id, "rendered", time.time() - t0


def render(scenes=None, draft=False, jobs=4):
    shots = build_film()   # writes timeline.json, synthesizes voices
    idxs = [i for i, s in enumerate(shots)
            if not scenes or (f"sc{s.scene:02d}" in scenes) or (s.scene == 99 and "credits" in scenes)]
    total = sum(shots[i].duration for i in idxs)
    print(f"rendering {len(idxs)} shots, {total/60:.1f} min of picture, jobs={jobs}, draft={draft}", flush=True)
    t0 = time.time()
    done = 0
    with mp.get_context("fork").Pool(jobs) as pool:
        for sid, status, dt in pool.imap_unordered(render_segment, [(i, draft) for i in idxs]):
            done += 1
            print(f"  [{done}/{len(idxs)}] {sid} {status} {dt:.1f}s", flush=True)
    print(f"done in {(time.time()-t0)/60:.1f} min")
    return shots


def concat(draft=False):
    shots = build_film(write=False)
    d = SEG_DIR / ("draft" if draft else "full")
    lst = d / "list.txt"
    lst.write_text("".join(f"file '{d / (s.id + '.mp4')}'\n" for s in shots))
    out = FILM_DIR / "edit" / "rough" / ("picture_draft.mp4" if draft else "picture.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out)], check=True)
    print(out)
    return out


def stills(scenes=None, per_shot=3, cols=6, thumb=400):
    from PIL import Image, ImageDraw
    shots = build_film(write=False)
    STILL_DIR.mkdir(parents=True, exist_ok=True)
    sel = [i for i, s in enumerate(shots) if not scenes or f"sc{s.scene:02d}" in scenes
           or (s.scene == 99 and "credits" in scenes)]
    tiles = []
    surf = skia.Surface(W // 2, H // 2)
    cv = surf.getCanvas()
    for i in sel:
        s = shots[i]
        for k in range(per_shot):
            u = (k + 0.5) / per_shot
            f = int(u * s.duration * FPS)
            draw_frame(cv, shots, i, f, 0.5)
            arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
            im = Image.fromarray(arr[:, :, :3]).resize((thumb, int(thumb * 9 / 16)))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, thumb, 18], fill=(0, 0, 0))
            d.text((4, 3), f"{s.id} t={f/FPS:.1f}/{s.duration:.1f}", fill=(255, 230, 160))
            tiles.append(im)
    rows = (len(tiles) + cols - 1) // cols
    th = int(thumb * 9 / 16)
    sheet = Image.new("RGB", (cols * thumb, rows * th), (20, 20, 20))
    for j, im in enumerate(tiles):
        sheet.paste(im, ((j % cols) * thumb, (j // cols) * th))
    name = "_".join(scenes) if scenes else "all"
    out = STILL_DIR / f"sheet_{name}.png"
    sheet.save(out)
    print(out, f"{len(sel)} shots, {sum(shots[i].duration for i in sel):.1f}s")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", nargs="*")
    ap.add_argument("--stills", nargs="*")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--concat", action="store_true")
    a = ap.parse_args(argv)
    if a.stills is not None:
        stills(a.stills or None)
    elif a.concat:
        concat(a.draft)
    else:
        render(a.scenes, a.draft, a.jobs)
        concat(a.draft) if not a.scenes else None


if __name__ == "__main__":
    sys.exit(main())
