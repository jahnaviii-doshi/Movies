"""Film mixer: timeline.json -> stems + mix_raw + loudness-normalised masters.

python -m anim.audio.mix [--timeline PATH] [--out DIR]

Outputs (DIR, default films/midnight_sweet_shop/edit/audio/):
  dialogue.wav, music.wav, sfx.wav     stems (48 kHz float32 stereo)
  mix_raw.wav                          sum, before loudness normalisation
  mix_16lufs.wav                       -16 LUFS integrated, TP <= -1.5 dBTP (streaming)
  mix_23lufs.wav                       -23 LUFS integrated, TP <= -2 dBTP (broadcast)
Rendered cues and sfx are cached in DIR/cache keyed by inputs + engine source hash.
Stems are memory-mapped so a 20-minute film does not need gigabytes of RAM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from . import synth as S

SR = S.SR
ROOT = Path(__file__).resolve().parents[3]
FILM = ROOT / "films" / __import__("os").environ.get("FILM", "midnight_sweet_shop")
HERE = Path(__file__).resolve().parent

DIALOGUE_GAIN_DB = -3.0
MUSIC_GAIN_DB = -5.0
SFX_GAIN_DB = -2.0
DUCK_MUSIC_DB = -9.0
DUCK_SFX_DB = -3.0
ATTACK_S, RELEASE_S = 0.15, 0.5
CHAR_PAN = {"meher": -0.08, "kabir": 0.1, "nani": -0.04, "amma": 0.05, "chutney": 0.0, "kid1": -0.35, "kid2": 0.35}


def db(x):
    return 10 ** (x / 20)


def _engine_hash(files):
    h = hashlib.sha256()
    for f in files:
        h.update((HERE / f).read_bytes())
    # the current film's own audio modules (cues/sfx/motifs), if any
    fdir = HERE.parent / "films" / FILM.name
    for f in sorted(fdir.glob("*.py")) if fdir.exists() else []:
        if f.stem in ("cues", "motifs", "sfx", "synth_extra"):
            h.update(f.read_bytes())
    return h.hexdigest()[:10]


def _cached(cache: Path, kind: str, key: dict, render):
    cache.mkdir(parents=True, exist_ok=True)
    k = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]
    f = cache / f"{kind}_{k}.npy"
    if f.exists():
        return np.load(f, mmap_mode="r")
    x = np.ascontiguousarray(render(), dtype=np.float32)
    np.save(f, x)
    return x


def _add(stem: np.ndarray, start_s: float, x: np.ndarray, gain: float = 1.0):
    i = int(round(start_s * SR))
    if i >= len(stem) or len(x) == 0:
        return
    if i < 0:
        x = x[-i:]
        i = 0
    m = min(len(x), len(stem) - i)
    stem[i: i + m] += gain * np.asarray(x[:m], dtype=np.float32)


def duck_curve(intervals, total_s, rate=1000):
    """Smoothed 0..1 'dialogue active' envelope at `rate` Hz (asymmetric attack/release)."""
    n = int(total_s * rate) + 2
    mask = np.zeros(n, np.float32)
    for a, b in intervals:
        mask[int(max(0, a - 0.08) * rate): int((b + 0.12) * rate)] = 1.0
    env = np.zeros(n, np.float32)
    ca = 1 - np.exp(-1 / (ATTACK_S * rate))
    cr = 1 - np.exp(-1 / (RELEASE_S * rate))
    # vectorised enough: iterate in python over 1 kHz samples (1.2 M for 20 min, ~0.5 s)
    e = 0.0
    for i in range(n):
        target = mask[i]
        e += (target - e) * (ca if target > e else cr)
        env[i] = e
    return env


def _measure(src: Path, I: float, TP: float, LRA: float) -> dict:
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
                         f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    txt = p1.stderr
    return json.loads(txt[txt.rindex("{"): txt.rindex("}") + 1])


def _loudnorm(src: Path, dst: Path, I: float, TP: float, LRA: float = 11.0) -> dict:
    js = _measure(src, I, TP, LRA)
    gain = I - float(js["input_i"])
    if float(js["input_tp"]) + gain > TP - 0.3:
        # linear normalisation would breach the true-peak ceiling: pre-gain + transparent
        # lookahead limiting first, so the final pass stays linear (no pumping)
        lim = dst.with_name(dst.stem + "_lim.wav")
        subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(src), "-af",
                        f"volume={gain:.2f}dB,alimiter=limit={db(TP - 1.0):.4f}:attack=5:release=80:level=false",
                        "-c:a", "pcm_f32le", str(lim)], capture_output=True, check=True)
        src = lim
        js = _measure(src, I, TP, LRA)
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:"
          f"linear=true:print_format=json")
    p2 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(src), "-af", af, "-ar", str(SR),
                         "-c:a", "pcm_s24le", str(dst)], capture_output=True, text=True)
    txt = p2.stderr
    out = json.loads(txt[txt.rindex("{"): txt.rindex("}") + 1])
    lim = dst.with_name(dst.stem + "_lim.wav")
    if lim.exists():
        lim.unlink()
    return {"input_i": js["input_i"], "output_i": out["output_i"], "output_tp": out["output_tp"],
            "normalization_type": out.get("normalization_type")}


def mix(timeline_path: Path, out_dir: Path, verbose=True) -> dict:
    from .cues import render_cue
    from .sfx import sfx as render_sfx

    t0 = time.time()
    tl = json.loads(Path(timeline_path).read_text())
    D = float(tl["duration"])
    N = int(round(D * SR))
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / "cache"
    eng_music = _engine_hash(["synth.py", "motifs.py", "cues.py"])
    eng_sfx = _engine_hash(["synth.py", "motifs.py", "sfx.py"])

    def stem_file(name):
        return np.lib.format.open_memmap(out_dir / f".{name}.npy", mode="w+", dtype=np.float32, shape=(N, 2))

    dlg, mus, fx = stem_file("dialogue"), stem_file("music"), stem_file("sfx")

    # ---- dialogue
    intervals = []
    for d in tl.get("dialogue", []):
        x, sr = sf.read(d["wav"], dtype="float32", always_2d=False)
        if x.ndim == 2:
            x = x.mean(1)
        if sr != SR:
            raise ValueError(f"{d['wav']}: expected {SR} Hz, got {sr}")
        _add(dlg, d["start"], S.pan(x.astype(np.float64), CHAR_PAN.get(d.get("char"), 0.0)), db(DIALOGUE_GAIN_DB))
        intervals.append((d["start"], d["start"] + len(x) / SR))
    if verbose:
        print(f"  dialogue: {len(intervals)} lines")

    # ---- music
    cues = sorted(tl.get("music", []), key=lambda c: c["start"])
    for i, c in enumerate(cues):
        start = float(c["start"])
        end = float(cues[i + 1]["start"]) if i + 1 < len(cues) else D
        dur = end - start
        if not c["cue"] or dur <= 0.05:
            continue
        # let each cue ring out under the next one for a natural tail (except into silence handled by fades)
        hits = [round(h - start, 3) for h in c.get("hits", []) if start <= h <= end]
        key = {"cue": c["cue"], "dur": round(dur, 3), "hits": hits, "eng": eng_music}
        x = _cached(cache, "cue", key, lambda: render_cue(c["cue"], dur, hits))
        _add(mus, start, x, db(MUSIC_GAIN_DB))
        if verbose:
            print(f"  music: {c['cue']:<18} {start:7.2f}s  +{dur:6.2f}s")

    # ---- sfx
    for e in tl.get("sfx", []):
        params = e.get("params") or {}
        key = {"name": e["name"], "dur": e.get("dur"), "params": params, "eng": eng_sfx}
        x = _cached(cache, "sfx", key, lambda: render_sfx(e["name"], e.get("dur"), **params))
        _add(fx, e["start"], x, db(SFX_GAIN_DB + float(e.get("gain_db", 0.0))))
    if verbose:
        print(f"  sfx: {len(tl.get('sfx', []))} events")

    # ---- ducking + sum, in chunks
    env = duck_curve(intervals, D)
    raw_path = out_dir / "mix_raw.wav"
    peak = 0.0
    chunk = SR * 10
    for a in range(0, N, chunk):
        b = min(N, a + chunk)
        tt = np.arange(a, b) / SR
        e = np.interp(tt, np.arange(len(env)) / 1000.0, env).astype(np.float32)[:, None]
        mus[a:b] *= 1 - (1 - db(DUCK_MUSIC_DB)) * e
        fx[a:b] *= 1 - (1 - db(DUCK_SFX_DB)) * e
        peak = max(peak, float(np.max(np.abs(dlg[a:b] + mus[a:b] + fx[a:b]))))
    trim = 0.98 / peak if peak > 0.98 else 1.0
    with sf.SoundFile(raw_path, "w", SR, 2, subtype="FLOAT") as fh:
        for a in range(0, N, chunk):
            b = min(N, a + chunk)
            y = (dlg[a:b] + mus[a:b] + fx[a:b]) * trim
            fh.write(np.nan_to_num(y))
    for name, arr in (("dialogue", dlg), ("music", mus), ("sfx", fx)):
        with sf.SoundFile(out_dir / f"{name}.wav", "w", SR, 2, subtype="FLOAT") as fh:
            for a in range(0, N, chunk):
                fh.write(np.nan_to_num(arr[a: min(N, a + chunk)] * trim))
        arr.flush()
    del dlg, mus, fx
    for name in ("dialogue", "music", "sfx"):
        try:
            os.remove(out_dir / f".{name}.npy")
        except OSError:
            pass

    r16 = _loudnorm(raw_path, out_dir / "mix_16lufs.wav", -16.0, -1.5)
    r23 = _loudnorm(raw_path, out_dir / "mix_23lufs.wav", -23.0, -2.0)
    res = {"duration_s": D, "raw_peak": peak, "trim": trim, "lufs16": r16, "lufs23": r23,
           "seconds": round(time.time() - t0, 1)}
    (out_dir / "mix_report.json").write_text(json.dumps(res, indent=2))
    if verbose:
        print(json.dumps(res, indent=2))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m anim.audio.mix")
    ap.add_argument("--timeline", default=str(FILM / "edit" / "timeline.json"))
    ap.add_argument("--out", default=str(FILM / "edit" / "audio"))
    a = ap.parse_args(argv)
    mix(Path(a.timeline), Path(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
