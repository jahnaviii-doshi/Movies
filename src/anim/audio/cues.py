"""Scene cues, all built from the three leitmotifs so the score plays as one piece.

render_cue(cue_id, duration, hits) -> (N, 2) float32 at 48 kHz.
`hits` are seconds into the cue for accents/swells (story beats: the power cut, the shop
blazing, Tola's THUNK...). Cues are duration-flexible: phrases loop/extend, ends fade.
"""
from __future__ import annotations

import warnings
from functools import lru_cache

import numpy as np

from . import synth as S
from .motifs import (SA, LULLABY, LULLABY_BPM, LULLABY_CHORDS, LULLABY_ENDED, SWAGGER, SWAGGER_BASS,
                     SWAGGER_BPM, WONDER, WONDER_BPM, WONDER_CHORDS, WONDER_OSTINATO, beats_len,
                     motif_seconds, seq, tender)

SR = S.SR


# ------------------------------------------------------------------ cached one-shots
@lru_cache(maxsize=4096)
def _santoor(f: float, dur: float, bright: float) -> np.ndarray:
    return S.santoor(f, dur, 1.0, bright)


@lru_cache(maxsize=2048)
def _mbox(f: float) -> np.ndarray:
    return S.music_box(f, 1.6, 1.0)


@lru_cache(maxsize=1024)
def _bell(f: float, dur: float) -> np.ndarray:
    return S.bell(f, dur, 1.0)


@lru_cache(maxsize=1024)
def _chime(f: float) -> np.ndarray:
    return S.chime(f, 2.0, 1.0)


@lru_cache(maxsize=256)
def _tabla(bol: str) -> np.ndarray:
    return S.tabla(bol, 293.66, 1.0)


@lru_cache(maxsize=2048)
def _harm(f: float, dur: float) -> np.ndarray:
    return S.harmonium(f, dur, 1.0)


def _r(f):  # quantize for caching
    return round(float(f), 2)


# ------------------------------------------------------------------ placement helpers
def place_plucked(buf: S.Buf, notes, inst="santoor", p=-0.25, gain=1.0, bright=1.0):
    for st, du, f, v in notes:
        if inst == "santoor":
            x = _santoor(_r(f), round(min(du + 0.8, 3.0), 1), bright)
        elif inst == "musicbox":
            x = _mbox(_r(f))
        elif inst == "chime":
            x = _chime(_r(f))
        elif inst == "bell":
            x = _bell(_r(f), 3.0)
        elif inst == "harmonium":
            x = _harm(_r(f), round(du, 2))
        else:
            raise ValueError(inst)
        buf.add(st, x * v, p, gain)


def place_legato(buf: S.Buf, notes, inst="bansuri", p=0.2, gain=1.0, **kw):
    if not notes:
        return
    t0 = notes[0][0]
    rel = [(st - t0, du, f, v) for st, du, f, v in notes]
    if inst == "bansuri":
        x = S.bansuri(rel, **kw)
    elif inst == "sarangi":
        x = S.sarangi(rel, **kw)
    elif inst == "hum":
        x = S.voice(rel, "m", wobble=0.004, **kw)
    elif inst == "ah":
        x = S.voice(rel, "a", **kw)
    elif inst == "oo":
        x = S.voice(rel, "u", **kw)
    elif inst == "la":
        x = S.voice(rel, "a", consonant_l=True, **kw)
    else:
        raise ValueError(inst)
    buf.add(t0, x, p, gain)


def place_pad(buf, t, chord, dur, gain=1.0, bright=0.4, wide=True):
    x = S.pad(chord, dur, 1.0, bright)
    if wide:
        buf.add(t, x, -0.55, gain * 0.75)
        buf.add(t + 0.013, x, 0.55, gain * 0.75)
    else:
        buf.add(t, x, 0.0, gain)


def drone(buf, D, gain=1.0, start=0.0):
    buf.add(start, S.tanpura(SA, D - start + 0.5), 0.0, gain)


KEHERWA = ["dha", "ge", "na", "tin", "na", "ke", "dhin", "na"]          # 8 eighths
DADRA = ["dha", "dhin", "na", "dha", "tin", "na"]                     # 6 eighths (3/4 feel)
TIPTOE = ["ke", None, "tit", None, "ke", "tit", None, "na"]


def tabla_groove(buf, t0, t1, bpm, pattern=KEHERWA, gain=1.0, swing=0.0, p=0.15, fill_every=4):
    eighth = 30.0 / bpm
    i = 0
    t = t0
    bar = 0
    while t < t1 - 0.05:
        bol = pattern[i % len(pattern)]
        if fill_every and (i // len(pattern)) % fill_every == fill_every - 1 and i % len(pattern) >= len(pattern) - 3:
            bol = ["tit", "ke", "dha"][(i % len(pattern)) - (len(pattern) - 3)]
        if bol:
            off = swing * eighth * 0.5 if i % 2 else 0.0
            v = 1.0 if i % len(pattern) == 0 else 0.72 + 0.1 * ((i * 13) % 5) / 5
            buf.add(t + off, _tabla(bol) * v, p, gain)
        i += 1
        t = t0 + i * eighth
        bar = i // len(pattern)
    return bar


def ostinato(buf, t0, t1, bpm, notes=WONDER_OSTINATO, gain=1.0, p=-0.35, octave=0, bright=0.9):
    eighth = 30.0 / bpm
    i = 0
    while t0 + i * eighth < t1 - 0.05:
        f = S.hz(notes[i % len(notes)]) * 2 ** octave
        v = 0.85 if i % len(notes) == 0 else 0.6 + 0.15 * ((i * 7) % 3) / 2
        buf.add(t0 + i * eighth, _santoor(_r(f), 1.2, bright) * v, p, gain)
        i += 1


def chords_loop(buf, t0, t1, chords, bar_s, gain=1.0, bright=0.4):
    i = 0
    t = t0
    while t < t1 - 0.2:
        place_pad(buf, t, chords[i % len(chords)], min(bar_s, t1 - t), gain, bright)
        i += 1
        t += bar_s


def lullaby(buf, t, inst, gain=1.0, bpm=LULLABY_BPM, octave=0, resolve=False, p=0.15, transpose=0,
            chords=True, chord_gain=0.8, vel=0.8, **kw):
    motif = LULLABY_ENDED if resolve else LULLABY
    notes = seq(motif, t, bpm, transpose=transpose, octave=octave, vel=vel)
    if inst in ("santoor", "musicbox", "chime", "bell", "harmonium"):
        place_plucked(buf, notes, inst, p, gain)
    else:
        place_legato(buf, notes, inst, p, gain, **kw)
    beat = 60.0 / bpm
    if chords:
        cs = LULLABY_CHORDS if not resolve else LULLABY_CHORDS[:2] + [(6, ["A2", "C#3", "E3"]), (8, ["D3", "F#3", "A3"])]
        for i, (b, ch) in enumerate(cs):
            nb = cs[i + 1][0] if i + 1 < len(cs) else beats_len(motif) + 1
            ch = [S.hz(c) * 2 ** (transpose / 12) for c in ch]
            place_pad(buf, t + b * beat, ch, (nb - b) * beat, chord_gain)
    return motif_seconds(motif, bpm)


def wonder(buf, t, inst="bansuri", gain=1.0, bpm=WONDER_BPM, octave=0, p=0.25, vel=0.85, **kw):
    notes = seq(WONDER, t, bpm, octave=octave, vel=vel)
    if inst in ("santoor", "musicbox", "chime", "bell"):
        place_plucked(buf, notes, inst, p, gain)
    else:
        place_legato(buf, notes, inst, p, gain, **kw)
    return motif_seconds(WONDER, bpm)


def swagger(buf, t, inst="harmonium", gain=1.0, bpm=SWAGGER_BPM, swing=0.3, is_tender=False, octave=0,
            p=-0.1, vel=0.85, legato=0.85, **kw):
    motif = tender(SWAGGER) if is_tender else SWAGGER
    notes = seq(motif, t, bpm, swing=swing, octave=octave, vel=vel, legato=legato)
    if inst in ("santoor", "musicbox", "harmonium", "chime"):
        place_plucked(buf, notes, inst, p, gain)
    else:
        place_legato(buf, notes, inst, p, gain, **kw)
    return motif_seconds(motif, bpm)


def swagger_bass(buf, t0, t1, bpm, gain=1.0, is_tender=False):
    q = 60.0 / bpm
    i = 0
    while t0 + i * q < t1 - 0.05:
        n = SWAGGER_BASS[i % len(SWAGGER_BASS)]
        if is_tender:
            n = n.replace("C3", "C#3")
        buf.add(t0 + i * q, _santoor(_r(S.hz(n)), 1.0, 0.5) * 0.9, -0.05, gain)
        i += 1


# ------------------------------------------------------------------ hits
def hit(buf, t, kind="swell", gain=1.0):
    if kind == "swell":
        place_pad(buf, max(0, t - 1.6), ["D3", "A3", "D4", "F#4"], 3.5, gain * 1.6, bright=0.7)
        buf.add(t, _bell(_r(S.hz("D5")), 3.0) * 0.6, 0.3, gain)
        buf.add(t, _bell(_r(S.hz("A4")), 3.0) * 0.5, -0.3, gain)
    elif kind == "sparkle":
        for i, n in enumerate(["D6", "E6", "F#6", "A6", "B6", "D7"]):
            buf.add(t + i * 0.045, _mbox(_r(S.hz(n))) * 0.5, -0.6 + i * 0.24, gain)
    elif kind == "boom":
        buf.add(t, _tabla("ge") * 1.4, 0.0, gain)
        buf.add(t, _bell(_r(S.hz("D3")), 3.0) * 0.6, 0.0, gain)
    elif kind == "drop":  # music falls away (power cut)
        pass


def cue_out(buf: S.Buf, D: float, wet=0.25, size=2.4, bright=0.5, level=0.08, fade_out=1.5, fade_in=0.3):
    x = S.reverb(buf.out(), wet, size, bright)[: S.ns(D)]
    if len(x) < S.ns(D):
        x = np.vstack([x, np.zeros((S.ns(D) - len(x), 2))])
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    x = x * (level / rms)
    pk = np.max(np.abs(x))
    if pk > 0.89:
        x = x * (0.89 / pk)
    return S.fade(x, min(fade_in, D / 4), min(fade_out, D / 3)).astype(np.float32)


# ------------------------------------------------------------------ cues
def c_dusk(D, hits):
    b = S.Buf(D + 3)
    cut = hits[0] if hits else D
    drone(b, D, 1.0)
    # heat-hazy santoor arpeggios of the lullaby notes, slow, until the power cut
    t, i = 0.5, 0
    pool = ["D4", "A4", "B4", "F#4", "A4", "E4", "D5", "B4"]
    while t < cut - 0.3:
        b.add(t, _santoor(_r(S.hz(pool[i % 8])), 2.0, 0.7) * 0.55, -0.3 + 0.6 * ((i * 3) % 5) / 4)
        t += 0.9 if i % 4 != 3 else 1.8
        i += 1
    place_pad(b, 0, ["D3", "A3", "E4"], min(cut, D), 0.9, 0.3)
    if hits:  # after the cut: only the drone, darker
        x = b.out()
        k = S.ns(cut)
        x[k:] *= np.linspace(1, 0.15, len(x) - k)[:, None] ** 2
        b2 = S.Buf(D + 3)
        b2.x = x
        b2.add(cut + 0.4, S.tanpura(SA, max(0.5, D - cut)), 0.0, 0.5)
        b = b2
    return cue_out(b, D, 0.3, 3.0, 0.4, 0.06)


def c_rooftop_story(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.7)
    chords_loop(b, 0, D, [["D3", "F#3", "A3"], ["B2", "D3", "F#3"], ["G2", "B2", "D3"], ["A2", "D3", "E3"]],
                4 * 60 / 66, 0.9, 0.3)
    t = 2.0
    while t < D - 4:
        t += lullaby(b, t, "musicbox", 0.35, chords=False, octave=1) + 6.0
    return cue_out(b, D, 0.3, 2.8, 0.4, 0.045)


def c_midnight_mystery(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    lows = ["D3", "A2", "B2", "F#2"]
    t, i = 0.0, 0
    while t < D - 0.5:
        b.add(t, _santoor(_r(S.hz(lows[i % 4])), 1.5, 0.5) * 0.7, -0.2)
        b.add(t + 0.75, _santoor(_r(S.hz(lows[i % 4]) * 1.5), 1.0, 0.5) * 0.35, 0.2)
        t += 1.5
        i += 1
    t = 3.0
    while t < D - 3:
        notes = seq(LULLABY[:3], t, 80, octave=1, vel=0.5)
        place_plucked(b, notes, "musicbox", 0.4, 0.5)
        t += 9.0
    for h in hits:
        hit(b, h, "sparkle", 0.8)
    return cue_out(b, D, 0.35, 3.2, 0.45, 0.04)


def c_wonder_unfold(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    build = min(D * 0.35, 6.0)
    # shimmering build: rising music-box sparkles that accelerate
    t, gap = 0.2, 0.45
    i = 0
    while t < build:
        n = WONDER_OSTINATO[i % 8]
        b.add(t, _mbox(_r(S.hz(n) * 2)) * (0.3 + 0.5 * t / build), -0.5 + (i % 5) * 0.25)
        t += gap
        gap = max(0.1, gap * 0.9)
        i += 1
    place_pad(b, 0, ["D3", "A3", "D4", "E4"], build + 1.0, 1.2, 0.5)
    ostinato(b, build, D, WONDER_BPM, gain=0.9)
    chords_loop(b, build, D, WONDER_CHORDS, 4 * 60 / WONDER_BPM, 1.0, 0.5)
    t = build + 4 * 60 / WONDER_BPM * 0.5
    while t < D - 3:
        t += wonder(b, t, "bansuri", 1.0) + 1.25
    tabla_groove(b, build + 4 * 60 / WONDER_BPM * 2, D, WONDER_BPM, gain=0.5)
    hit(b, build, "swell", 1.0)
    for h in hits:
        hit(b, h, "sparkle", 1.0)
    return cue_out(b, D, 0.28, 2.6, 0.55, 0.085)


def c_shop_warm(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    chords_loop(b, 0, D, [["D3", "F#3", "A3"], ["G2", "B2", "D3"], ["B2", "D3", "F#3"], ["A2", "C#3", "E3"]],
                4 * 60 / 80, 0.8, 0.35)
    t = 0.5
    k = 0
    while t < D - 3:
        if k % 2 == 0:
            t += lullaby(b, t, "santoor", 0.75, bpm=80, chords=False) + 1.5
        else:
            notes = seq(LULLABY, t, 80, octave=0, vel=0.6)
            place_plucked(b, notes, "harmonium", 0.0, 0.5)
            t += motif_seconds(LULLABY, 80) + 1.5
        k += 1
    tabla_groove(b, 1.5, D, 80, DADRA, gain=0.28)
    for h in hits:
        hit(b, h, "sparkle", 0.8)
    return cue_out(b, D, 0.3, 2.2, 0.5, 0.06)


def c_flight(D, hits):
    b = S.Buf(D + 3)
    bpm = WONDER_BPM
    bar = 4 * 60 / bpm
    drone(b, D, 0.5)
    ostinato(b, 0, D, bpm, gain=0.95)
    ostinato(b, bar * 4, D, bpm, gain=0.4, octave=1, p=0.45, bright=1.0)
    chords_loop(b, 0, D, WONDER_CHORDS, bar, 1.2, 0.6)
    tabla_groove(b, bar * 2, D, bpm, gain=0.65)
    t, k = bar, 0
    while t < D - 3:
        inst = "bansuri" if k % 2 == 0 else "sarangi"
        t += wonder(b, t, inst, 1.0 if inst == "bansuri" else 0.7, octave=0) + (bar if k % 2 else 0)
        k += 1
    for h in hits:
        hit(b, h, "swell", 1.0)
    return cue_out(b, D, 0.3, 2.8, 0.6, 0.095)


def c_dawn_soft(D, hits):
    b = S.Buf(D + 3)
    place_pad(b, 0, ["D3", "A3", "F#4"], D, 1.0, 0.35)
    t = 1.0
    while t < D - 4:
        t += lullaby(b, t, "santoor", 0.6, bpm=60, chords=False) + 3.0
    return cue_out(b, D, 0.35, 3.0, 0.45, 0.04)


def c_swagger(D, hits):
    b = S.Buf(D + 3)
    bpm = SWAGGER_BPM
    two_bars = 8 * 60 / bpm
    swagger_bass(b, 0, D, bpm, 0.9)
    tabla_groove(b, 0, D, bpm, KEHERWA, gain=0.7, swing=0.3)
    t, k = 0.0, 0
    while t < D - 1:
        swagger(b, t, "harmonium", 0.9)
        if k % 2 == 1:
            swagger(b, t, "santoor", 0.5, octave=1, p=0.35)
        t += two_bars
        k += 1
    for h in hits:
        hit(b, h, "boom", 0.8)
    return cue_out(b, D, 0.18, 1.6, 0.6, 0.08)


def c_deflate(D, hits):
    b = S.Buf(D + 3)
    # sad trombone-ish sarangi slide down: B4 A4 G#4 G4~
    notes = [(0.0, 0.45, S.hz("B4"), 0.8), (0.45, 0.45, S.hz("A4"), 0.75), (0.9, 0.45, S.hz("G#4"), 0.7),
             (1.35, 1.4, S.hz("G4"), 0.7)]
    place_legato(b, notes, "sarangi", 0.0, 1.0)
    if D > 3.5:
        place_pad(b, 2.4, ["G2", "B2", "D3"], D - 2.4, 0.7, 0.3)
    return cue_out(b, D, 0.2, 1.8, 0.5, 0.05, fade_out=0.8)


def c_montage(D, hits):
    b = S.Buf(D + 3)
    bpm = 112
    bar = 4 * 60 / bpm
    ostinato(b, 0, D, bpm, gain=0.7, bright=1.0)
    tabla_groove(b, 0, D, bpm, KEHERWA, gain=0.6)
    chords_loop(b, 0, D, WONDER_CHORDS, bar, 0.7, 0.5)
    t, k = bar, 0
    while t < D - 2:
        inst = ["santoor", "bansuri", "musicbox", "bansuri"][k % 4]
        t += wonder(b, t, inst, 0.8 if inst != "musicbox" else 0.5, bpm=bpm, octave=1 if inst == "musicbox" else 0) + bar
        k += 1
    for h in hits:
        hit(b, h, "sparkle", 0.8)
    return cue_out(b, D, 0.22, 2.0, 0.6, 0.075)


def c_brave(D, hits):
    b = S.Buf(D + 3)
    bpm = 70
    bar = 4 * 60 / bpm
    drone(b, D, 0.8)
    # heroic: bayan booms on the beat, wonder theme augmented low on sarangi, pad climbing
    t, i = 0.0, 0
    while t < D - 0.3:
        b.add(t, _tabla("ge") * (1.2 if i % 4 == 0 else 0.7), 0.0, 1.0)
        if i % 4 == 0:
            b.add(t, _bell(_r(S.hz("D3")), 3.0) * 0.3, 0.0)
        t += 60 / bpm
        i += 1
    chords_loop(b, 0, D, [["D3", "A3"], ["B2", "F#3"], ["G2", "D3"], ["A2", "E3"]], bar, 1.4, 0.55)
    t = bar * 0.5
    while t < D - 3:
        t += wonder(b, t, "sarangi", 1.0, bpm=bpm, octave=-1) + bar
    for h in hits:
        hit(b, h, "swell", 1.2)
        hit(b, h, "boom", 1.0)
    return cue_out(b, D, 0.3, 2.5, 0.5, 0.085)


def c_chutney_tender(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    t = 0.5
    while t < D - 3:
        t += lullaby(b, t, "bansuri", 0.8, bpm=58, chord_gain=0.8) + 2.0
    return cue_out(b, D, 0.32, 2.6, 0.45, 0.05)


def c_fading(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    chords_loop(b, 0, D, [["B2", "D3", "F#3"], ["G2", "B2", "D3"], ["E2", "G2", "B2"], ["F#2", "A#2", "C#3"]],
                4 * 60 / 60, 0.9, 0.25)
    t = 1.0
    k = 0
    while t < D - 3:
        # the lullaby on music box, slowing like a winding-down box
        bpm = 60 - 6 * k
        notes = seq(LULLABY, t, max(40, bpm), octave=1, vel=0.55)
        notes = [(st + 0.04 * j * j, du, f * 0.997 ** j, v * (0.95 ** j)) for j, (st, du, f, v) in enumerate(notes)]
        place_plucked(b, notes, "musicbox", 0.35, 0.6)
        t += motif_seconds(LULLABY, max(40, bpm)) + 4.0
        k += 1
    return cue_out(b, D, 0.4, 3.4, 0.4, 0.045)


def c_sneak(D, hits):
    b = S.Buf(D + 3)
    bpm = 118
    e = 30 / bpm
    pat = ["D3", None, "F#3", None, "G3", "G#3", "A3", None, "D3", None, "F#3", None, "A3", "G#3", "G3", None]
    i = 0
    while i * e < D - 0.3:
        n = pat[i % len(pat)]
        if n:
            b.add(i * e, _santoor(_r(S.hz(n)), 0.5, 0.4) * 0.8, -0.15)
        i += 1
    tabla_groove(b, 0, D, bpm, TIPTOE, gain=0.5, fill_every=0)
    for h in hits:
        hit(b, h, "boom", 0.7)
    return cue_out(b, D, 0.15, 1.5, 0.5, 0.06)


def c_wish_chaos(D, hits):
    b = S.Buf(D + 3)
    bpm = 132
    two_bars = 8 * 60 / bpm
    swagger_bass(b, 0, D, bpm, 0.9)
    tabla_groove(b, 0, D, bpm, KEHERWA, gain=0.75, swing=0.2, fill_every=2)
    ostinato(b, 0, D, bpm, gain=0.35, octave=1, bright=1.0)
    t, k = 0.0, 0
    while t < D - 1:
        inst = ["harmonium", "santoor", "bansuri", "harmonium"][k % 4]
        swagger(b, t, inst, 0.85, bpm=bpm, octave=1 if inst == "santoor" else 0)
        t += two_bars
        k += 1
    for h in hits:
        hit(b, h, "sparkle", 1.0)
        hit(b, h, "boom", 0.8)
    return cue_out(b, D, 0.18, 1.6, 0.6, 0.085)


def c_crystal_sting(D, hits):
    b = S.Buf(D + 3)
    for i, n in enumerate(["B5", "C#6", "F#6", "D6", "G6", "C#7"]):
        b.add(0.05 * i, _chime(_r(S.hz(n))) * 0.6, -0.6 + 0.24 * i)
    place_pad(b, 0, ["B2", "F#3", "C#4", "D4"], D, 1.3, 0.35)
    b.add(0, _tabla("ge") * 0.8, 0)
    t = 1.5
    while t < D - 1:
        b.add(t, _chime(_r(S.hz(["F#6", "C#7", "D6"][int(t) % 3]))) * 0.35, 0.5 - (t % 2) * 0.5)
        t += 1.3
    return cue_out(b, D, 0.4, 3.0, 0.6, 0.05)


def c_low_point(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.55)
    # same six notes, sorrowful harmony underneath (Bm - Em - G)
    t = 1.0
    while t < D - 4:
        notes = seq(LULLABY, t, 50, vel=0.75)
        place_legato(b, notes, "sarangi", 0.1, 0.8)
        beat = 60 / 50
        for bb, ch in [(0, ["B2", "D3", "F#3"]), (3, ["E2", "G2", "B2"]), (6, ["G2", "B2", "E3"])]:
            place_pad(b, t + bb * beat, ch, 3 * beat, 0.9, 0.25)
        t += motif_seconds(LULLABY, 50) + 3.0
    return cue_out(b, D, 0.38, 3.2, 0.4, 0.05)


def c_stairs_tender(D, hits):
    b = S.Buf(D + 3)
    bpm = 60
    two_bars = 8 * 60 / bpm
    place_pad(b, 0, ["D3", "F#3", "A3"], D, 0.9, 0.3)
    t, k = 0.5, 0
    while t < D - 2:
        swagger(b, t, "harmonium", 0.75, bpm=bpm, swing=0.0, is_tender=True, legato=1.0)
        if k >= 1:
            swagger(b, t, "santoor", 0.35, bpm=bpm, swing=0.0, is_tender=True, octave=1, p=0.4)
        t += two_bars
        k += 1
    # one soft pulse per beat: one step at a time
    i = 0
    while i < D - 0.5:
        b.add(i, _tabla("tun") * 0.35, 0.1)
        i += 1
    return cue_out(b, D, 0.3, 2.6, 0.45, 0.05)


def c_wall_hum(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    place_pad(b, 0, ["D3", "A3"], D, 0.6, 0.2)
    for h in hits:
        hit(b, h, "sparkle", 0.5)
    return cue_out(b, D, 0.4, 3.5, 0.35, 0.03)


def c_memory(D, hits):
    b = S.Buf(D + 3)
    place_pad(b, 0, ["D3", "F#3", "A3", "E4"], D, 0.9, 0.25)
    t = 0.5
    while t < D - 3:
        t += lullaby(b, t, "musicbox", 0.45, bpm=60, chords=False, octave=1) + 1.5
    return cue_out(b, D, 0.45, 3.6, 0.35, 0.04)


def c_blaze(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.8)
    h0 = hits[0] if hits else min(1.0, D * 0.1)
    # build to the hit, then the lullaby in full with its ending, then the wonder theme
    place_pad(b, 0, ["D3", "A3", "D4"], h0 + 0.5, 1.0, 0.6)
    hit(b, h0, "swell", 1.5)
    hit(b, h0, "sparkle", 1.2)
    hit(b, h0, "boom", 1.2)
    t = h0 + 0.3
    bpm = 72
    ostinato(b, t, D, bpm, gain=0.6, bright=1.0)
    t += lullaby(b, t, "ah", 0.9, bpm=bpm, resolve=True, chord_gain=1.3, octave=0, formant_shift=1.15, vel=0.9)
    lullaby(b, h0 + 0.3, "santoor", 0.5, bpm=bpm, resolve=True, chords=False, octave=1)
    tabla_groove(b, t, D, WONDER_BPM, gain=0.6)
    chords_loop(b, t, D, WONDER_CHORDS, 4 * 60 / WONDER_BPM, 1.3, 0.65)
    while t < D - 3:
        t += wonder(b, t, "bansuri", 1.0) + 0.5
    for h in hits[1:]:
        hit(b, h, "swell", 1.2)
    return cue_out(b, D, 0.3, 3.0, 0.6, 0.1)


def c_heavy(D, hits):
    b = S.Buf(D + 3)
    bpm = 76
    two_bars = 8 * 60 / bpm
    h0 = hits[0] if hits else 0.0
    drone(b, D, 0.6)
    chords_loop(b, 0, D, [["D3", "F#3", "A3"], ["G2", "B2", "D3"], ["A2", "C#3", "E3"], ["D3", "F#3", "A3"]],
                4 * 60 / bpm, 1.1, 0.5)
    t, k = 0.0, 0
    while t < D - 2:
        swagger(b, t, "harmonium", 0.9, bpm=bpm, swing=0.0, is_tender=True, legato=1.0)
        swagger(b, t, "bansuri", 0.75, bpm=bpm, swing=0.0, is_tender=True, octave=1, p=0.3)
        t += two_bars
        k += 1
    tabla_groove(b, 0, D, bpm, KEHERWA, gain=0.5)
    hit(b, h0, "boom", 1.4)
    hit(b, h0, "swell", 1.3)
    for h in hits[1:]:
        hit(b, h, "sparkle", 1.0)
    return cue_out(b, D, 0.28, 2.6, 0.55, 0.09)


def c_dawn_farewell(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    t, k = 0.5, 0
    while t < D - 4:
        inst = "bansuri" if k % 2 == 0 else "santoor"
        t += lullaby(b, t, inst, 0.8 if inst == "bansuri" else 0.7, bpm=56, resolve=True, chord_gain=1.0) + 2.0
        k += 1
    return cue_out(b, D, 0.35, 3.2, 0.5, 0.055)


def c_walk_home(D, hits):
    b = S.Buf(D + 3)
    bpm = 84
    bar = 4 * 60 / bpm
    ostinato(b, 0, D, bpm, gain=0.7, bright=0.8)
    chords_loop(b, 0, D, WONDER_CHORDS, bar, 0.9, 0.45)
    tabla_groove(b, bar, D, bpm, KEHERWA, gain=0.4)
    t = bar
    while t < D - 3:
        t += wonder(b, t, "bansuri", 0.85, bpm=bpm) + bar
    return cue_out(b, D, 0.3, 2.6, 0.5, 0.065)


def c_coda(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    t, k = 0.5, 0
    while t < D - 4:
        inst = "santoor" if k % 2 == 0 else "musicbox"
        t += lullaby(b, t, inst, 0.7, bpm=60, resolve=True, chord_gain=0.8, octave=0 if k % 2 == 0 else 1) + 2.0
        k += 1
    for h in hits:
        hit(b, h, "sparkle", 0.7)
    return cue_out(b, D, 0.35, 3.0, 0.45, 0.045)


def c_credits(D, hits):
    b = S.Buf(D + 3)
    bpm = WONDER_BPM
    bar = 4 * 60 / bpm
    sections = []
    t = 0.0
    # A: wonder theme full | B: swagger interlude | C: lullaby with ending, then repeat
    while t < D - 2:
        sec_len = min(bar * 8, D - t)
        sections.append(("wonder", t, sec_len)); t += sec_len
        if t >= D - 2:
            break
        sl = min(8 * 60 / SWAGGER_BPM * 2, D - t)
        sections.append(("swagger", t, sl)); t += sl
        if t >= D - 2:
            break
        sl = min(motif_seconds(LULLABY_ENDED, 66) + 2, D - t)
        sections.append(("lullaby", t, sl)); t += sl
    for kind, t0, L in sections:
        t1 = t0 + L
        if kind == "wonder":
            drone(b, t1, 0.4, start=t0)
            ostinato(b, t0, t1, bpm, gain=0.9)
            chords_loop(b, t0, t1, WONDER_CHORDS, bar, 1.2, 0.6)
            tabla_groove(b, t0 + bar, t1, bpm, gain=0.6)
            tt = t0 + bar * 0.5
            k = 0
            while tt < t1 - 3:
                tt += wonder(b, tt, "bansuri" if k % 2 == 0 else "sarangi", 0.9) + 0.25
                k += 1
        elif kind == "swagger":
            swagger_bass(b, t0, t1, SWAGGER_BPM, 0.8)
            tabla_groove(b, t0, t1, SWAGGER_BPM, gain=0.6, swing=0.3)
            tt = t0
            while tt < t1 - 1:
                tt += swagger(b, tt, "harmonium", 0.85)
        else:
            lullaby(b, t0 + 0.3, "santoor", 0.8, bpm=66, resolve=True, chord_gain=1.0)
            lullaby(b, t0 + 0.3, "ah", 0.45, bpm=66, resolve=True, chords=False, octave=0, formant_shift=1.1)
    return cue_out(b, D, 0.28, 2.6, 0.55, 0.08, fade_out=3.0)


def c_postcredits(D, hits):
    b = S.Buf(D + 3)
    notes = seq(SWAGGER[:9], 0.3, 120, octave=1, vel=0.6, legato=0.6)
    place_plucked(b, notes, "musicbox", 0.0, 0.8)
    t = motif_seconds(SWAGGER[:9], 120) + 0.6
    # floating away: rising sparkles
    i = 0
    while t < D - 0.5:
        b.add(t, _mbox(_r(S.hz("D5") * 2 ** (i / 12 * 2))) * 0.5, -0.5 + (i % 5) * 0.25)
        t += 0.22
        i += 1
    return cue_out(b, D, 0.25, 2.0, 0.6, 0.05)


def c_generic(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    place_pad(b, 0, ["D3", "F#3", "A3"], D, 0.9, 0.3)
    t = 1.0
    while t < D - 4:
        t += lullaby(b, t, "santoor", 0.5, bpm=60, chords=False) + 4.0
    return cue_out(b, D, 0.3, 2.8, 0.45, 0.04)


CUES = {
    "dusk": c_dusk, "rooftop_story": c_rooftop_story, "midnight_mystery": c_midnight_mystery,
    "wonder_unfold": c_wonder_unfold, "shop_warm": c_shop_warm, "flight": c_flight, "dawn_soft": c_dawn_soft,
    "swagger": c_swagger, "deflate": c_deflate, "montage": c_montage, "brave": c_brave,
    "chutney_tender": c_chutney_tender, "fading": c_fading, "sneak": c_sneak, "wish_chaos": c_wish_chaos,
    "crystal_sting": c_crystal_sting, "low_point": c_low_point, "stairs_tender": c_stairs_tender,
    "wall_hum": c_wall_hum, "memory": c_memory, "blaze": c_blaze, "heavy": c_heavy,
    "dawn_farewell": c_dawn_farewell, "walk_home": c_walk_home, "coda": c_coda, "credits": c_credits,
    "postcredits": c_postcredits,
}


def _film_cues() -> dict:
    """Cues of the current film (FILM env), from anim.films.<slug>.cues.CUES; {} for film 1."""
    import importlib
    import os
    film = os.environ.get("FILM", "midnight_sweet_shop")
    if film == "midnight_sweet_shop":
        return {}
    try:
        return importlib.import_module(f"anim.films.{film}.cues").CUES
    except ModuleNotFoundError:
        return {}


def render_cue(cue_id: str, duration: float, hits: list[float] | None = None) -> np.ndarray:
    hits = sorted(h for h in (hits or []) if 0 <= h <= duration)
    if duration <= 0.05 or cue_id == "":
        return np.zeros((S.ns(max(duration, 0.0)), 2), dtype=np.float32)
    fn = _film_cues().get(cue_id) or CUES.get(cue_id)
    if fn is None:
        warnings.warn(f"unknown cue {cue_id!r}: using generic lullaby bed")
        fn = c_generic
    x = fn(float(duration), hits)
    n = S.ns(duration)
    if len(x) < n:
        x = np.vstack([x, np.zeros((n - len(x), 2), np.float32)])
    return np.nan_to_num(x[:n]).astype(np.float32)
