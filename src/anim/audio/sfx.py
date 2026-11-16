"""Procedural sound effects: cartoon-warm, child-friendly. sfx(name, dur=None, **params) -> (N,2) float32.

Levels: spot effects peak ~ -6 dBFS; beds (names ending _bed, cicadas, wind_flight...) sit
around -30 dBFS RMS. The mixer applies each cue's gain_db on top.
"""
from __future__ import annotations

import warnings

import numpy as np

from . import synth as S
from .motifs import LULLABY, seq

SR = S.SR
ns, t_axis, noise = S.ns, S.t_axis, S.noise


def _rng(seed):
    return np.random.default_rng(seed)


def st(mono, p=0.0):
    return S.pan(mono, p)


def spot(x: np.ndarray, peak=0.5) -> np.ndarray:
    x = x if x.ndim == 2 else st(x)
    pk = np.max(np.abs(x)) + 1e-9
    return S.fade(x * (peak / pk), 0.002, 0.03)


def bed(x: np.ndarray, rms=0.03) -> np.ndarray:
    x = x if x.ndim == 2 else st(x)
    r = np.sqrt(np.mean(x ** 2)) + 1e-9
    x = x * (rms / r)
    pk = np.max(np.abs(x))
    if pk > 0.6:
        x *= 0.6 / pk
    return S.fade(x, 0.4, 0.6)


def space(x, wet=0.2, size=1.6, bright=0.5):
    x = x if x.ndim == 2 else st(x)
    return S.reverb(x, wet, size, bright)


def env_exp(n, tau):
    return np.exp(-t_axis(n) / tau)


def glide_tone(f0, f1, dur, harmonics=(1.0,), curve=1.0, vib=0.0, vib_rate=6.0):
    n = ns(dur)
    t = t_axis(n)
    u = (t / dur) ** curve
    fc = f0 * (f1 / f0) ** u
    if vib:
        fc = fc * (1 + vib * np.sin(2 * np.pi * vib_rate * t))
    return S.osc_additive(fc, list(harmonics), phase_jitter=False)


def metal(f, dur=1.5, vel=1.0, ratios=(1.0, 2.32, 4.25, 6.63, 9.38), decay=1.0, seed=0):
    """Brass/metal modal hit."""
    n = ns(dur)
    t = t_axis(n)
    g = _rng(seed)
    out = np.zeros(n)
    for i, r in enumerate(ratios):
        fk = f * r
        if fk > 16000:
            continue
        out += (1 / (1 + 0.6 * i)) * np.sin(2 * np.pi * fk * t + g.uniform(0, 6)) * np.exp(-t / (decay * dur * 0.45 / (1 + 0.5 * i)))
    out[: ns(0.003)] += S.hp(noise(ns(0.003), seed), 3000) * 0.4
    return vel * out


def wood(f=700, dur=0.12, seed=0):
    n = ns(dur)
    t = t_axis(n)
    out = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.6 * t) + 0.25 * np.sin(2 * np.pi * f * 4.1 * t))
    out *= np.exp(-t / 0.025)
    out += S.bp(noise(n, seed), 800, 4000) * np.exp(-t / 0.008) * 0.6
    return out


def thump(f=60, dur=0.5, seed=0):
    n = ns(dur)
    t = t_axis(n)
    fc = f * (1 + 1.5 * np.exp(-t / 0.03))
    return np.sin(np.cumsum(2 * np.pi * fc / SR)) * np.exp(-t / (dur * 0.3)) + 0.3 * S.lp(noise(n, seed), 400) * np.exp(-t / 0.04)


def noise_sweep(dur, f0, f1, q=0.6, seed=0, env=None):
    """Band-pass noise whose centre sweeps f0->f1 (processed in short blocks)."""
    n = ns(dur)
    x = noise(n, seed)
    out = np.zeros(n)
    blk = ns(0.02)
    for i in range(0, n, blk):
        u = i / max(1, n - 1)
        fc = f0 * (f1 / f0) ** u
        seg = x[max(0, i - blk): i + blk]
        y = S.bp(seg, fc * (1 - q / 2), fc * (1 + q / 2))
        out[i: i + blk] = y[-min(blk, n - i):] if len(y) >= blk else y[: n - i]
    if env is None:
        env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return out * env


# ------------------------------------------------------------------ ambiences
def crickets_bed(dur=10.0, density=1.0, seed=1):
    n = ns(dur)
    g = _rng(seed)
    out = np.zeros((n, 2))
    for c in range(int(5 * density)):
        f = g.uniform(3900, 5300)
        p = g.uniform(-0.8, 0.8)
        period = g.uniform(0.55, 1.1)
        pulses = int(g.integers(3, 6))
        rate = g.uniform(26, 38)
        level = g.uniform(0.3, 1.0)
        tt = g.uniform(0, period)
        chirp_len = pulses / rate
        m = ns(chirp_len)
        tm = t_axis(m)
        chirp = np.sin(2 * np.pi * f * tm) * (np.sin(np.pi * rate * tm) ** 2) * np.sin(np.pi * tm / chirp_len)
        mono_chirp = chirp * level
        sc = st(mono_chirp, p)
        while tt < dur - chirp_len:
            i = ns(tt)
            out[i: i + m] += sc * g.uniform(0.7, 1.0)
            tt += period * g.uniform(0.92, 1.08)
    out += st(S.bp(noise(n, seed + 5), 2500, 7000) * 0.02)
    return bed(space(out, 0.15, 1.2), 0.025)[:n]


def night_bed(dur=10.0, seed=2):
    n = ns(dur)
    x = crickets_bed(dur, 1.0, seed)[:n].astype(np.float64)
    br = S.lp(noise(n, seed + 1), 500) * (0.5 + 0.5 * S.lp(noise(n, seed + 2), 0.3) * 30)
    x += st(br * 0.012)
    g = _rng(seed)
    tt = g.uniform(3, 8)
    while tt < dur - 2:  # distant dogs
        b = dog_bark_mono(seed=int(tt * 10)) * 0.08
        b = S.lp(b, 1800)
        i = ns(tt)
        sb = space(st(b, g.uniform(-0.9, 0.9)), 0.6, 2.5, 0.3)
        m = min(len(sb), n - i)
        x[i: i + m] += sb[:m]
        tt += g.uniform(6, 14)
    return bed(x, 0.028)


def heat_cicadas(dur=10.0, seed=3):
    n = ns(dur)
    t = t_axis(n)
    x = S.bp(noise(n, seed), 4200, 7200) * (0.6 + 0.4 * np.sin(2 * np.pi * 48 * t) ** 2)
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.0 + 1.0)
    x2 = S.bp(noise(n, seed + 1), 5200, 8200) * (0.6 + 0.4 * np.sin(2 * np.pi * 61 * t) ** 2)
    return bed(np.stack([x * swell, x2 * swell[::-1]], 1), 0.022)


def coo(seed=0):
    g = _rng(seed)
    f = g.uniform(260, 320)
    a = glide_tone(f, f * 0.92, 0.35, (1, 0.3, 0.1), vib=0.03, vib_rate=18) * np.sin(np.pi * np.linspace(0, 1, ns(0.35)))
    b = glide_tone(f * 1.05, f * 0.85, 0.5, (1, 0.3, 0.1), vib=0.03, vib_rate=18) * np.sin(np.pi * np.linspace(0, 1, ns(0.5)))
    out = np.concatenate([a, np.zeros(ns(0.08)), b])
    return S.lp(out, 1200)


def day_bed(dur=10.0, seed=4):
    n = ns(dur)
    x = heat_cicadas(dur, seed).astype(np.float64) * 0.7
    traffic = S.lp(noise(n, seed + 3), 220) * (0.7 + 0.3 * S.lp(noise(n, seed + 4), 0.5) * 20)
    x += st(traffic * 0.05)
    g = _rng(seed)
    tt = g.uniform(1, 4)
    while tt < dur - 1.5:
        c = coo(int(tt * 7)) * 0.25
        i = ns(tt)
        sc = st(c, g.uniform(-0.7, 0.7))
        x[i: i + len(sc)] += sc[: n - i]
        tt += g.uniform(3.5, 8)
    tt = g.uniform(4, 9)
    while tt < dur - 1:  # far-off horn
        h = S.lp(glide_tone(410, 400, 0.4, (1, 0.6, 0.4, 0.3)), 1500) * 0.03
        i = ns(tt)
        x[i: i + len(h)] += st(h, g.uniform(-1, 1))[: n - i]
        tt += g.uniform(9, 18)
    return bed(x, 0.03)


# ------------------------------------------------------------------ town / time
def train_horn_distant(dur=None):
    L = 3.2
    out = np.zeros(ns(L))
    for st0, ln in [(0.0, 1.0), (1.25, 1.6)]:
        m = ns(ln)
        tone = sum(glide_tone(f, f * 0.995, ln, (1, 0.7, 0.5, 0.35, 0.25)) for f in (311.1, 370.0, 466.2))
        tone *= S.adsr(m, 0.12, 0.1, 0.9, 0.35)
        i = ns(st0)
        out[i: i + m] += tone[: len(out) - i]
    out = S.lp(out, 1400)
    return spot(space(out, 0.55, 3.0, 0.3), 0.25)


def fans_wind_down(dur=3.5, seed=5):
    n = ns(dur)
    t = t_axis(n)
    out = np.zeros((n, 2))
    g = _rng(seed)
    for k in range(4):
        rate0 = g.uniform(9, 14)
        decay = g.uniform(1.4, 2.4)
        rate = rate0 * np.exp(-t / decay)
        ph = np.cumsum(2 * np.pi * rate / SR)
        whoosh = S.bp(noise(n, seed + k), 300, 1600) * (0.55 + 0.45 * np.sin(ph) ** 2) * np.exp(-t / (decay * 1.2))
        hum = np.sin(np.cumsum(2 * np.pi * (100 * np.exp(-t / (decay * 1.5)) + 20) / SR)) * 0.15 * np.exp(-t / decay)
        out += st(whoosh + hum, g.uniform(-0.8, 0.8)) * g.uniform(0.5, 1.0)
    return spot(space(out, 0.2, 1.2), 0.3)


def town_groan(dur=2.5, seed=6):
    n = ns(dur)
    out = np.zeros((n + ns(1), 2))
    g = _rng(seed)
    for k in range(12):
        f = g.uniform(140, 300)
        L = g.uniform(1.2, 2.0)
        notes = [(0.0, L, f, 0.8)]
        v = S.voice(notes, "a" if k % 2 else "o", vel=0.6, formant_shift=g.uniform(0.9, 1.25), vib_depth=0.01)
        # downward glide "aww": time-warp via simple pitch-lowering resample chunks is costly; use amplitude shape
        v = v * np.linspace(1, 0.4, len(v))
        i = ns(g.uniform(0, 0.4))
        sv = st(S.lp(v, 1200), g.uniform(-0.9, 0.9))
        m = min(len(sv), len(out) - i)
        out[i: i + m] += sv[:m]
    return spot(space(out[:n], 0.6, 2.8, 0.3), 0.18)


def clock_strike(dur=None, n=12, interval=1.7, f=196.0):
    L = (n - 1) * interval + 4.5
    out = np.zeros(ns(L))
    for k in range(n):
        b = S.bell(f, 4.5, 1.0, decay=1.4)
        b[: ns(3.0)] += 0.4 * S.bell(f * 2.01, 3.0, 1.0)
        i = ns(k * interval)
        out[i: i + len(b)] += b[: len(out) - i]
    out = S.lp(out, 3000)
    return spot(space(out, 0.5, 3.5, 0.35), 0.35)


# ------------------------------------------------------------------ dog
def dog_bark_mono(seed=0, f=320):
    n = ns(0.18)
    t = t_axis(n)
    fc = f * (1.25 - 0.35 * t / 0.18)
    src = S.osc_additive(fc, [1 / k ** 1.2 for k in range(1, 30)], maxf=8000)
    src += S.bp(noise(n, seed), 600, 4000) * 0.6
    out = S._formant(src, "a", 1.45) + 0.2 * src
    out *= S.adsr(n, 0.005, 0.05, 0.6, 0.08)
    return out


def dog_bark(dur=None, n=2):
    parts = []
    for k in range(n):
        parts += [dog_bark_mono(k, 320 + 20 * k), np.zeros(ns(0.12))]
    return spot(space(np.concatenate(parts), 0.12, 1.0), 0.55)


def dog_whine(dur=None):
    L = 1.0
    n = ns(L)
    t = t_axis(n)
    fc = 950 + 350 * np.sin(np.pi * t / L) - 200 * (t / L) ** 2
    fc *= 1 + 0.02 * np.sin(2 * np.pi * 9 * t)
    src = S.osc_additive(fc, [1, 0.35, 0.12, 0.05])
    src = src * np.sin(np.pi * t / L) ** 0.8
    src += S.bp(noise(n, 9), 1500, 4000) * 0.04
    return spot(space(src, 0.1, 0.8), 0.32)


def dog_sneeze(dur=None):
    a = S.bp(noise(ns(0.08), 3), 800, 3000) * np.linspace(0.2, 1, ns(0.08))
    b = S.hp(noise(ns(0.22), 4), 2500) * env_exp(ns(0.22), 0.05)
    tone = glide_tone(700, 420, 0.12, (1, 0.4, 0.2)) * env_exp(ns(0.12), 0.04) * 0.6
    out = np.concatenate([a, b])
    out[ns(0.08): ns(0.08) + len(tone)] += tone
    return spot(space(out, 0.1, 0.8), 0.4)


def dog_howl(dur=None, seed=11):
    g = _rng(seed)
    pts = [(0, 1.1, 480, 0.7), (1.1, 0.5, 690, 0.85), (1.6, 0.25, 610, 0.8), (1.85, 0.6, 720, 0.85),
           (2.45, 0.9, 520, 0.7)]
    v = S.voice(pts, "u", vel=0.9, vib_depth=0.035, wobble=0.02, formant_shift=1.3, breathy=0.2)
    v2 = S.voice(pts, "o", vel=0.6, vib_depth=0.03, formant_shift=1.4)
    m = min(len(v), len(v2))
    out = v[:m] + 0.5 * v2[:m]
    return spot(space(out, 0.35, 2.0), 0.4)


def dog_pant(dur=2.0):
    n = ns(dur)
    t = t_axis(n)
    ph = (t * 3.2) % 1
    env = np.where(ph < 0.45, np.sin(np.pi * ph / 0.45), 0) ** 1.5
    x = S.bp(noise(n, 13), 700, 3500) * env * (0.7 + 0.3 * (np.floor(t * 3.2) % 2))
    return spot(space(x, 0.1, 0.7), 0.25)


# ------------------------------------------------------------------ feet / wood
def footsteps_soft(dur=2.0, rate=2.2, seed=14):
    n = ns(dur)
    out = np.zeros(n)
    g = _rng(seed)
    tt = 0.05
    while tt < dur - 0.1:
        m = ns(0.09)
        p = S.lp(noise(m, int(tt * 100)), 600) * env_exp(m, 0.02) + 0.5 * thump(90, 0.09, int(tt * 9))
        i = ns(tt)
        out[i: i + m] += p[: n - i] * g.uniform(0.6, 1.0)
        tt += 1 / rate * g.uniform(0.9, 1.1)
    return spot(space(out, 0.1, 0.8), 0.25)


def creak(dur=0.7, f0=180, f1=120, seed=15, lo=300, hi=1600):
    n = ns(dur)
    t = t_axis(n)
    rate = f0 + (f1 - f0) * t / dur + 25 * S.lp(noise(n, seed), 6) * 10
    ph = np.cumsum(rate / SR)
    pulses = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
    out = S.bp(pulses, lo, hi) + 0.3 * S.bp(pulses, hi, hi * 2.5)
    return out * np.sin(np.pi * t / dur) ** 0.7


def stair_creak(dur=None):
    return spot(space(creak(0.75, 140, 95, 16), 0.15, 1.0), 0.3)


def floor_creak(dur=None):
    return spot(space(creak(0.6, 110, 80, 17, 200, 1100), 0.15, 1.0), 0.28)


# ------------------------------------------------------------------ magic / shop
def wind_chime_hello(dur=None, seed=18):
    g = _rng(seed)
    notes = ["D6", "F#6", "A6", "B6", "E6", "D7", "A6"]
    out = np.zeros((ns(3.5), 2))
    tt = 0.0
    for i, nme in enumerate(notes):
        c = S.chime(S.hz(nme), 2.4, g.uniform(0.5, 1.0))
        k = ns(tt)
        sc = st(c, g.uniform(-0.6, 0.6))
        m = min(len(sc), len(out) - k)
        out[k: k + m] += sc[:m]
        tt += g.uniform(0.06, 0.16)
    return spot(space(out, 0.35, 2.2, 0.7), 0.4)


def shimmer(dur, f0, f1, density=14, seed=19, up=True):
    n = ns(dur)
    out = np.zeros((n, 2))
    g = _rng(seed)
    for k in range(density):
        st0 = g.uniform(0, dur * 0.7)
        L = g.uniform(0.4, 1.2)
        L = min(L, dur - st0)
        if L <= 0.05:
            continue
        fa = g.uniform(f0, f1)
        fb = fa * (g.uniform(1.3, 2.0) if up else g.uniform(0.5, 0.75))
        tone = glide_tone(fa, fb, L, (1, 0.2)) * np.sin(np.pi * np.linspace(0, 1, ns(L))) ** 2
        i = ns(st0)
        sc = st(tone, g.uniform(-0.8, 0.8))
        m = min(len(sc), n - i)
        out[i: i + m] += sc[:m]
    return out


def wall_glow(dur=3.0):
    x = shimmer(dur, 700, 2200, 22, 20, True)
    n = ns(dur)
    sw = noise_sweep(dur, 400, 4000, 0.5, 21) * np.linspace(0, 1, n) ** 2 * 0.3
    x += st(sw)
    x += st(S.pad(["D3", "A3", "D4"], dur, 1.0, 0.5)[:n] * 4 * np.linspace(0, 1, n))
    return spot(space(x, 0.35, 2.2, 0.6), 0.4)


def sparkle(dur=1.2, seed=22, count=9):
    g = _rng(seed)
    out = np.zeros((ns(dur + 1.0), 2))
    pool = ["D7", "E7", "F#7", "A6", "B6", "D6"]
    for k in range(count):
        c = S.music_box(S.hz(pool[g.integers(0, len(pool))]), 0.8, g.uniform(0.4, 1.0))
        i = ns(g.uniform(0, dur * 0.8))
        sc = st(c, g.uniform(-0.9, 0.9))
        m = min(len(sc), len(out) - i)
        out[i: i + m] += sc[:m]
    return spot(space(out, 0.3, 1.6, 0.7), 0.3)


def shop_unfold(dur=4.5, seed=23):
    n = ns(dur + 1.5)
    out = np.zeros((n, 2))
    g = _rng(seed)

    def put(t, x, p=0.0, gain=1.0):
        sx = x if x.ndim == 2 else st(x, p)
        i = ns(t)
        m = min(len(sx), n - i)
        if m > 0:
            out[i: i + m] += sx[:m] * gain

    # panels clacking open in an accelerating, rising sequence
    tt, k = 0.1, 0
    while tt < dur * 0.75:
        put(tt, wood(450 + 60 * k + g.uniform(-30, 30), 0.15, k), g.uniform(-0.7, 0.7), 0.8)
        put(tt + 0.02, noise_sweep(0.35, 500, 2500, 0.8, 50 + k) * 0.6, g.uniform(-0.5, 0.5))
        tt += max(0.12, 0.42 * 0.88 ** k)
        k += 1
    put(dur * 0.55, awning_snap_mono() * 0.9, 0.2)
    put(0.0, noise_sweep(dur, 300, 3000, 0.6, 60) * 0.5)
    put(dur * 0.35, shimmer(dur * 0.65, 900, 3000, 20, 61, True), 0, 0.8)
    for j in range(5):  # lanterns
        put(dur * 0.6 + j * 0.22, lantern_mono(70 + j) * 0.5, -0.6 + j * 0.3)
    put(dur * 0.85, wind_chime_hello()[:, :] * 0.6)
    return spot(space(out, 0.25, 1.8, 0.6), 0.55)


def lantern_mono(seed=24):
    n = ns(0.45)
    t = t_axis(n)
    w = S.lp(noise(n, seed), 700) * np.sin(np.pi * np.clip(t / 0.35, 0, 1)) ** 2
    tone = glide_tone(180, 320, 0.45, (1, 0.3)) * env_exp(n, 0.12) * 0.3
    ch = np.zeros(n)
    c = S.chime(S.hz("A6"), 0.4, 0.2)
    ch[: len(c)] += c[:n]
    return w + tone + ch


def lantern_light(dur=None):
    return spot(space(lantern_mono(), 0.2, 1.0), 0.3)


def awning_snap_mono():
    n = ns(0.3)
    t = t_axis(n)
    snap = S.bp(noise(n, 25), 900, 5000) * np.exp(-t / 0.018)
    flap = S.bp(noise(n, 26), 200, 1200) * np.exp(-t / 0.08) * 0.5
    return snap + flap + 0.4 * thump(110, 0.3, 2)


def awning_snap(dur=None):
    return spot(space(awning_snap_mono(), 0.12, 0.9), 0.5)


# ------------------------------------------------------------------ Tola, the brass scale
def tola_tink(dur=None):
    return spot(space(metal(1850, 0.8, 1.0, decay=0.6, seed=1), 0.15, 1.0), 0.3)


def tola_clank(dur=None):
    a = metal(620, 0.9, 1.0, decay=0.5, seed=2)
    b = metal(700, 0.7, 0.7, decay=0.4, seed=3)
    out = np.zeros(ns(1.1))
    out[: len(a)] += a
    k = ns(0.11)
    out[k: k + len(b)] += b[: len(out) - k]
    out += np.pad(S.bp(noise(ns(0.4), 4), 3000, 9000) * env_exp(ns(0.4), 0.06) * 0.2, (0, len(out) - ns(0.4)))
    return spot(space(out, 0.15, 1.0), 0.45)


def tola_clonk(dur=None):
    a = metal(330, 1.6, 1.0, ratios=(1.0, 2.0, 2.92, 4.1, 5.4), decay=0.8, seed=5)
    a[: ns(0.4)] += thump(120, 0.4, 5)[: ns(0.4)] * 0.7
    return spot(space(a, 0.2, 1.3), 0.55)


def tola_laugh(dur=1.6, seed=26):
    g = _rng(seed)
    out = np.zeros(ns(dur + 0.6))
    tt, k = 0.0, 0
    while tt < dur:
        f = g.uniform(1400, 2400) * (1 + 0.15 * np.sin(k * 1.3))
        m = metal(f, 0.25, g.uniform(0.4, 1.0), decay=0.4, seed=k)
        i = ns(tt)
        out[i: i + len(m)] += m[: len(out) - i]
        tt += g.uniform(0.045, 0.09) * (1 + 0.7 * (k % 6 == 5))
        k += 1
    return spot(space(out, 0.18, 1.0), 0.35)


def tola_alarm(dur=None):
    out = np.zeros(ns(1.6))
    for k in range(3):
        c = metal(560 + 30 * k, 0.6, 1.0, decay=0.45, seed=30 + k) + 0.5 * thump(140, 0.3, k)[: ns(0.6)].sum() * 0
        c[: ns(0.25)] += thump(160, 0.25, k)[: ns(0.25)] * 0.5
        i = ns(k * 0.32)
        out[i: i + len(c)] += c[: len(out) - i]
    return spot(space(out, 0.2, 1.2), 0.6)


def tola_clonng(dur=None):
    a = metal(220, 4.0, 1.0, ratios=(1.0, 2.0, 2.76, 3.98, 5.43, 6.8), decay=1.2, seed=7)
    a[: ns(0.5)] += thump(90, 0.5, 7)[: ns(0.5)]
    t = t_axis(len(a))
    a *= 1 + 0.12 * np.sin(2 * np.pi * 3.2 * t)  # bloom/beating
    return spot(space(a, 0.35, 2.8, 0.55), 0.65)


def tola_thunk(dur=None):
    n = ns(4.0)
    th = thump(48, 1.0, 8)
    out = np.zeros(n)
    out[: len(th)] += th * 1.3
    ring = metal(147, 3.8, 0.8, ratios=(1.0, 2.0, 3.01, 4.2), decay=1.3, seed=8)
    out[ns(0.02): ns(0.02) + len(ring)] += ring[: n - ns(0.02)]
    return spot(space(out, 0.35, 3.0, 0.45), 0.7)


def jar_chord(dur=None, seed=27):
    g = _rng(seed)
    notes = ["D5", "F#5", "A5", "D6", "F#6", "A6", "B6", "D7", "E6", "A5"]
    out = np.zeros((ns(3.5), 2))
    for i, nme in enumerate(notes):
        c = S.chime(S.hz(nme), 3.0, g.uniform(0.5, 0.9))
        k = ns(i * 0.018 + g.uniform(0, 0.02))
        sc = st(c, -0.9 + 1.8 * i / (len(notes) - 1))
        m = min(len(sc), len(out) - k)
        out[k: k + m] += sc[:m]
    return spot(space(out, 0.35, 2.4, 0.75), 0.5)


def jars_refill(dur=2.8, seed=28):
    g = _rng(seed)
    n = ns(dur + 1.5)
    out = np.zeros((n, 2))
    tt, gap = 0.0, 0.12
    pool = ["D6", "E6", "F#6", "A6", "B6", "D7", "A5", "F#5"]
    while tt < dur:
        c = S.chime(S.hz(pool[g.integers(0, 8)]) * g.uniform(0.995, 1.005), 1.2, g.uniform(0.3, 0.8))
        i = ns(tt)
        sc = st(c, g.uniform(-0.9, 0.9))
        m = min(len(sc), n - i)
        out[i: i + m] += sc[:m]
        tt += gap * g.uniform(0.5, 1.2)
        gap = max(0.018, gap * 0.94)
    out += st(S.bp(noise(n, seed), 3000, 9000) * np.sin(np.pi * np.linspace(0, 1, n)) * 0.05)
    return spot(space(out, 0.3, 2.0, 0.7), 0.45)


# ------------------------------------------------------------------ bubbles / floating
def bubble_rise(dur=1.6):
    n = ns(dur)
    t = t_axis(n)
    tone = glide_tone(300, 1200, dur, (1, 0.25), curve=0.7, vib=0.04, vib_rate=7)
    tone *= np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.8
    x = st(tone * 0.6) + shimmer(dur, 1500, 4000, 10, 31, True) * 0.5
    return spot(space(x, 0.3, 1.6, 0.6), 0.35)


def bubble_settle(dur=None):
    n = ns(0.6)
    tone = glide_tone(900, 500, 0.6, (1, 0.3)) * env_exp(n, 0.15)
    c = S.chime(S.hz("A6"), 1.2, 0.4)
    out = np.zeros(ns(1.2))
    out[:n] += tone
    out[ns(0.08): ns(0.08) + len(c)] += c[: len(out) - ns(0.08)]
    return spot(space(out, 0.25, 1.2), 0.3)


def bubble_fizzle(dur=1.8, seed=32):
    n = ns(dur)
    t = t_axis(n)
    fc = 300 * (1 + 2 * np.sin(np.pi * np.clip(t / (dur * 0.8), 0, 1) * 0.5)) * (1 - 0.6 * (t / dur) ** 2)
    tone = S.osc_additive(fc * (1 + 0.05 * S.lp(noise(n, seed), 20) * 20), [1, 0.2]) * (1 - t / dur) ** 1.5
    g = _rng(seed)
    crack = np.zeros(n)
    for k in range(40):
        i = ns(g.uniform(dur * 0.3, dur * 0.95))
        m = ns(0.004)
        crack[i: i + m] += S.hp(noise(m, k), 3000)[: n - i] * g.uniform(0.2, 0.6)
    return spot(space(tone * 0.5 + crack * 0.6, 0.2, 1.0), 0.28)


def magic_float(dur=2.0):
    n = ns(dur)
    x = shimmer(dur, 600, 1800, 16, 33, True)
    x += st(glide_tone(220, 440, dur, (1, 0.3, 0.1)) * np.sin(np.pi * np.linspace(0, 1, n)) * 0.25)
    return spot(space(x, 0.35, 2.0, 0.6), 0.35)


def whoosh(dur=0.9, intensity=1.0, seed=34):
    n = ns(dur)
    x = noise_sweep(dur, 300, 2200 * (0.6 + 0.4 * intensity), 0.9, seed)
    x2 = noise_sweep(dur, 250, 1700 * (0.6 + 0.4 * intensity), 0.9, seed + 1)
    out = np.stack([x, x2[::-1] * 0.3 + x2 * 0.7], 1)
    return spot(space(out, 0.15, 1.0), 0.25 + 0.25 * min(1.0, intensity))


def wind_flight(dur=8.0, seed=35):
    n = ns(dur)
    t = t_axis(n)
    a = S.lp(noise(n, seed), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 3.1) ** 2)
    b = S.bp(noise(n, seed + 1), 400, 1600) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.3 + 1) ** 2) * 0.5
    return bed(np.stack([a + b * 0.6, a * 0.8 + b], 1), 0.035)


def boing(dur=None):
    L = 0.9
    n = ns(L)
    t = t_axis(n)
    fc = 180 * (1 + 0.6 * np.exp(-t / 0.08)) * (1 + 0.25 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.4))
    x = S.osc_additive(fc, [1, 0.5, 0.25, 0.1]) * np.exp(-t / 0.35)
    x += wood(900, 0.05, 3)[:n].sum() * 0 + np.pad(wood(900, 0.05, 3), (0, n - ns(0.05))) * 0.4
    return spot(space(x, 0.1, 0.8), 0.45)


def pop(dur=None):
    n = ns(0.12)
    x = glide_tone(1200, 400, 0.12, (1, 0.2)) * env_exp(n, 0.03) + S.hp(noise(n, 36), 2000) * env_exp(n, 0.005)
    return spot(x, 0.35)


# ------------------------------------------------------------------ creatures
def monkey_chatter(dur=1.5, seed=37):
    g = _rng(seed)
    notes = []
    tt = 0.0
    while tt < dur - 0.1:
        L = g.uniform(0.05, 0.12)
        notes.append((tt, L, g.uniform(900, 1500), g.uniform(0.6, 1.0)))
        tt += L + g.uniform(0.01, 0.05)
    v = S.voice(notes, "e", vel=1.0, formant_shift=1.9, vib_depth=0.02, breathy=0.3)
    return spot(space(v, 0.15, 1.0), 0.35)


def buffalo_moo(dur=None):
    pts = [(0.0, 0.5, 120, 0.8), (0.5, 1.2, 104, 0.9), (1.7, 0.5, 92, 0.6)]
    a = S.voice(pts, "u", vel=1.0, formant_shift=0.7, breathy=0.25, vib_depth=0.012)
    b = S.voice(pts, "o", vel=0.7, formant_shift=0.75)
    m = min(len(a), len(b))
    return spot(space(a[:m] + 0.6 * b[:m], 0.2, 1.4, 0.4), 0.5)


def koel_call(dur=None, n_calls=3):
    out = []
    for k in range(n_calls):
        f = 800 * 1.08 ** k
        a = glide_tone(f, f * 1.25, 0.18, (1, 0.25)) * np.sin(np.pi * np.linspace(0, 1, ns(0.18)))
        b = glide_tone(f * 1.25, f * 1.45, 0.28, (1, 0.25)) * np.sin(np.pi * np.linspace(0, 1, ns(0.28)))
        out += [a, np.zeros(ns(0.04)), b, np.zeros(ns(0.45))]
    return spot(space(np.concatenate(out), 0.4, 2.5, 0.5), 0.25)


def sparrows_dawn(dur=6.0, seed=38):
    n = ns(dur)
    out = np.zeros((n, 2))
    g = _rng(seed)
    tt = 0.1
    while tt < dur - 0.3:
        for _ in range(int(g.integers(1, 4))):
            L = g.uniform(0.04, 0.09)
            f = g.uniform(3200, 5800)
            c = glide_tone(f, f * g.uniform(0.7, 1.3), L, (1, 0.15)) * np.sin(np.pi * np.linspace(0, 1, ns(L)))
            i = ns(tt)
            sc = st(c, g.uniform(-0.9, 0.9)) * g.uniform(0.3, 1.0)
            m = min(len(sc), n - i)
            out[i: i + m] += sc[:m]
            tt += L + g.uniform(0.02, 0.07)
        tt += g.uniform(0.2, 0.9)
    return bed(space(out, 0.3, 1.5), 0.02)


# ------------------------------------------------------------------ wishes / chaos
def syrup_gush(dur=3.0, seed=39):
    n = ns(dur)
    t = t_axis(n)
    wash = S.lp(noise(n, seed), 900) * np.clip(t / 0.4, 0, 1) * (1 - 0.3 * t / dur)
    g = _rng(seed)
    bl = np.zeros(n)
    for k in range(int(dur * 18)):
        L = g.uniform(0.05, 0.14)
        f0 = g.uniform(180, 520)
        b = glide_tone(f0, f0 * g.uniform(1.4, 2.0), L, (1, 0.3)) * env_exp(ns(L), L / 3)
        i = ns(g.uniform(0, dur - L))
        bl[i: i + len(b)] += b * g.uniform(0.3, 0.9)
    return spot(space(wash * 0.6 + bl * 0.5, 0.2, 1.2), 0.5)


def slosh(dur=0.7, seed=40):
    n = ns(dur)
    x = S.lp(noise(n, seed), 1100) * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    x += syrup_gush(dur, seed)[:n, 0] * 0.3
    return spot(space(x, 0.15, 0.9), 0.35)


def sploosh(dur=None, seed=41):
    n = ns(1.4)
    t = t_axis(n)
    hit_ = S.lp(noise(n, seed), 2500) * np.exp(-t / 0.18) + thump(70, 1.4, seed)[:n] * 0.6
    tail = syrup_gush(1.4, seed + 1)[:n, 0] * np.exp(-t / 0.5) * 0.5
    return spot(space(hit_ + tail, 0.2, 1.2), 0.65)


def rickshaw_bell(dur=None):
    out = np.zeros(ns(1.4))
    for k in range(2):
        n = ns(0.6)
        t = t_axis(n)
        r = (np.sin(2 * np.pi * 2150 * t) + 0.6 * np.sin(2 * np.pi * 3270 * t) + 0.3 * np.sin(2 * np.pi * 5100 * t))
        r *= np.exp(-t / 0.25) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t) ** 2)
        i = ns(k * 0.3)
        out[i: i + n] += r[: len(out) - i]
    return spot(space(out, 0.2, 1.2), 0.4)


def rickshaw_zoom(dur=2.0, seed=42):
    n = ns(dur)
    t = t_axis(n)
    u = t / dur
    env = np.exp(-((u - 0.45) / 0.22) ** 2)
    rattle = S.bp(noise(n, seed), 500, 3000) * (0.5 + 0.5 * (np.sin(2 * np.pi * 22 * t) > 0.6))
    w = noise_sweep(dur, 400, 1800, 1.0, seed + 1, env=np.ones(n))
    x = (rattle * 0.5 + w) * env
    p = np.clip((u - 0.45) * 3, -1, 1)
    L = x * np.cos((p + 1) * np.pi / 4)
    R = x * np.sin((p + 1) * np.pi / 4)
    return spot(space(np.stack([L, R], 1), 0.15, 1.0), 0.45)


# ------------------------------------------------------------------ crystal / fading
def crystal_tink(dur=None):
    return spot(space(S.chime(S.hz("F#7"), 1.4, 1.0), 0.25, 1.4, 0.8), 0.3)


def crystal_spread(dur=2.5, seed=43):
    g = _rng(seed)
    n = ns(dur + 0.8)
    out = np.zeros((n, 2))
    tt, gap = 0.0, 0.15
    while tt < dur:
        f = g.uniform(3000, 7000)
        m = ns(0.03)
        c = np.sin(2 * np.pi * f * t_axis(m)) * env_exp(m, 0.008) + S.hp(noise(m, int(tt * 1000)), 4000) * env_exp(m, 0.003)
        i = ns(tt)
        sc = st(c, g.uniform(-0.8, 0.8)) * g.uniform(0.3, 1.0)
        out[i: i + m] += sc[: n - i]
        tt += gap * g.uniform(0.3, 1.2)
        gap = max(0.012, gap * 0.93)
    out += st(S.pad(["B2", "C3"], dur, 1.0, 0.3)[:n] * 6)
    return spot(space(out, 0.3, 1.6, 0.7), 0.35)


def crystal_melt(dur=2.4):
    x = shimmer(dur, 1500, 4500, 20, 44, up=False)
    n = ns(dur)
    x += st(glide_tone(1760, 880, dur, (1, 0.2)) * np.sin(np.pi * np.linspace(0, 1, n)) * 0.2)
    return spot(space(x, 0.4, 2.2, 0.7), 0.35)


def shop_flicker(dur=2.0, seed=45):
    n = ns(dur)
    t = t_axis(n)
    g = _rng(seed)
    gate = (S.lp(noise(n, seed), 8) * 40 > -0.2).astype(float)
    gate = S.lp(gate, 60)
    buzz = S.osc_additive(np.full(n, 100.0), [1, 0.5, 0.4, 0.3, 0.2, 0.15]) * 0.4 + S.bp(noise(n, seed + 1), 2000, 6000) * 0.1
    x = buzz * gate
    for k in range(3):
        c = S.chime(S.hz(["D6", "A6", "F#6"][k]), 0.6, 0.3) * 0.5
        i = ns(g.uniform(0, dur - 0.6))
        x[i: i + len(c)] += c[: n - i]
    return spot(space(x, 0.25, 1.2), 0.25)


def shop_shut(dur=None, seed=46):
    n = ns(1.6)
    x = np.zeros(n)
    th = thump(55, 0.9, seed) * 1.2
    x[: len(th)] += th
    slap = S.bp(noise(ns(0.08), seed), 300, 3000) * env_exp(ns(0.08), 0.015)
    x[: len(slap)] += slap
    air = noise_sweep(1.2, 1200, 300, 0.9, seed + 1) * 0.4
    x[ns(0.05): ns(0.05) + len(air)] += air[: n - ns(0.05)]
    return spot(space(x, 0.3, 1.8, 0.4), 0.65)


# ------------------------------------------------------------------ household
def page_turn(dur=None, seed=47):
    n = ns(0.55)
    t = t_axis(n)
    crinkle = S.bp(noise(n, seed), 1800, 7000) * (0.4 + 0.6 * (S.lp(noise(n, seed + 1), 40) * 15) ** 2)
    x = crinkle * np.sin(np.pi * t / 0.55) ** 0.6
    return spot(space(x, 0.1, 0.6), 0.2)


def water_pour(dur=2.0, seed=48):
    n = ns(dur)
    g = _rng(seed)
    x = S.bp(noise(n, seed), 600, 2500) * 0.3
    for k in range(int(dur * 25)):
        L = g.uniform(0.03, 0.08)
        f0 = g.uniform(400, 1000)
        b = glide_tone(f0, f0 * 1.6, L, (1,)) * env_exp(ns(L), L / 3)
        i = ns(g.uniform(0, dur - L))
        x[i: i + len(b)] += b * g.uniform(0.2, 0.6)
    x *= S.adsr(n, 0.1, 0.1, 1.0, 0.3)
    return spot(space(x, 0.15, 0.9), 0.3)


def iron_steam(dur=1.2, seed=49):
    n = ns(dur)
    x = S.hp(noise(n, seed), 2500) * S.adsr(n, 0.02, 0.2, 0.6, 0.5)
    return spot(space(x, 0.15, 0.8), 0.22)


def swallow_gulp(dur=None):
    n = ns(0.25)
    x = glide_tone(170, 75, 0.25, (1, 0.3)) * np.sin(np.pi * np.linspace(0, 1, n)) + np.pad(
        S.bp(noise(ns(0.02), 5), 500, 2000) * 0.5, (0, n - ns(0.02)))
    return spot(x, 0.3)


def munch(dur=None, seed=50):
    out = np.zeros(ns(0.9))
    for k in range(3):
        m = ns(0.1)
        c = S.bp(noise(m, seed + k), 900, 3500) * env_exp(m, 0.025) + 0.3 * thump(160, 0.1, k)[:m]
        i = ns(k * 0.28)
        out[i: i + m] += c
    return spot(out, 0.3)


# ------------------------------------------------------------------ the lullaby, diegetic
def hum_lullaby(dur=None, bpm=60, octave=-1):
    notes = seq(LULLABY, 0.0, bpm, octave=octave, vel=0.85)
    v = S.voice(notes, "m", vel=1.0, breathy=0.18, wobble=0.012, vib_depth=0.012, formant_shift=0.95)
    return spot(space(v, 0.18, 1.2, 0.4), 0.35)


def wall_echo_lullaby(dur=None, bpm=60):
    notes = seq(LULLABY, 0.0, bpm, octave=1, vel=0.6)
    L = notes[-1][0] + notes[-1][1] + 3.0
    out = np.zeros((ns(L + 2.5), 2))
    for delay, gain, p in [(0.0, 1.0, 0.0), (0.42, 0.45, -0.6), (0.84, 0.25, 0.6)]:
        for stt, du, f, v in notes:
            c = S.chime(f, 2.4, v) * gain
            i = ns(stt + delay)
            sc = st(S.lp(c, 5000), p)
            m = min(len(sc), len(out) - i)
            out[i: i + m] += sc[:m]
    return spot(space(out, 0.6, 3.5, 0.45), 0.25)


def sung_lullaby_child(dur=None, bpm=64):
    notes = seq(LULLABY, 0.0, bpm, octave=0, vel=0.85, legato=0.92)
    v = S.voice(notes, "a", vel=1.0, consonant_l=True, formant_shift=1.28, vib_depth=0.006, breathy=0.08)
    return spot(space(v, 0.3, 2.0, 0.5), 0.35)


# ------------------------------------------------------------------ off-screen kids (TTS-layered)
def _kid_layers(phrases, seed=51, n_layers=5, spread=0.35):
    """Layer short kid TTS utterances with small pitch/time offsets -> small off-screen group."""
    from pathlib import Path

    from scipy.signal import resample_poly

    from .. import voice as V
    cache = Path(__file__).resolve().parents[3] / "films" / __import__("os").environ.get("FILM", "midnight_sweet_shop") / "edit" / "audio" / "cache" / "kids"
    g = _rng(seed)
    clips = []
    for k in range(n_layers):
        char = "kid1" if k % 2 == 0 else "kid2"
        text = phrases[k % len(phrases)]
        try:
            meta = V.synth(char, text, cache)
            import soundfile as sf
            x, _ = sf.read(meta["wav"])
        except Exception as e:  # noqa: BLE001
            warnings.warn(f"kid TTS unavailable ({e}); using synthetic fallback")
            notes = [(i * 0.16, 0.12, g.uniform(380, 520), 0.9) for i in range(5)]
            x = S.voice(notes, "a", vel=1.0, formant_shift=1.35, consonant_l=False)
        # small pitch variation via tiny integer ratios
        up, down = [(20, 19), (19, 20), (21, 20), (20, 21), (1, 1)][k % 5]
        if up != down:
            x = resample_poly(x, up, down)
        clips.append((g.uniform(0, spread), st(x, g.uniform(-0.8, 0.8)) * g.uniform(0.6, 1.0)))
    L = max(o + len(c) / SR for o, c in clips) + 0.5
    out = np.zeros((ns(L), 2))
    for o, c in clips:
        i = ns(o)
        out[i: i + len(c)] += c
    out[:, 0] = S.lp(out[:, 0], 5000)
    out[:, 1] = S.lp(out[:, 1], 5000)
    return space(out, 0.3, 1.4, 0.5)


def kids_laugh(dur=None):
    return spot(_kid_layers(["Ha ha ha ha ha!", "Hee hee hee hee!", "Ha ha ha!", "Ahahaha!", "Hahaha ha!"], 52, 6, 0.4), 0.4)


def kids_gasp(dur=None):
    return spot(_kid_layers(["Whoa!", "Ooh!", "Wow!", "Whoaaa!"], 53, 5, 0.25), 0.4)


# ------------------------------------------------------------------ registry
REGISTRY = {
    "crickets_bed": crickets_bed, "night_bed": night_bed, "day_bed": day_bed, "heat_cicadas": heat_cicadas,
    "train_horn_distant": train_horn_distant, "fans_wind_down": fans_wind_down, "town_groan": town_groan,
    "clock_strike": clock_strike, "dog_whine": dog_whine, "dog_bark": dog_bark, "dog_sneeze": dog_sneeze,
    "dog_howl": dog_howl, "dog_pant": dog_pant, "footsteps_soft": footsteps_soft, "stair_creak": stair_creak,
    "wind_chime_hello": wind_chime_hello, "wall_glow": wall_glow, "shop_unfold": shop_unfold,
    "lantern_light": lantern_light, "awning_snap": awning_snap, "floor_creak": floor_creak,
    "tola_tink": tola_tink, "tola_clank": tola_clank, "tola_clonk": tola_clonk, "tola_laugh": tola_laugh,
    "tola_alarm": tola_alarm, "tola_clonng": tola_clonng, "tola_thunk": tola_thunk, "jar_chord": jar_chord,
    "bubble_rise": bubble_rise, "bubble_settle": bubble_settle, "bubble_fizzle": bubble_fizzle,
    "magic_float": magic_float, "whoosh": whoosh, "wind_flight": wind_flight, "boing": boing,
    "sparkle": sparkle, "monkey_chatter": monkey_chatter, "shadow_grow": None, "syrup_gush": syrup_gush,
    "slosh": slosh, "rickshaw_bell": rickshaw_bell, "rickshaw_zoom": rickshaw_zoom, "sploosh": sploosh,
    "buffalo_moo": buffalo_moo, "crystal_tink": crystal_tink, "crystal_spread": crystal_spread,
    "crystal_melt": crystal_melt, "shop_flicker": shop_flicker, "shop_shut": shop_shut,
    "jars_refill": jars_refill, "page_turn": page_turn, "water_pour": water_pour, "iron_steam": iron_steam,
    "koel_call": koel_call, "sparrows_dawn": sparrows_dawn, "kids_laugh": kids_laugh, "kids_gasp": kids_gasp,
    "hum_lullaby": hum_lullaby, "wall_echo_lullaby": wall_echo_lullaby, "sung_lullaby_child": sung_lullaby_child,
    "pop": pop, "swallow_gulp": swallow_gulp, "munch": munch,
}


def shadow_grow(dur=3.0):
    n = ns(dur)
    t = t_axis(n)
    low = glide_tone(38, 62, dur, (1, 0.5, 0.25), curve=1.5) * np.clip(t / dur, 0, 1) ** 1.5
    sw = noise_sweep(dur, 150, 1200, 0.8, 54, env=(t / dur) ** 2) * 0.5
    pad_ = S.pad(["D2", "A2", "D3"], dur, 1.0, 0.6)[:n] * 8 * (t / dur) ** 1.2
    x = low + sw + pad_
    x[-ns(0.5):] *= np.linspace(1, 0.3, ns(0.5))
    return spot(space(x, 0.35, 2.2, 0.4), 0.55)


REGISTRY["shadow_grow"] = shadow_grow
BEDS = {"crickets_bed", "night_bed", "day_bed", "heat_cicadas", "wind_flight", "sparrows_dawn"}


def _film_sfx() -> dict:
    """SFX of the current film (FILM env), from anim.films.<slug>.sfx.REGISTRY."""
    import importlib
    import os
    film = os.environ.get("FILM", "midnight_sweet_shop")
    if film == "midnight_sweet_shop":
        return {}
    try:
        return importlib.import_module(f"anim.films.{film}.sfx").REGISTRY
    except ModuleNotFoundError:
        return {}


def sfx(name: str, dur: float | None = None, **params) -> np.ndarray:
    fn = _film_sfx().get(name) or REGISTRY.get(name)
    if fn is None:
        warnings.warn(f"unknown sfx {name!r}; using sparkle")
        fn = sparkle
    import inspect
    sig = inspect.signature(fn)
    kw = {k: v for k, v in params.items() if k in sig.parameters}
    if "dur" in sig.parameters and dur is not None:
        kw["dur"] = dur
    x = fn(**kw)
    x = x if x.ndim == 2 else st(x)
    if dur is not None:
        n = ns(dur)
        if len(x) < n and name in BEDS:  # loop beds with crossfade
            reps = int(np.ceil(n / len(x))) + 1
            xf = ns(0.5)
            out = np.zeros((n + len(x), 2))
            pos = 0
            for _ in range(reps):
                seg = S.fade(x, 0.5, 0.5)
                m = min(len(seg), len(out) - pos)
                out[pos: pos + m] += seg[:m]
                pos += len(x) - xf
                if pos >= n:
                    break
            x = out[:n]
        elif len(x) > n and name in BEDS:
            x = S.fade(x[:n], 0.0, min(1.0, dur / 4))
    return np.nan_to_num(x).astype(np.float32)
