"""Character voices: local Kokoro-82M (Apache-2.0) TTS, run offline in the container.

Each character = base voice (or blend) + pitch shift + pace + colour. Pitch is raised by
generating slower then resampling faster (formants rise too: reads younger).
Outputs per line: 48 kHz mono wav + a per-frame (24 fps) mouth-openness envelope.
Cached by hash of (character config, text).
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"
SR = 48000
FPS = 24

CAST = {
    #            voices (blend weights)                 semitones speed  vibrato(Hz,depth st) growl
    "meher":   dict(voices={"hf_beta": 1.0},                    st=3.5, speed=0.92, vib=None, growl=0.0),
    "kabir":   dict(voices={"hm_psi": 0.7, "hf_alpha": 0.3},    st=4.0, speed=1.02, vib=None, growl=0.0),
    "nani":    dict(voices={"hf_alpha": 1.0},                   st=-1.0, speed=0.82, vib=(4.5, 0.10), growl=0.0),
    "amma":    dict(voices={"hf_beta": 0.6, "bf_isabella": 0.4}, st=2.0, speed=0.86, vib=(6.0, 0.18), growl=0.0),
    "chutney": dict(voices={"hm_omega": 1.0},                   st=-2.5, speed=0.88, vib=None, growl=0.35),
    "kid1":    dict(voices={"af_nova": 1.0},                    st=5.0, speed=1.05, vib=None, growl=0.0),
    "kid2":    dict(voices={"am_puck": 0.5, "af_sky": 0.5},     st=5.5, speed=1.08, vib=None, growl=0.0),
}


@lru_cache(maxsize=1)
def _kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))


def _style(voices: dict):
    k = _kokoro()
    style = None
    for name, w in voices.items():
        s = k.get_voice_style(name) * w
        style = s if style is None else style + s
    return style


def _vibrato(x: np.ndarray, rate: float, depth_st: float) -> np.ndarray:
    n = np.arange(len(x))
    # variable delay line: pitch deviation ~ derivative of delay
    max_delay = (2 ** (depth_st / 12) - 1) * SR / (2 * np.pi * rate)
    d = max_delay * (1 + np.sin(2 * np.pi * rate * n / SR))
    idx = np.clip(n - d, 0, len(x) - 1)
    i0 = np.floor(idx).astype(int); f = idx - i0
    i1 = np.minimum(i0 + 1, len(x) - 1)
    return x[i0] * (1 - f) + x[i1] * f


def _growl(x: np.ndarray, amt: float) -> np.ndarray:
    if amt <= 0:
        return x
    sos = butter(2, [70, 900], btype="band", fs=SR, output="sos")
    low = sosfilt(sos, x)
    rough = np.tanh(low * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * np.arange(len(x)) / SR))
    return x + amt * 0.25 * rough


def mouth_envelope(x: np.ndarray, fps: int = FPS) -> list[float]:
    hop = SR // fps
    n = int(np.ceil(len(x) / hop))
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    if rms.max() > 0:
        rms = rms / np.percentile(rms, 95)
    env = np.clip((rms - 0.12) / 0.7, 0, 1)
    # light smoothing, keep some chatter so mouths flap like speech
    env = np.convolve(env, [0.25, 0.5, 0.25], mode="same")
    return [round(float(v), 3) for v in env]


def synth(char: str, text: str, out_dir: Path) -> dict:
    cfg = CAST[char]
    key = hashlib.sha256(json.dumps([char, cfg, text], sort_keys=True).encode()).hexdigest()[:12]
    wav = out_dir / f"{char}_{key}.wav"
    meta_f = wav.with_suffix(".json")
    if meta_f.exists() and wav.exists():
        return json.loads(meta_f.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    k = _kokoro()
    r = 2 ** (cfg["st"] / 12)
    samples, sr = k.create(text, voice=_style(cfg["voices"]), speed=cfg["speed"] / r, lang="en-us")
    x = np.asarray(samples, dtype=np.float64)
    # resample to 48k and apply pitch ratio in one step: output length = len * 48000/sr / r
    frac = Fraction(48000 / (sr * r)).limit_denominator(200)
    x = resample_poly(x, frac.numerator, frac.denominator)
    if cfg["vib"]:
        x = _vibrato(x, *cfg["vib"])
    x = _growl(x, cfg["growl"])
    # trim silence, short fades
    thr = 0.01 * np.max(np.abs(x))
    nz = np.where(np.abs(x) > thr)[0]
    if len(nz):
        x = x[max(0, nz[0] - 480): nz[-1] + 2400]
    fade = np.linspace(0, 1, 240)
    x[:240] *= fade; x[-240:] *= fade[::-1]
    x = 0.89 * x / (np.max(np.abs(x)) + 1e-9)
    sf.write(wav, x.astype(np.float32), SR)
    meta = {"char": char, "text": text, "wav": str(wav), "duration": len(x) / SR, "mouth": mouth_envelope(x)}
    meta_f.write_text(json.dumps(meta))
    return meta
