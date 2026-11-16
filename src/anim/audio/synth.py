"""Original instrument synthesis (numpy/scipy only). 48 kHz. Mono note renderers + stereo helpers.

Every renderer returns a float64 mono array and applies its own envelope (no clicks).
Phrase renderers (bansuri, sarangi, hum) take a list of notes and synthesize a continuous
pitch curve so slides/portamento sound natural.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
RNG = np.random.default_rng(7)

A4 = 440.0
NOTE_INDEX = {"C": -9, "C#": -8, "Db": -8, "D": -7, "D#": -6, "Eb": -6, "E": -5, "F": -4, "F#": -3,
              "Gb": -3, "G": -2, "G#": -1, "Ab": -1, "A": 0, "A#": 1, "Bb": 1, "B": 2}


def hz(name: str | float) -> float:
    """'F#4' -> Hz. Floats pass through."""
    if not isinstance(name, str):
        return float(name)
    n, o = (name[:-1], int(name[-1]))
    return A4 * 2 ** ((NOTE_INDEX[n] + 12 * (o - 4)) / 12)


def t_axis(n: int) -> np.ndarray:
    return np.arange(n) / SR


def ns(sec: float) -> int:
    return max(1, int(round(sec * SR)))


# ------------------------------------------------------------------ envelopes / filters
def adsr(n: int, a=0.01, d=0.1, s=0.7, r=0.1, hold: float | None = None) -> np.ndarray:
    """ADSR over n samples. `hold` = seconds before release starts (default: n - r)."""
    a_n, d_n, r_n = ns(a), ns(d), ns(r)
    hold_n = n - r_n if hold is None else min(n - r_n, ns(hold))
    env = np.full(n, s, dtype=np.float64)
    env[:a_n] = np.linspace(0, 1, a_n)[: n]
    end_d = min(hold_n, a_n + d_n)
    if end_d > a_n:
        env[a_n:end_d] = np.linspace(1, s, d_n)[: end_d - a_n]
    lvl = env[max(0, hold_n - 1)]
    env[hold_n:] = lvl * np.linspace(1, 0, n - hold_n) ** 1.5
    return env


def fade(x: np.ndarray, fin=0.005, fout=0.02) -> np.ndarray:
    x = x.copy()
    a, b = min(len(x), ns(fin)), min(len(x), ns(fout))
    x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    x[len(x) - b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


def bp(x, lo, hi, order=2):
    lo = max(10, lo); hi = min(SR / 2 - 100, hi)
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, max(f, 10), btype="high", fs=SR, output="sos"), x)


def noise(n: int, seed: int | None = None) -> np.ndarray:
    g = np.random.default_rng(seed) if seed is not None else RNG
    return g.standard_normal(n)


def pan(mono: np.ndarray, p: float = 0.0) -> np.ndarray:
    """p in [-1,1]; constant-power."""
    ang = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(ang), mono * np.sin(ang)], axis=1)


def osc_additive(freq_curve: np.ndarray, amps: list[float], phase_jitter=True, maxf=12000.0) -> np.ndarray:
    """Band-limited additive oscillator following a per-sample frequency curve."""
    ph = np.cumsum(2 * np.pi * freq_curve / SR)
    out = np.zeros_like(ph)
    fmax = float(np.max(freq_curve)) if len(freq_curve) else 0
    for k, a in enumerate(amps, start=1):
        if a == 0 or k * fmax > maxf:
            continue
        off = RNG.uniform(0, 2 * np.pi) if phase_jitter else 0.0
        out += a * np.sin(k * ph + off)
    return out


# ------------------------------------------------------------------ reverb
_IR_CACHE: dict = {}


def reverb_ir(size: float = 2.2, bright: float = 0.5, seed: int = 3) -> np.ndarray:
    key = (round(size, 2), round(bright, 2), seed)
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    n = ns(size)
    t = t_axis(n)
    g = np.random.default_rng(seed)
    irs = []
    for ch in range(2):
        x = g.standard_normal(n) * np.exp(-6.9 * t / size)
        # darken the tail: blend a low-passed copy in over time
        dark = lp(x, 1500 + 6000 * bright)
        w = np.clip(t / size * 2, 0, 1)
        x = x * (1 - w) * bright + dark * (w + (1 - bright) * (1 - w))
        x[: ns(0.012)] *= np.linspace(0, 1, ns(0.012))  # pre-delay softness
        irs.append(x / np.sqrt(np.sum(x ** 2)))
    ir = np.stack(irs, axis=1)
    _IR_CACHE[key] = ir
    return ir


def reverb(st: np.ndarray, wet=0.25, size=2.2, bright=0.5) -> np.ndarray:
    if wet <= 0 or len(st) == 0:
        return st
    ir = reverb_ir(size, bright)
    pre = ns(0.018)
    out = np.zeros((len(st) + len(ir) + pre, 2))
    for c in range(2):
        out[pre: pre + len(st) + len(ir) - 1, c] = fftconvolve(st[:, c], ir[:, c])
    dry = np.zeros_like(out)
    dry[: len(st)] = st
    return dry * (1 - wet * 0.5) + out * wet


# ------------------------------------------------------------------ plucked / struck
def santoor(f, dur=2.5, vel=0.8, bright=1.0) -> np.ndarray:
    f = hz(f)
    n = ns(max(dur, 0.4) + 1.2)
    t = t_axis(n)
    out = np.zeros(n)
    for det in (-1.6, 1.6):  # double course, cents
        ff = f * 2 ** (det / 1200)
        for k in range(1, 9):
            fk = ff * k * (1 + 0.0009 * k * k)  # slight stiffness inharmonicity
            if fk > 14000:
                break
            amp = (1.0 / k ** 1.1) * (1.0 if k == 1 else 0.85) * (bright ** (k / 4))
            dec = 2.2 / (1 + 0.55 * (k - 1)) * (220 / max(f, 110)) ** 0.35
            out += amp * np.sin(2 * np.pi * fk * t + RNG.uniform(0, 6.28)) * np.exp(-t / dec)
    # hammer: short bright noise tick
    tick = hp(noise(ns(0.012)), 2500) * np.linspace(1, 0, ns(0.012)) ** 2
    out[: len(tick)] += 0.35 * tick * bright
    out *= adsr(n, a=0.002, d=0.05, s=1.0, r=0.25)
    return 0.32 * vel * out


def music_box(f, dur=1.6, vel=0.7) -> np.ndarray:
    f = hz(f)
    n = ns(dur + 0.6)
    t = t_axis(n)
    out = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.1)
           + 0.35 * np.sin(2 * np.pi * f * 3.96 * t) * np.exp(-t / 0.35)
           + 0.12 * np.sin(2 * np.pi * f * 8.3 * t) * np.exp(-t / 0.12))
    out[: ns(0.004)] += hp(noise(ns(0.004)), 4000) * 0.2
    return 0.3 * vel * fade(out, 0.001, 0.08)


BELL_PARTIALS = [(0.5, 1.0, 1.0), (1.0, 0.8, 0.8), (1.19, 0.5, 0.6), (1.56, 0.35, 0.45),
                 (2.0, 0.45, 0.4), (2.74, 0.25, 0.3), (3.0, 0.2, 0.25), (4.07, 0.12, 0.18)]


def bell(f, dur=3.0, vel=0.7, partials=BELL_PARTIALS, decay=1.0) -> np.ndarray:
    f = hz(f)
    n = ns(dur)
    t = t_axis(n)
    out = np.zeros(n)
    for ratio, amp, d in partials:
        fk = f * ratio
        if fk > 15000:
            continue
        out += amp * np.sin(2 * np.pi * fk * t + RNG.uniform(0, 6.28)) * np.exp(-t / (d * decay * dur * 0.6))
    return 0.25 * vel * fade(out, 0.001, 0.05)


def chime(f, dur=2.0, vel=0.6) -> np.ndarray:
    """Small glass/brass chime: bright, inharmonic, quick shimmer."""
    return bell(f, dur, vel, partials=[(1, 1, 1), (2.76, 0.5, 0.5), (5.4, 0.25, 0.3), (8.93, 0.12, 0.15)])


# ------------------------------------------------------------------ tabla
def _drum(f0, f1, glide, dur, partials, noise_amt, vel, nlp=3000):
    n = ns(dur)
    t = t_axis(n)
    fc = f1 + (f0 - f1) * np.exp(-t / glide)
    ph = np.cumsum(2 * np.pi * fc / SR)
    out = np.zeros(n)
    for ratio, amp, d in partials:
        out += amp * np.sin(ratio * ph) * np.exp(-t / d)
    nz = lp(noise(n), nlp) * np.exp(-t / 0.015)
    out += noise_amt * nz
    return vel * fade(out, 0.0005, 0.03)


def tabla(bol: str, sa: float = 293.66, vel=0.8) -> np.ndarray:
    """Bols: na, tin, ta, ke, ge, dha, dhin, tun, tit."""
    b = bol.lower()
    dayan_f = sa
    if b in ("na", "ta"):
        x = _drum(dayan_f * 1.06, dayan_f, 0.008, 0.9,
                  [(1, 1.0, 0.35), (2, 0.55, 0.22), (3, 0.35, 0.15), (4, 0.2, 0.08)], 0.25, vel)
    elif b == "tin":
        x = _drum(dayan_f * 1.03, dayan_f, 0.006, 0.6, [(1, 1.0, 0.18), (2, 0.25, 0.1)], 0.12, vel * 0.8)
    elif b == "tun":
        x = _drum(dayan_f * 1.02, dayan_f, 0.01, 1.2, [(1, 1.0, 0.6), (2, 0.15, 0.2)], 0.05, vel * 0.8)
    elif b in ("ke", "ka", "tit"):
        n = ns(0.08)
        x = lp(noise(n), 1800) * np.exp(-t_axis(n) / 0.012) * vel * 0.7
        x = fade(x, 0.0005, 0.01)
    elif b == "ge":
        # bayan: boom whose pitch glides upward (palm pressure)
        x = _drum(75, 105, 0.12, 0.9, [(1, 1.0, 0.45), (2, 0.2, 0.15)], 0.15, vel, nlp=900)
    elif b in ("dha", "dhin"):
        x1 = tabla("na" if b == "dha" else "tin", sa, vel)
        x2 = tabla("ge", sa, vel * 0.9)
        n = max(len(x1), len(x2))
        x = np.zeros(n); x[: len(x1)] += x1; x[: len(x2)] += x2
        x /= 0.35  # sub-calls already scaled
    else:
        x = np.zeros(ns(0.05))
    return 0.35 * x


# ------------------------------------------------------------------ sustained / reeds
def harmonium(f, dur=1.0, vel=0.7, trem=True) -> np.ndarray:
    f = hz(f)
    n = ns(dur + 0.18)
    t = t_axis(n)
    amps = [1.0, 0.75, 0.6, 0.45, 0.38, 0.3, 0.22, 0.18, 0.14, 0.1, 0.08, 0.06]
    out = np.zeros(n)
    for det in (-3.0, 3.5):
        fc = np.full(n, f * 2 ** (det / 1200))
        out += osc_additive(fc, amps, maxf=9000)
    out = lp(out, 3500)
    if trem:
        out *= 1 + 0.07 * np.sin(2 * np.pi * 5.3 * t)
    out *= adsr(n, a=0.06, d=0.1, s=0.9, r=0.18, hold=dur)
    return 0.08 * vel * out


def pad(freqs, dur=4.0, vel=0.5, bright=0.5) -> np.ndarray:
    """Soft string pad: detuned band-limited saws, slow attack, low-passed."""
    n = ns(dur + 1.2)
    t = t_axis(n)
    out = np.zeros(n)
    saw = [1.0 / k for k in range(1, 18)]
    for f in freqs:
        f = hz(f)
        for det in (-7, 0, 6):
            fc = f * 2 ** (det / 1200) * (1 + 0.0015 * np.sin(2 * np.pi * (0.2 + 0.07 * det) * t))
            out += osc_additive(fc, saw, maxf=7000)
    out = lp(out, 900 + 3000 * bright)
    out *= adsr(n, a=min(1.2, dur * 0.4), d=0.3, s=0.9, r=1.2, hold=dur)
    return 0.025 * vel * out / max(1, len(freqs)) ** 0.5


def tanpura(sa: float = 146.83, dur: float = 8.0, vel=0.5, cycle=4.8) -> np.ndarray:
    """Drone: Pa-Sa'-Sa'-Sa (low) cycle, each pluck with jawari brightness bloom."""
    n = ns(dur)
    out = np.zeros(n + ns(5))
    strings = [sa * 1.5 / 2 * 2, sa * 2, sa * 2, sa]  # Pa(mid), Sa, Sa, low Sa
    step = cycle / 4
    k = 0
    tt = 0.0
    while tt < dur:
        f = strings[k % 4]
        m = ns(4.5)
        t = t_axis(m)
        x = np.zeros(m)
        bloom = 0.3 + 0.7 * (1 - np.exp(-t / 0.6)) * np.exp(-t / 3.5)  # jawari: brightness swells
        for h in range(1, 28):
            if f * h > 9000:
                break
            amp = (1 / h) * np.clip(bloom * (1.4 - h / 28), 0, 1) ** (0.5 + h * 0.08)
            x += amp * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h) + RNG.uniform(0, 6.28))
        x *= np.exp(-t / 3.2) * adsr(m, a=0.01, d=0.2, s=1.0, r=0.6)
        i = ns(tt)
        out[i: i + m] += x
        k += 1
        tt += step
    out = out[:n]
    return 0.05 * vel * fade(out, 0.3, 1.0)


# ------------------------------------------------------------------ phrase (legato) instruments
def _curves(notes, n, glide=0.06, artic=0.04, vib_rate=5.2, vib_depth=0.006, vib_delay=0.35):
    """notes: list of (start_s, dur_s, freq, vel). Returns freq curve, amp curve."""
    fcur = np.zeros(n)
    acur = np.zeros(n)
    notes = sorted(notes, key=lambda x: x[0])
    for i, (st, du, f, v) in enumerate(notes):
        f = hz(f)
        a, b = ns(st), min(n, ns(st + du))
        if a >= n:
            continue
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        legato_to_next = nxt is not None and abs(nxt[0] - (st + du)) < 0.03
        end = min(n, ns(nxt[0])) if legato_to_next else b
        seg_t = t_axis(end - a)
        prevf = hz(notes[i - 1][2]) if i > 0 and abs(notes[i - 1][0] + notes[i - 1][1] - st) < 0.03 else f
        g = np.exp(-seg_t / glide) if prevf != f else 0
        fseg = f + (prevf - f) * g
        vib = vib_depth * np.clip((seg_t - vib_delay) / 0.4, 0, 1) * np.sin(2 * np.pi * vib_rate * seg_t)
        fcur[a:end] = fseg * (1 + vib)
        env = np.ones(end - a) * v
        an = ns(artic)
        env[:an] *= np.linspace(0.55 if prevf != f and i > 0 else 0, 1, an)[: end - a]
        if not legato_to_next:
            rn = min(ns(0.12), end - a)
            env[-rn:] *= np.linspace(1, 0, rn)
        acur[a:end] = env
    # fill gaps in pitch so oscillator doesn't jump to 0Hz
    last = hz(notes[0][2]) if notes else 220
    for i in range(n):
        if fcur[i] == 0:
            fcur[i] = last
        else:
            last = fcur[i]
    return fcur, acur


def _phrase_len(notes, tail=0.6):
    return ns(max(s + d for s, d, *_ in notes) + tail)


def bansuri(notes, vel=0.8, breath=0.18) -> np.ndarray:
    n = _phrase_len(notes)
    fc, ac = _curves(notes, n, glide=0.05, vib_depth=0.0055, vib_delay=0.4)
    tone = osc_additive(fc, [1.0, 0.22, 0.09, 0.04], maxf=10000)
    br = bp(noise(n), 1200, 5000) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t_axis(n)))
    chiff = np.zeros(n)
    out = (tone + breath * br) * lp(ac, 40, 1)
    return 0.22 * vel * fade(out, 0.01, 0.1) + chiff


FORMANTS = {
    "a": [(800, 1.0, 80), (1150, 0.5, 90), (2900, 0.25, 120)],
    "o": [(450, 1.0, 70), (800, 0.45, 80), (2830, 0.12, 100)],
    "m": [(250, 1.0, 60), (1100, 0.08, 90), (2300, 0.03, 120)],
    "u": [(325, 1.0, 50), (700, 0.3, 60), (2530, 0.06, 100)],
    "e": [(400, 1.0, 60), (2000, 0.45, 100), (2550, 0.3, 120)],
}


def _formant(x, vowel, shift=1.0):
    out = np.zeros_like(x)
    for f, g, bw in FORMANTS[vowel]:
        f *= shift
        out += g * bp(x, f - bw * 1.2, f + bw * 1.2, order=2)
    return out


def sarangi(notes, vel=0.8) -> np.ndarray:
    n = _phrase_len(notes, 0.8)
    fc, ac = _curves(notes, n, glide=0.11, vib_rate=5.6, vib_depth=0.009, vib_delay=0.25, artic=0.09)
    saw = osc_additive(fc, [1 / k for k in range(1, 30)], maxf=9000)
    bow = 1 + 0.05 * lp(noise(n), 12)
    body = 0.7 * _formant(saw, "a") + 0.3 * _formant(saw, "e")
    out = (body + 0.15 * lp(saw, 2500)) * bow * lp(ac, 25, 1)
    return 0.5 * vel * fade(out, 0.02, 0.2)


def voice(notes, vowel="m", vel=0.8, breathy=0.12, formant_shift=1.0, vib_depth=0.008,
          wobble=0.0, consonant_l=False) -> np.ndarray:
    """Wordless voice: hum ('m'), 'ah' ('a'), 'oo' ('u'). consonant_l: 'la' onsets per note."""
    n = _phrase_len(notes, 0.5)
    fc, ac = _curves(notes, n, glide=0.07, vib_rate=5.0, vib_depth=vib_depth, vib_delay=0.3, artic=0.07)
    if wobble:
        fc = fc * (1 + wobble * lp(noise(n), 6) * 0.5)
    # glottal source ~ -12 dB/oct
    src = osc_additive(fc, [1 / k ** 1.6 for k in range(1, 40)], maxf=8000)
    src += breathy * bp(noise(n), 300, 6000) * 0.4
    out = _formant(src, vowel, formant_shift)
    if vowel == "m":
        out = lp(out + 0.3 * lp(src, 400), 1400)
    if consonant_l:
        # quick dip + brighter onset at each note start: reads as "la"
        for st, du, *_ in notes:
            a = ns(st)
            m = min(ns(0.07), n - a)
            if m > 0:
                out[a: a + m] *= np.linspace(0.25, 1, m)
    out *= lp(ac, 30, 1)
    peak = np.max(np.abs(out)) + 1e-9
    return 0.3 * vel * fade(out / peak, 0.02, 0.15)


# ------------------------------------------------------------------ utility: one-shots into a buffer
class Buf:
    """Stereo accumulation buffer with add-at-time helpers."""

    def __init__(self, seconds: float):
        self.n = ns(seconds)
        self.x = np.zeros((self.n, 2))

    def add(self, t: float, sig: np.ndarray, p: float = 0.0, gain: float = 1.0):
        st = sig if sig.ndim == 2 else pan(sig, p)
        i = ns(t) if t > 0 else 0
        if i >= self.n:
            return
        m = min(len(st), self.n - i)
        self.x[i: i + m] += gain * st[:m]

    def out(self) -> np.ndarray:
        return self.x
