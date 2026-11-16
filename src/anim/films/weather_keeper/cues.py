"""Score cues for The Weather Keeper of Block C. All built from the three leitmotifs
(motifs.py) so the score plays as one piece.

CUES[cue_id](duration, hits) -> (N, 2) float32 @ 48 kHz. `hits` = seconds into the cue for
story accents (see each cue's docstring). Unknown ids fall back to a Keeper's-theme bed via
the defaultdict-like CUES.get wrapper used by the shared engine (see FallbackCues below).
"""
from __future__ import annotations

import numpy as np

from ...audio import synth as S
from ...audio.cues import (DADRA, KEHERWA, TIPTOE, _bell, _chime, _harm, _mbox, _r, _santoor, _tabla, chords_loop,
                           cue_out, place_pad, tabla_groove)
from . import synth_extra as X
from .motifs import (BHAAP, BHAAP_BASS, BHAAP_BPM, BHAAP_CHORDS, KEEPER, KEEPER_BPM, KEEPER_CHORDS, KEEPER_V2,
                     KEEPER_V3, MONSOON, MONSOON_BPM, MONSOON_CHORDS, MONSOON_HINT, SA_G, bhaap_sad)

SR = S.SR


# ------------------------------------------------------------------ sequencing
def seqr(motif, start=0.0, bpm=60.0, transpose=0, octave=0, vel=0.8, legato=1.0, swing=0.0):
    """(pitch, beats) -> [(start_s, dur_s, hz, vel)], skipping 'rest'."""
    spb = 60.0 / bpm
    out, b = [], 0.0
    for i, (p, d) in enumerate(motif):
        if p != "rest":
            tb = b + (swing * 0.5 if swing and abs((b * 2) % 2 - 1) < 1e-6 else 0.0)
            f = S.hz(p) * 2 ** ((transpose + 12 * octave) / 12)
            v = min(1.0, vel * (1.08 if i == 0 else 1.0) * (0.94 + 0.12 * ((i * 37) % 7) / 7))
            out.append((start + tb * spb, d * spb * legato, f, v))
        b += d
    return out


def mlen(motif, bpm):
    return sum(d for _, d in motif) * 60.0 / bpm


def legato(b: S.Buf, notes, inst, p=0.0, gain=1.0, **kw):
    if not notes:
        return
    t0 = notes[0][0]
    rel = [(st - t0, du, f, v) for st, du, f, v in notes]
    fn = {"sarangi": S.sarangi, "bansuri": S.bansuri, "shehnai": X.shehnai, "trumpet": X.trumpet,
          "trombone": X.trombone, "tuba": X.tuba, "strings": X.strings_line,
          "hum": lambda n, **k: S.voice(n, "m", **k), "oo": lambda n, **k: S.voice(n, "u", **k)}[inst]
    b.add(t0, fn(rel, **kw), p, gain)


def plucked(b: S.Buf, notes, inst, p=0.0, gain=1.0):
    for st, du, f, v in notes:
        f = _r(f)
        if inst == "glock":
            x = X.glock(f, 1.6)
        elif inst == "pizz":
            x = X.pizz(f, 0.7)
        elif inst == "sitar":
            x = X.sitar(f, round(min(2.6, du + 1.2), 1))
        elif inst == "santoor":
            x = _santoor(f, round(min(du + 0.8, 3.0), 1), 1.0)
        elif inst == "musicbox":
            x = _mbox(f)
        elif inst == "chime":
            x = _chime(f)
        else:
            raise ValueError(inst)
        b.add(st, x * v, p, gain)


def drone(b, D, gain=1.0, start=0.0):
    b.add(start, S.tanpura(SA_G, max(0.5, D - start) + 0.5), 0.0, gain)


def chord_hz(ch, transpose=0):
    return [S.hz(c) * 2 ** (transpose / 12) for c in ch]


def strings_pad(b, t, ch, dur, gain=1.0, bright=0.45, attack=0.8):
    x = X.strings_chord(ch, dur, 1.0, bright, attack)
    b.add(t, x, -0.4, gain * 0.8)
    b.add(t + 0.011, x, 0.4, gain * 0.8)


# ------------------------------------------------------------------ the three motifs as builders
def keeper(b, t, voices=1, inst="sarangi", bpm=KEEPER_BPM, gain=1.0, transpose=0, chords=True, octave=0):
    """Keeper's theme with 1, 2 or 3 voices. Returns its length in seconds."""
    legato(b, seqr(KEEPER, t, bpm, transpose, octave, 0.85), inst, 0.12, gain)
    if voices >= 2:
        legato(b, seqr(KEEPER_V2, t, bpm, transpose, 0, 0.6), "bansuri", -0.3, gain * 0.75)
    if voices >= 3:
        plucked(b, seqr(KEEPER_V3, t, bpm, transpose, 0, 0.8), "pizz", -0.05, gain * 0.9)
        plucked(b, seqr(KEEPER, t, bpm, transpose, 1, 0.45), "glock", 0.35, gain * 0.55)
    if chords:
        beat = 60.0 / bpm
        for i, (bb, ch) in enumerate(KEEPER_CHORDS):
            nb = KEEPER_CHORDS[i + 1][0] if i + 1 < len(KEEPER_CHORDS) else 16
            if voices >= 2:
                strings_pad(b, t + bb * beat, chord_hz(ch, transpose), (nb - bb) * beat + 0.6, gain * 0.9)
            else:
                place_pad(b, t + bb * beat, chord_hz(ch, transpose), (nb - bb) * beat + 0.6, gain * 0.6, 0.3)
    return mlen(KEEPER, bpm)


def bhaap(b, t, style="pizz", bpm=BHAAP_BPM, gain=1.0, transpose=0, reps=1):
    """Bhaap's theme: 'pizz' (glock + pizz), 'brass' (band), 'sad', 'musicbox', 'tiny'."""
    motif = bhaap_sad() if style == "sad" else BHAAP
    if style == "sad":
        bpm = min(bpm, 70)
    L = mlen(motif, bpm)
    q = 60.0 / bpm
    for r in range(reps):
        t0 = t + r * L
        if style in ("pizz", "tiny"):
            plucked(b, seqr(motif, t0, bpm, transpose, 0, 0.9), "glock", 0.25, gain * (0.7 if style == "tiny" else 1.0))
            if style == "pizz":
                plucked(b, seqr(motif, t0, bpm, transpose, -1, 0.7), "pizz", -0.2, gain * 0.7)
                for i in range(int(L / q)):
                    n = BHAAP_BASS[i % len(BHAAP_BASS)]
                    b.add(t0 + i * q, X.pizz(_r(S.hz(n) * 2 ** (transpose / 12)), 0.6) * 0.8, -0.1, gain * 0.8)
        elif style == "brass":
            legato(b, seqr(motif, t0, bpm, transpose, 0, 0.85, legato=0.8), "trumpet", 0.15, gain)
            plucked(b, seqr(motif, t0, bpm, transpose, 1, 0.5), "glock", 0.4, gain * 0.5)
            for i in range(int(L / q)):
                n = BHAAP_BASS[i % len(BHAAP_BASS)]
                fb = S.hz(n) * 2 ** (transpose / 12)
                b.add(t0 + i * q, X.tuba([(0, q * 0.55, fb / (2 if fb > 120 else 1), 0.9)]), -0.05, gain * 0.9)
                ch = BHAAP_CHORDS[(i // 2) % len(BHAAP_CHORDS)]
                stab = sum(X.trombone([(0, q * 0.3, S.hz(c) * 2 ** (transpose / 12), 0.6)]) for c in ch[:2])
                b.add(t0 + i * q + q * 0.5, stab, -0.3, gain * 0.45)
                b.add(t0 + i * q + q * 0.5, X.snare(0.6, False, i % 3), 0.2, gain * 0.5)
                if i % 2 == 0:
                    b.add(t0 + i * q, X.kick(0.8), 0.0, gain * 0.6)
        elif style == "sad":
            plucked(b, seqr(motif, t0, bpm, transpose, 0, 0.7), "glock", 0.2, gain * 0.8)
            legato(b, seqr(motif, t0, bpm, transpose, -1, 0.5, legato=1.0), "bansuri", -0.2, gain * 0.45)
        elif style == "musicbox":
            plucked(b, seqr(motif, t0, bpm, transpose, 1, 0.7), "musicbox", 0.1, gain)
    return L * reps


def monsoon(b, t, style="full", bpm=MONSOON_BPM, gain=1.0, transpose=0, drums=True):
    """'hint' (4 notes, shehnai), 'full' (orchestra), 'dance' (up-tempo with groove)."""
    if style == "hint":
        legato(b, seqr(MONSOON_HINT, t, 60, transpose, 0, 0.7), "shehnai", 0.1, gain * 0.8)
        place_pad(b, t, chord_hz(["G2", "D3", "A3"], transpose), mlen(MONSOON_HINT, 60) + 2, gain * 0.7, 0.25)
        b.add(t, X.timpani(_r(S.hz("G2")), 0.5, 3.0), 0.0, gain * 0.4)
        return mlen(MONSOON_HINT, 60)
    if style == "dance":
        bpm = 112
    L = mlen(MONSOON, bpm)
    beat = 60.0 / bpm
    legato(b, seqr(MONSOON, t, bpm, transpose, 0, 0.9), "strings", 0.05, gain * 1.1)
    half = 14 * beat
    legato(b, [n for n in seqr(MONSOON, t, bpm, transpose, 0, 0.8) if n[0] >= t + half - 1e-6], "shehnai", 0.25,
           gain * 0.75)
    plucked(b, seqr(MONSOON, t, bpm, transpose, -1, 0.5), "sitar", -0.35, gain * 0.6)
    for i, (bb, ch) in enumerate(MONSOON_CHORDS):
        nb = MONSOON_CHORDS[i + 1][0] if i + 1 < len(MONSOON_CHORDS) else 28
        strings_pad(b, t + bb * beat, chord_hz(ch, transpose), (nb - bb) * beat + 0.8, gain * 1.2, 0.5, 0.5)
        # sitar arpeggio on each chord
        for k, c in enumerate(ch + ch[1:2]):
            b.add(t + bb * beat + k * beat * 0.5, X.sitar(_r(S.hz(c) * 2 ** (transpose / 12 + 1)), 2.0) * 0.5, -0.5, gain * 0.5)
    if drums:
        tabla_groove(b, t, t + L, bpm, KEHERWA, gain * (0.7 if style == "full" else 0.9), p=0.2)
        for k in range(int(L / beat)):
            if k % 4 == 0:
                b.add(t + k * beat, X.dhol(1.0, True), 0.0, gain * 0.8)
            if style == "dance" and k % 2 == 1:
                b.add(t + k * beat, X.dhol(0.8, False), 0.15, gain * 0.5)
        b.add(t, X.cymbal(0.8, 3.0), 0.3, gain * 0.6)
        b.add(t + L - 4 * beat, X.cymbal(1.0, 4.0), -0.3, gain * 0.8)
    return L


def riser(b, t0, t1, gain=1.0):
    """Timpani roll + rising string swell into t1."""
    k = 0
    t = t0
    while t < t1:
        u = (t - t0) / max(0.01, t1 - t0)
        b.add(t, X.timpani(_r(S.hz("G2")), 0.2 + 0.8 * u, 1.0), 0.0, gain * 0.5)
        t += max(0.05, 0.22 - 0.17 * u)
        k += 1
    strings_pad(b, t0, chord_hz(["G2", "D3", "A3", "D4"]), t1 - t0 + 0.5, gain * 1.4, 0.6, attack=max(0.5, t1 - t0))


def sting(b, t, kind="comic", gain=1.0):
    if kind == "comic":       # brass "wah-wah" + snare rim
        b.add(t, X.trombone([(0, 0.25, "D3", 0.9), (0.28, 0.6, "C#3", 0.8)]), 0.0, gain)
        b.add(t, X.snare(0.8), 0.3, gain * 0.5)
    elif kind == "boom":
        b.add(t, X.dhol(1.0, True), 0.0, gain)
        b.add(t, X.timpani(_r(S.hz("G2")), 1.0, 2.5), 0.0, gain * 0.8)
        b.add(t, X.cymbal(0.7, 2.5), 0.2, gain * 0.5)
    elif kind == "sparkle":
        for i, n in enumerate(["G5", "A5", "C6", "D6", "G6"]):
            b.add(t + i * 0.05, X.glock(_r(S.hz(n)), 1.4) * 0.6, -0.6 + 0.3 * i, gain)
    elif kind == "ping":
        b.add(t, X.glock(_r(S.hz("D6")), 1.6), 0.3, gain)
    elif kind == "swell":
        strings_pad(b, max(0, t - 1.5), chord_hz(["G2", "D3", "A3", "D4", "G4"]), 4.0, gain * 1.6, 0.7, 1.5)
        b.add(t, X.cymbal(0.8, 3.0), 0.0, gain * 0.6)


def loop_fill(t, D, fn, gap=1.0, tail=2.0):
    while t < D - tail:
        t += fn(t) + gap
    return t


# ------------------------------------------------------------------ cues
def c_heat_open(D, hits):
    """hits[0]: thermometer pops (ping); hits[1]: power cut (music droops to the drone)."""
    b = S.Buf(D + 3)
    drone(b, D, 0.8)
    cut = hits[1] if len(hits) > 1 else D
    place_pad(b, 0, chord_hz(["G3", "A3", "D4", "A4"]), cut, 0.9, 0.25)
    # heat haze: slow sitar drips of the scale, wobbly
    t, i = 1.0, 0
    pool = ["G4", "D5", "C5", "A4", "F4", "G4", "D4", "C5"]
    while t < cut - 0.5:
        b.add(t, X.sitar(_r(S.hz(pool[i % 8])), 2.4) * 0.5, -0.4 + 0.2 * (i % 5))
        t += 1.3 if i % 3 else 2.1
        i += 1
    if cut > 6:
        legato(b, seqr(KEEPER[:4], 3.0, 48, 0, 0, 0.6), "sarangi", 0.2, 0.6)
    if hits:
        sting(b, hits[0], "ping", 0.9)
    if len(hits) > 1:
        x = b.x
        k = S.ns(cut)
        n = len(x) - k
        x[k:] *= (np.linspace(1, 0.12, n) ** 2)[:, None]
        b.add(cut, X.trombone([(0, 1.2, "G3", 0.7), (1.2, 1.4, "D3", 0.6)]), 0.0, 0.5)   # the sag
        drone(b, D, 0.5, cut + 0.5)
    return cue_out(b, D, 0.3, 2.8, 0.45, 0.055)


def c_block_life(D, hits):
    """Bustling, cranky courtyard comedy. hits: brass stabs (tanker, squabble)."""
    b = S.Buf(D + 3)
    bpm = 104
    q = 60 / bpm
    walk = ["G2", "A2", "C3", "D3", "F2", "G2", "A2", "C3"]
    t, i = 0.0, 0
    while t < D - 0.3:
        b.add(t, X.pizz(_r(S.hz(walk[i % 8])), 0.6), -0.1, 0.9)
        if i % 2:
            b.add(t, _harm(_r(S.hz(["G3", "C4", "D4", "F3"][(i // 2) % 4])), round(q * 0.8, 2)) * 0.5, 0.3, 0.6)
        t += q
        i += 1
    tabla_groove(b, 0, D, bpm, TIPTOE, 0.5)
    t = 2 * q * 4
    while t < D - 4:
        legato(b, seqr(KEEPER[:7], t, bpm * 1.2, 0, 0, 0.6, legato=0.6), "shehnai", 0.25, 0.5)
        t += mlen(KEEPER[:7], bpm * 1.2) + 4 * q * 2
    for h in hits:
        sting(b, h, "comic", 0.9)
    return cue_out(b, D, 0.2, 1.8, 0.5, 0.05)


def c_stairs_khadoos(D, hits):
    """Grumpy tuba tiptoe; hits = low stinger (the ball not given back)."""
    b = S.Buf(D + 3)
    bpm = 72
    t = 0.3
    while t < D - 2:
        notes = seqr(KEEPER[:4], t, bpm, -12, 0, 0.8, legato=0.55)
        legato(b, notes, "tuba", 0.0, 0.9)
        b.add(t, X.snare(0.4, True, 1), 0.3, 0.6)
        t += mlen(KEEPER[:4], bpm) + 1.2
    t = 0.0
    while t < D:
        b.add(t, X.pizz(_r(S.hz("G2")), 0.5) * 0.7, -0.2, 0.7)
        b.add(t + 60 / bpm, X.pizz(_r(S.hz("D3")), 0.5) * 0.5, 0.2, 0.6)
        t += 2 * 60 / bpm
    for h in hits:
        b.add(h, X.tuba([(0, 0.9, "G1", 1.0)]), 0.0, 1.0)
        b.add(h, X.timpani(_r(S.hz("G2")), 0.8), 0.0, 0.6)
    return cue_out(b, D, 0.2, 1.8, 0.4, 0.05)


def c_roof_sneak(D, hits):
    """Sneaky pizz + glock taps; hits[0] = the cooker whistle: music stops dead."""
    b = S.Buf(D + 3)
    stop = hits[0] if hits else D
    bpm = 96
    q = 60 / bpm
    pat = ["G3", None, "A#3", None, "C4", "D4", None, "A#3"]
    t, i = 0.0, 0
    while t < stop - 0.1:
        n = pat[i % 8]
        if n:
            b.add(t, X.pizz(_r(S.hz(n)), 0.5) * 0.8, -0.3 + 0.6 * ((i * 3) % 5) / 4, 0.8)
        if i % 8 == 6:
            b.add(t, X.glock(_r(S.hz("G6")), 1.0) * 0.4, 0.5, 0.6)
        t += q / 2
        i += 1
    drone(b, stop + 1, 0.4)
    x = b.x
    k = S.ns(stop)
    x[k:] = 0
    return cue_out(b, D, 0.25, 2.0, 0.5, 0.045, fade_out=0.3)


def c_cloud_birth(D, hits):
    """Keeper's theme alone (sarangi) over the drone; hits[0] = Bhaap opens his eyes -> Bhaap's theme."""
    b = S.Buf(D + 3)
    drone(b, D, 0.8)
    eyes = hits[0] if hits else D * 0.6
    keeper(b, 0.8, 1, "sarangi", gain=1.0)
    sting(b, eyes, "sparkle", 0.9)
    t = eyes + 0.4
    while t < D - 2:
        t += bhaap(b, t, "tiny", gain=0.9) + 0.8
    return cue_out(b, D, 0.3, 2.6, 0.5, 0.055)


def c_caught(D, hits):
    """'WHO is on my roof?' A comic freeze: tremolo strings, a timp thump at each hit."""
    b = S.Buf(D + 3)
    t = 0.0
    while t < D:
        strings_pad(b, t, chord_hz(["G2", "C#3", "G3"]), 2.2, 0.9, 0.6, 0.1)
        t += 2.0
    for h in (hits or [0.1]):
        b.add(h, X.timpani(_r(S.hz("G2")), 1.0), 0.0, 0.9)
        b.add(h, X.tuba([(0, 0.6, "C#2", 0.9)]), 0.0, 0.7)
    return cue_out(b, D, 0.25, 2.0, 0.5, 0.045)


def c_recruited(D, hits):
    """Keeper's theme, 2 voices (Ishaan holds the wire): warm and wary."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    loop_fill(1.0, D, lambda t: keeper(b, t, 2, "sarangi"), gap=2.0, tail=6)
    return cue_out(b, D, 0.3, 2.6, 0.5, 0.055)


def c_workshop_reveal(D, hits):
    """The tank's silver-blue cathedral: string swell + glock arpeggios, Keeper's theme 2-voice warmer."""
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    sting(b, hits[0] if hits else 0.6, "swell", 1.0)
    arp = ["G4", "C5", "D5", "A5", "G5", "D5", "C5", "A4"]
    t, i = 0.5, 0
    while t < D - 0.5:
        b.add(t, X.glock(_r(S.hz(arp[i % 8])), 1.6) * 0.5, -0.6 + 1.2 * ((i * 5) % 8) / 7, 0.7)
        t += 0.25
        i += 1
    loop_fill(2.5, D, lambda t: keeper(b, t, 2, "strings", bpm=60), gap=1.0, tail=6)
    return cue_out(b, D, 0.4, 3.4, 0.6, 0.065)


def c_montage_brass(D, hits):
    """Bhaap's theme as a small brass band (the apprenticeship montage). hits = cymbal accents."""
    b = S.Buf(D + 3)
    t = 0.2
    k = 0
    while t < D - 1.5:
        t += bhaap(b, t, "brass" if k % 3 != 2 else "pizz", gain=1.0, transpose=(0 if k % 2 == 0 else 5))
        k += 1
    for h in hits:
        b.add(h, X.cymbal(0.9, 2.0), 0.2, 0.7)
    return cue_out(b, D, 0.18, 1.6, 0.6, 0.075)


def c_smog_sweep(D, hits):
    """Lighter, swung sweeping: brushed snare, pizz, Bhaap theme on glock slower."""
    b = S.Buf(D + 3)
    bpm = 108
    q = 60 / bpm
    t, i = 0.0, 0
    while t < D - 0.2:
        b.add(t + (q * 0.15 if i % 2 else 0), X.snare(0.5, True, i % 3), 0.2, 0.6)
        if i % 2 == 0:
            b.add(t, X.pizz(_r(S.hz(BHAAP_BASS[(i // 2) % 8])), 0.6), -0.2, 0.8)
        t += q / 2
        i += 1
    loop_fill(0.8, D, lambda t: bhaap(b, t, "tiny", bpm=bpm), gap=q * 2, tail=3)
    return cue_out(b, D, 0.2, 1.6, 0.5, 0.055)


def c_hailstorm(D, hits):
    """Comic chaos: fast pizz runs, glock rattles, falling tuba; hits = crashes."""
    b = S.Buf(D + 3)
    g = np.random.default_rng(5)
    t = 0.0
    scale = ["G3", "A3", "C4", "D4", "F4", "G4", "A4", "C5", "D5"]
    while t < D - 0.3:
        b.add(t, X.pizz(_r(S.hz(scale[int(g.integers(0, 9))])), 0.4) * 0.7, g.uniform(-0.7, 0.7), 0.8)
        if g.random() < 0.35:
            b.add(t, X.glock(_r(S.hz(scale[int(g.integers(4, 9))]) * 2), 0.8) * 0.4, g.uniform(-0.8, 0.8), 0.6)
        t += 0.09
    t = 1.0
    while t < D - 2:
        legato(b, [(t, 0.4, S.hz("D3"), 0.8), (t + 0.4, 0.4, S.hz("C3"), 0.8), (t + 0.8, 0.9, S.hz("A2"), 0.8)],
               "tuba", 0.0, 0.9)
        t += 2.6
    for h in hits:
        b.add(h, X.cymbal(1.0, 2.0), 0.0, 0.9)
        b.add(h, X.dhol(1.0, True), 0.0, 0.8)
    return cue_out(b, D, 0.15, 1.4, 0.6, 0.07)


def c_notebook(D, hits):
    """Tara writing: gentle pizz + glock Bhaap theme slow + harmonium."""
    b = S.Buf(D + 3)
    chords_loop(b, 0, D, [chord_hz(c) for c in BHAAP_CHORDS], 4 * 60 / 84, 0.7, 0.3)
    loop_fill(0.6, D, lambda t: bhaap(b, t, "tiny", bpm=84), gap=1.4, tail=3)
    return cue_out(b, D, 0.25, 2.0, 0.45, 0.045)


def c_photo_alone(D, hits):
    """Meghnath alone with Varsha's photo: Keeper's theme solo, very soft, soft strings."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    strings_pad(b, 0, chord_hz(["G2", "D3", "A3"]), D, 0.7, 0.3, 2.0)
    keeper(b, 1.0, 1, "sarangi", bpm=50, gain=0.8, chords=False)
    return cue_out(b, D, 0.35, 3.0, 0.4, 0.04)


def c_overdue(D, hits):
    """The late monsoon: tick-like pizz ostinato, low strings, Keeper fragments."""
    b = S.Buf(D + 3)
    bpm = 90
    q = 60 / bpm
    t, i = 0.0, 0
    while t < D - 0.2:
        b.add(t, X.pizz(_r(S.hz("G4" if i % 2 == 0 else "F4")), 0.3) * 0.6, 0.4 if i % 2 else -0.4, 0.6)
        t += q
        i += 1
    strings_pad(b, 0, chord_hz(["G2", "D3", "F3"]), D, 0.8, 0.35, 2.0)
    t = 2.0
    while t < D - 4:
        legato(b, seqr(KEEPER[:4], t, 56, 0, -1, 0.6), "sarangi", 0.1, 0.7)
        t += mlen(KEEPER[:4], 56) + 3.0
    return cue_out(b, D, 0.3, 2.4, 0.4, 0.045)


def c_trunk_reveal(D, hits):
    """The Monsoon Trunk uncovered: low strings, dhol boom at hits[0], a sitar shimmer."""
    b = S.Buf(D + 3)
    drone(b, D, 0.7)
    h0 = hits[0] if hits else 0.5
    sting(b, h0, "boom", 1.0)
    strings_pad(b, h0, chord_hz(["G2", "D3", "A3"]), D - h0, 1.0, 0.4, 1.5)
    t = h0 + 1.0
    for k, n in enumerate(["G4", "A4", "C5", "D5", "F5", "G5"]):
        b.add(t + k * 0.12, X.sitar(_r(S.hz(n)), 2.5) * 0.6, -0.5 + 0.2 * k, 0.8)
    for h in hits[1:]:
        sting(b, h, "boom", 0.8)
    return cue_out(b, D, 0.35, 3.0, 0.45, 0.055)


def c_varsha_memory(D, hits):
    """The silhouette memory: the MONSOON HINT (4 notes, shehnai) over a bruised purple pad."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    place_pad(b, 0, chord_hz(["G2", "C3", "D3", "A3"]), D, 0.8, 0.25)
    t = hits[0] if hits else 1.0
    monsoon(b, t, "hint", gain=1.0)
    for h in hits[1:]:
        sting(b, h, "sparkle", 0.6)
    return cue_out(b, D, 0.45, 3.4, 0.4, 0.045)


def c_go_home(D, hits):
    """'GO HOME.' Tired, lonely: Keeper's theme in fragments + a sad Bhaap drizzle."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    legato(b, seqr(KEEPER[:7], 0.8, 48, 0, 0, 0.6), "sarangi", 0.1, 0.8)
    t = 0.8 + mlen(KEEPER[:7], 48) + 1.0
    if t < D - 3:
        bhaap(b, t, "sad", gain=0.8)
    return cue_out(b, D, 0.35, 3.0, 0.4, 0.04)


def c_dadi_night(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    chords_loop(b, 0, D, [chord_hz(c) for c in [["G2", "D3", "A#3"], ["F2", "C3", "A3"]]], 4.0, 0.7, 0.25)
    loop_fill(1.5, D, lambda t: (legato(b, seqr(KEEPER[:7], t, 50, 0, 0, 0.55), "bansuri", 0.1, 0.8),
                                 mlen(KEEPER[:7], 50))[1], gap=3.0, tail=4)
    return cue_out(b, D, 0.35, 2.8, 0.4, 0.038)


def c_shortcut_sneak(D, hits):
    """The shortcut: sneaky low pizz and tension that rises to hits[0] (the lid lifts: cut)."""
    b = S.Buf(D + 3)
    end = hits[0] if hits else D
    bpm = 100
    q = 60 / bpm
    pat = ["G2", "G2", "A#2", "G2", "C3", "C#3", "C3", "A#2"]
    t, i = 0.0, 0
    while t < end - 0.1:
        b.add(t, X.pizz(_r(S.hz(pat[i % 8])), 0.5) * 0.9, -0.2, 0.9)
        t += q / 2
        i += 1
    strings_pad(b, 0, chord_hz(["G2", "C#3", "G3"]), end, 0.9, 0.5, max(1.0, end * 0.8))
    x = b.x
    x[S.ns(end):] = 0
    return cue_out(b, D, 0.25, 2.0, 0.5, 0.05, fade_out=0.2)


def c_aandhi(D, hits):
    """The dust storm: driving dhol, tremolo strings, brass blasts, swirling sitar. hits = brass blasts."""
    b = S.Buf(D + 3)
    bpm = 132
    q = 60 / bpm
    t, i = 0.0, 0
    while t < D - 0.2:
        b.add(t, X.dhol(1.0, i % 2 == 0), 0.0 if i % 2 == 0 else 0.2, 0.9)
        if i % 4 == 3:
            b.add(t + q / 2, X.dhol(0.8, False), -0.2, 0.6)
        t += q
        i += 1
    t = 0.0
    while t < D:
        strings_pad(b, t, chord_hz(["G2", "C#3", "G3", "A#3"]), 1.6, 1.2, 0.8, 0.05)
        t += 1.5
    g = np.random.default_rng(9)
    scale = ["G3", "A#3", "C4", "C#4", "D4", "F4", "G4", "A#4"]
    t = 0.5
    while t < D - 0.5:
        for k in range(6):
            b.add(t + k * 0.06, X.sitar(_r(S.hz(scale[(k + int(g.integers(0, 8))) % 8])), 1.0) * 0.4, g.uniform(-0.8, 0.8), 0.6)
        t += 1.4
    for h in (hits or [0.2]):
        b.add(h, X.trombone([(0, 1.0, "G2", 1.0)]) + X.trumpet([(0, 1.0, "C#4", 0.9)]), 0.0, 0.9)
        b.add(h, X.cymbal(1.0, 2.5), 0.0, 0.8)
    return cue_out(b, D, 0.15, 1.6, 0.6, 0.08)


def c_storm_rescue(D, hits):
    """Meghnath spins the storm back: Keeper's theme heroic (strings + brass) over drums.
    hits[0] = the storm is pulled down (big resolution swell), music then deflates."""
    b = S.Buf(D + 3)
    bpm = 96
    res = hits[0] if hits else D * 0.75
    beat = 60 / bpm
    t, i = 0.0, 0
    while t < res - 0.2:
        b.add(t, X.dhol(0.9, i % 2 == 0), 0.0, 0.7)
        t += beat
        i += 1
    legato(b, seqr(KEEPER, 0.5, 70, 0, 0, 0.95), "strings", 0.0, 1.2)
    legato(b, seqr(KEEPER, 0.5, 70, 0, -1, 0.8), "trombone", -0.3, 0.6)
    ost = ["G3", "C4", "D4", "G4"]
    t, i = 0.0, 0
    while t < res - 0.1:
        b.add(t, X.sitar(_r(S.hz(ost[i % 4])), 1.0) * 0.5, 0.4, 0.6)
        t += beat / 2
        i += 1
    sting(b, res, "swell", 1.2)
    x = b.x
    k = S.ns(res + 1.5)
    if k < len(x):
        x[k:] *= (np.linspace(1, 0.15, len(x) - k) ** 2)[:, None]
    return cue_out(b, D, 0.2, 2.2, 0.55, 0.075)


def c_aftermath(D, hits):
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    t = 1.0
    while t < D - 3:
        b.add(t, X.pizz(_r(S.hz("D4")), 0.6) * 0.5, 0.3, 0.6)
        t += 2.5
    legato(b, seqr(KEEPER[7:], 2.0, 46, 0, 0, 0.5), "sarangi", 0.0, 0.7)
    return cue_out(b, D, 0.35, 2.8, 0.4, 0.035)


def c_waiting(D, hits):
    """Ishaan waits for Bhaap: Bhaap's theme small and slow on glock, long silences."""
    b = S.Buf(D + 3)
    drone(b, D, 0.4)
    t = 1.5
    while t < D - 4:
        t += bhaap(b, t, "sad", bpm=60, gain=0.7) + 5.0
    return cue_out(b, D, 0.4, 3.0, 0.45, 0.032)


def c_bhaap_returns(D, hits):
    """The tiny grey cloud comes home: Bhaap's theme tender (glock + strings); hits[0] = happy spark."""
    b = S.Buf(D + 3)
    strings_pad(b, 0, chord_hz(["G3", "B3", "D4"]), D, 0.8, 0.4, 2.0)
    loop_fill(1.0, D, lambda t: bhaap(b, t, "tiny", bpm=80, gain=0.9), gap=1.5, tail=3)
    for h in hits:
        sting(b, h, "sparkle", 0.9)
    return cue_out(b, D, 0.35, 2.6, 0.5, 0.05)


def c_three_keys(D, hits):
    """The kids decide: Keeper's theme with THREE voices, building."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    loop_fill(0.8, D, lambda t: keeper(b, t, 3, "sarangi", bpm=60), gap=0.5, tail=6)
    for h in hits:
        sting(b, h, "sparkle", 0.7)
    return cue_out(b, D, 0.3, 2.6, 0.5, 0.06)


def c_bowl_slowmo(D, hits):
    """Rehan's run-up and the slow-motion key: heartbeat + riser into hits[0] (the CLICK)."""
    b = S.Buf(D + 3)
    click = hits[0] if hits else D - 1.0
    t = 0.0
    while t < click:
        b.add(t, X.kick(0.9), 0.0, 0.8)
        b.add(t + 0.28, X.kick(0.6), 0.0, 0.6)
        t += max(0.55, 1.1 - 0.5 * t / max(click, 0.1))
    riser(b, 0.0, click, 1.0)
    legato(b, seqr(MONSOON_HINT, max(0.0, click - 4.5), 50, 0, -1, 0.6), "shehnai", 0.1, 0.6)
    sting(b, click, "swell", 1.3)
    sting(b, click, "sparkle", 1.0)
    return cue_out(b, D, 0.35, 3.0, 0.5, 0.06)


def c_monsoon_full(D, hits):
    """THE MONSOON rolls out: the full theme (orchestra, sitar, shehnai, tabla, dhol).
    hits[0] = lid lifts (big swell)."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    t0 = hits[0] if hits else 0.5
    sting(b, t0, "swell", 1.3)
    loop_fill(t0 + 0.3, D, lambda t: monsoon(b, t, "full"), gap=0.0, tail=8)
    return cue_out(b, D, 0.3, 3.0, 0.55, 0.085)


def c_first_rain_dance(D, hits):
    """Joy in the rain: Monsoon theme up-tempo with groove, Bhaap brass interjections."""
    b = S.Buf(D + 3)
    t = 0.3
    k = 0
    while t < D - 2:
        if k % 3 == 2:
            t += bhaap(b, t, "brass", bpm=120, gain=1.0)
        else:
            t += monsoon(b, t, "dance", gain=1.0)
        k += 1
    return cue_out(b, D, 0.25, 2.2, 0.6, 0.085)


def c_keeper_laughs(D, hits):
    """Meghnath laughs in the rain: Keeper's theme warm, 3 voices, strings."""
    b = S.Buf(D + 3)
    drone(b, D, 0.5)
    loop_fill(0.5, D, lambda t: keeper(b, t, 3, "strings", bpm=64, gain=1.0), gap=0.5, tail=5)
    return cue_out(b, D, 0.35, 2.8, 0.55, 0.06)


def c_notebook_passed(D, hits):
    """The notebook handed on, and he rests: Keeper's theme 3-voice + a Monsoon-hint coda."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    L = keeper(b, 0.5, 3, "sarangi", bpm=56)
    if 0.5 + L + 1 < D - 5:
        monsoon(b, 0.5 + L + 0.5, "hint", gain=0.8)
    return cue_out(b, D, 0.35, 3.0, 0.5, 0.05)


def c_coda(D, hits):
    """Weeks later, a hot bright day: Bhaap's theme sunny on pizz + glock; Keeper's tag at the end."""
    b = S.Buf(D + 3)
    t = 0.3
    while t < D - 7:
        t += bhaap(b, t, "pizz", bpm=120)
    if D > 6:
        legato(b, seqr(KEEPER[-2:], D - 5.5, 56, 0, 0, 0.6), "bansuri", 0.1, 0.7)
    return cue_out(b, D, 0.2, 1.8, 0.55, 0.06)


def c_credits(D, hits):
    """Medley: Bhaap brass -> Keeper 3-voice -> Monsoon full finale."""
    b = S.Buf(D + 3)
    t = 0.3
    t += bhaap(b, t, "brass", reps=2)
    if t < D - 20:
        t += keeper(b, t + 0.5, 3, "strings", bpm=64) + 0.5
    while t < D - 6:
        t += monsoon(b, t, "full")
    return cue_out(b, D, 0.25, 2.4, 0.6, 0.075)


def c_postcredits(D, hits):
    b = S.Buf(D + 3)
    bhaap(b, 0.3, "tiny", bpm=150)
    sting(b, min(D - 1.0, 0.3 + mlen(BHAAP, 150) + 0.3), "sparkle", 0.9)
    return cue_out(b, D, 0.2, 1.6, 0.6, 0.05)


def c_keeper_bed(D, hits):
    """Fallback for unknown ids: a soft Keeper's-theme bed."""
    b = S.Buf(D + 3)
    drone(b, D, 0.6)
    loop_fill(1.0, D, lambda t: keeper(b, t, 1, "bansuri", bpm=52, gain=0.7), gap=3.0, tail=6)
    return cue_out(b, D, 0.3, 2.6, 0.45, 0.04)


class FallbackCues(dict):
    """dict whose .get() returns the Keeper's-theme bed for unknown ids (but not for '')."""

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return c_keeper_bed if key else default


CUES = FallbackCues({
    "heat_open": c_heat_open, "block_life": c_block_life, "stairs_khadoos": c_stairs_khadoos,
    "roof_sneak": c_roof_sneak, "cloud_birth": c_cloud_birth, "caught": c_caught, "recruited": c_recruited,
    "workshop_reveal": c_workshop_reveal, "montage_brass": c_montage_brass, "smog_sweep": c_smog_sweep,
    "hailstorm": c_hailstorm, "notebook": c_notebook, "photo_alone": c_photo_alone, "overdue": c_overdue,
    "trunk_reveal": c_trunk_reveal, "varsha_memory": c_varsha_memory, "go_home": c_go_home,
    "dadi_night": c_dadi_night, "shortcut_sneak": c_shortcut_sneak, "aandhi": c_aandhi,
    "storm_rescue": c_storm_rescue, "aftermath": c_aftermath, "waiting": c_waiting,
    "bhaap_returns": c_bhaap_returns, "three_keys": c_three_keys, "bowl_slowmo": c_bowl_slowmo,
    "monsoon_full": c_monsoon_full, "first_rain_dance": c_first_rain_dance, "keeper_laughs": c_keeper_laughs,
    "notebook_passed": c_notebook_passed, "coda": c_coda, "credits": c_credits, "postcredits": c_postcredits,
    "keeper_bed": c_keeper_bed,
})
