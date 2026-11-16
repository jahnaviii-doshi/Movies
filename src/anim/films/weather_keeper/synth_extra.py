"""Extra instruments for The Weather Keeper of Block C (all synthesized, 48 kHz).

sitar (plucked, jawari buzz, sympathetic shimmer), shehnai (nasal double reed, legato),
trumpet / trombone / tuba (small brass band, legato or stabs), snare, bass drum, dhol boom,
glockenspiel, pizzicato strings, string section (legato lines and sustained chords).
Legato instruments take notes as [(start_s, dur_s, freq_or_name, vel)], like synth.bansuri.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from ...audio import synth as S

SR = S.SR
ns, t_axis, noise, hz = S.ns, S.t_axis, S.noise, S.hz


# ------------------------------------------------------------------ plucked
@lru_cache(maxsize=2048)
def sitar(f: float, dur: float = 2.2, vel: float = 1.0, bright: float = 1.0) -> np.ndarray:
    """Plucked sitar: bright attack, partials whose brightness 'blooms' (jawari) after the pluck,
    plus a faint sympathetic-string halo a fifth/octave above."""
    f = hz(f)
    n = ns(dur)
    t = t_axis(n)
    out = np.zeros(n)
    g = np.random.default_rng(int(f * 10) % 9973)
    bloom = 0.35 + 0.65 * np.clip(t / 0.12, 0, 1) * np.exp(-t / 0.9)   # jawari brightness swell
    for k in range(1, 22):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > 14000:
            break
        amp = (1.0 / k ** 0.85) * (bright if k > 4 else 1.0)
        dec = 0.9 * dur / (1 + 0.18 * k)
        hi = 1.0 if k < 5 else bloom
        out += amp * hi * np.sin(2 * np.pi * fk * t + g.uniform(0, 6.28)) * np.exp(-t / dec)
    # pluck transient
    out[: ns(0.004)] += S.hp(noise(ns(0.004), 3), 2000) * 0.8
    # sympathetic halo
    halo = 0.12 * (np.sin(2 * np.pi * f * 2 * t) + 0.7 * np.sin(2 * np.pi * f * 1.5 * t)) \
        * np.clip(t / 0.25, 0, 1) * np.exp(-t / (dur * 0.6))
    out = out + halo
    return 0.16 * vel * S.fade(out, 0.0005, 0.08)


@lru_cache(maxsize=2048)
def glock(f: float, dur: float = 1.8, vel: float = 1.0) -> np.ndarray:
    f = hz(f)
    n = ns(dur)
    t = t_axis(n)
    out = np.zeros(n)
    for r, a, d in [(1.0, 1.0, 1.0), (2.76, 0.35, 0.35), (5.40, 0.18, 0.15), (8.93, 0.08, 0.08)]:
        if f * r < 16000:
            out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (d * dur * 0.5))
    out[: ns(0.002)] += S.hp(noise(ns(0.002), 5), 4000) * 0.3
    return 0.22 * vel * S.fade(out, 0.0003, 0.05)


@lru_cache(maxsize=2048)
def pizz(f: float, dur: float = 0.7, vel: float = 1.0) -> np.ndarray:
    """Pizzicato string: short Karplus-Strong pluck through a wooden body resonance."""
    f = hz(f)
    n = ns(dur)
    period = SR / f
    p = int(period)
    frac = period - p
    buf = S.lp(noise(p + 2, int(f) % 997), min(6000, f * 8))
    out = np.zeros(n)
    out[: len(buf)] = buf[:n]
    damp = 0.996 - 0.0004 * (f / 200)
    for i in range(p + 1, n):
        out[i] = damp * (0.5 * (1 - frac) * (out[i - p] + out[i - p - 1]) + frac * 0.5 * (out[i - p - 1] + out[i - p - 2 if i - p - 2 >= 0 else 0]))
    body = S.bp(out, 180, 2600) + 0.4 * S.bp(out, 380, 520)
    env = np.exp(-t_axis(n) / (0.12 + 30 / f))
    return 0.5 * vel * S.fade(body * env / (np.max(np.abs(body)) + 1e-9), 0.0005, 0.03)


# ------------------------------------------------------------------ legato reeds & brass
def shehnai(notes, vel=0.8) -> np.ndarray:
    n = S._phrase_len(notes, 0.5)
    fc, ac = S._curves(notes, n, glide=0.09, vib_rate=6.2, vib_depth=0.011, vib_delay=0.18, artic=0.05)
    # reed: strong odd + some even harmonics, nasal formants
    src = S.osc_additive(fc, [1.0, 0.55, 0.9, 0.4, 0.7, 0.3, 0.5, 0.25, 0.35, 0.18, 0.25, 0.12], maxf=11000)
    nasal = 0.6 * S.bp(src, 900, 1500) + 0.5 * S.bp(src, 2300, 3300) + 0.25 * S.lp(src, 700)
    br = S.bp(noise(n), 2500, 7000) * 0.05
    out = (nasal + br) * S.lp(ac, 35, 1)
    out /= (np.max(np.abs(out)) + 1e-9)
    return 0.32 * vel * S.fade(out, 0.01, 0.12)


def _brass(notes, harmonics, lo, hi, vel, vib=0.004, growl=0.0):
    n = S._phrase_len(notes, 0.35)
    fc, ac = S._curves(notes, n, glide=0.03, vib_rate=5.5, vib_depth=vib, vib_delay=0.4, artic=0.03)
    a = S.lp(ac, 40, 1)
    src = S.osc_additive(fc, harmonics, maxf=12000)
    # brightness follows loudness (the brass "blat")
    dark = S.lp(src, lo)
    bright = S.lp(src, hi)
    mixk = np.clip(a, 0, 1) ** 1.5
    out = (dark * (1 - mixk) + bright * mixk) * a
    if growl:
        out *= 1 + growl * np.sin(2 * np.pi * 31 * t_axis(n))
    out /= (np.max(np.abs(out)) + 1e-9)
    return S.fade(out, 0.005, 0.08) * vel


def trumpet(notes, vel=0.8):
    return 0.3 * _brass(notes, [1 / k ** 0.7 for k in range(1, 26)], 1400, 6500, vel)


def trombone(notes, vel=0.8):
    return 0.32 * _brass(notes, [1 / k ** 0.8 for k in range(1, 26)], 700, 3200, vel, vib=0.003)


def tuba(notes, vel=0.8):
    return 0.42 * _brass(notes, [1 / k ** 1.0 for k in range(1, 20)], 300, 1300, vel, vib=0.0015, growl=0.04)


def strings_line(notes, vel=0.8, bright=0.5, voices=5) -> np.ndarray:
    """A legato violin-section line (detuned saw ensemble, slow bow attack)."""
    n = S._phrase_len(notes, 0.9)
    fc, ac = S._curves(notes, n, glide=0.12, vib_rate=5.3, vib_depth=0.006, vib_delay=0.3, artic=0.18)
    out = np.zeros(n)
    g = np.random.default_rng(11)
    for v in range(voices):
        det = 1 + g.uniform(-0.006, 0.006)
        drift = 1 + 0.002 * S.lp(noise(n, 40 + v), 3) * 30
        out += S.osc_additive(fc * det * drift, [1 / k for k in range(1, 18)], maxf=9000)
    out = S.lp(out, 1800 + 3500 * bright) + 0.25 * S.bp(out, 2500, 4500) * bright
    out *= S.lp(ac, 6, 1)
    out /= (np.max(np.abs(out)) + 1e-9)
    return 0.3 * vel * S.fade(out, 0.05, 0.4)


def strings_chord(freqs, dur=4.0, vel=0.6, bright=0.45, attack=0.8) -> np.ndarray:
    n = ns(dur)
    t = t_axis(n)
    out = np.zeros(n)
    g = np.random.default_rng(int(sum(hz(f) for f in freqs)) % 991)
    for f in freqs:
        f = hz(f)
        for v in range(3):
            fc = np.full(n, f * (1 + g.uniform(-0.005, 0.005))) * (1 + 0.004 * np.sin(2 * np.pi * 5.1 * t + v))
            out += S.osc_additive(fc, [1 / k for k in range(1, 14)], maxf=8000)
    out = S.lp(out, 1200 + 3000 * bright)
    env = np.clip(t / attack, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    out = out * env
    return 0.08 * vel * out / (np.sqrt(len(freqs)) + 1e-9) / 3


# ------------------------------------------------------------------ drums
@lru_cache(maxsize=64)
def snare(vel=1.0, brush=False, seed=0) -> np.ndarray:
    n = ns(0.35 if not brush else 0.25)
    t = t_axis(n)
    nz = S.bp(noise(n, 70 + seed), 1500 if not brush else 2500, 9000)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    out = (nz * np.exp(-t / (0.09 if not brush else 0.05)) * (0.7 if brush else 1.0) + (0.0 if brush else 0.6) * body)
    return 0.45 * vel * S.fade(out / (np.max(np.abs(out)) + 1e-9), 0.0005, 0.02)


@lru_cache(maxsize=16)
def kick(vel=1.0) -> np.ndarray:
    n = ns(0.5)
    t = t_axis(n)
    fc = 55 * (1 + 2.2 * np.exp(-t / 0.025))
    x = np.sin(np.cumsum(2 * np.pi * fc / SR)) * np.exp(-t / 0.18)
    x[: ns(0.003)] += S.hp(noise(ns(0.003), 71), 1000) * 0.4
    return 0.5 * vel * S.fade(x / (np.max(np.abs(x)) + 1e-9), 0.0005, 0.03)


@lru_cache(maxsize=16)
def dhol(vel=1.0, low=True) -> np.ndarray:
    """Big festive barrel drum: boomy low side or slappy high side."""
    n = ns(0.9 if low else 0.3)
    t = t_axis(n)
    if low:
        fc = 70 * (1 + 0.8 * np.exp(-t / 0.06))
        x = np.sin(np.cumsum(2 * np.pi * fc / SR)) * np.exp(-t / 0.35) + 0.25 * S.lp(noise(n, 72), 300) * np.exp(-t / 0.05)
    else:
        x = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.04) + 0.6 * S.bp(noise(n, 73), 1500, 6000) * np.exp(-t / 0.02)
    return 0.55 * vel * S.fade(x / (np.max(np.abs(x)) + 1e-9), 0.0005, 0.03)


@lru_cache(maxsize=16)
def cymbal(vel=1.0, dur=2.5) -> np.ndarray:
    n = ns(dur)
    t = t_axis(n)
    x = S.hp(noise(n, 74), 5000) * np.exp(-t / (dur * 0.35))
    x += 0.3 * S.bp(noise(n, 75), 3000, 8000) * np.exp(-t / 0.15)
    return 0.25 * vel * S.fade(x, 0.0005, 0.2)


@lru_cache(maxsize=16)
def timpani(f: float = 98.0, vel=1.0, dur=2.0) -> np.ndarray:
    f = hz(f)
    n = ns(dur)
    t = t_axis(n)
    x = np.zeros(n)
    for r, a in [(1.0, 1.0), (1.5, 0.5), (1.98, 0.35), (2.44, 0.2)]:
        x += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (0.7 / r))
    x += 0.3 * S.lp(noise(n, 76), 500) * np.exp(-t / 0.03)
    return 0.5 * vel * S.fade(x / (np.max(np.abs(x)) + 1e-9), 0.0005, 0.1)
