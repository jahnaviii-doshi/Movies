"""The three original leitmotifs of the score (all composed for this film). Key: Sa = D.

Notes are (pitch, beats). Use `seq()` to turn a motif into timed note events.
"""
from __future__ import annotations

from .synth import hz

SA = 146.83  # D3, the drone's low Sa

# 1. AMMA'S LULLABY: six notes, 3/4, ♩=66, Bhupali-flavoured (D E F# A B).
#    It deliberately ends on Re (E), unresolved: "the story without an ending".
#    Only when the ending is remembered (blaze / dawn_farewell / coda) does a seventh
#    note arrive: Re -> Sa (E -> D), resolving it.
LULLABY = [("A4", 1.0), ("B4", 0.5), ("F#4", 1.5), ("A4", 1.0), ("F#4", 1.0), ("E4", 3.0)]
LULLABY_RESOLVE = [("E4", 2.0), ("D4", 4.0)]        # the "ending": Re held, then Sa
LULLABY_ENDED = LULLABY[:-1] + LULLABY_RESOLVE      # seven notes: the story with its ending
LULLABY_BPM = 66
LULLABY_CHORDS = [(0, ["D3", "F#3", "A3"]), (3, ["B2", "D3", "F#3"]), (6, ["E3", "A3", "B3"])]  # beats

# 2. WONDER THEME: 4/4, ♩=96. Opens with the lullaby's first interval (A-B), then leaps up a sixth.
WONDER = [("A4", .5), ("B4", .5), ("F#5", 2.5), ("E5", .5),
          ("F#5", .5), ("A5", .5), ("B5", 2.5), ("A5", .5),
          ("F#5", 1), ("E5", .5), ("D5", .5), ("E5", 2),
          ("D5", .5), ("E5", .5), ("F#5", .5), ("A5", .5), ("D6", 2)]
WONDER_BPM = 96
WONDER_OSTINATO = ["D4", "A4", "D5", "E5", "F#5", "E5", "D5", "A4"]  # eighths, santoor
WONDER_CHORDS = [["D3", "F#3", "A3"], ["B2", "D3", "F#3"], ["G2", "B2", "D3"], ["A2", "C#3", "E3"]]

# 3. KABIR'S SWAGGER: 4/4, ♩=108, swung, cocky flat-7 (C natural).
#    Tender version: ♩=60, straight, flat-7 sweetened to C#: the brag becomes a promise.
SWAGGER = [("D4", .5), ("F#4", .25), ("A4", .25), ("B4", .5), ("A4", .5), ("C5", .75), ("B4", .25),
           ("A4", .5), ("F#4", .5),
           ("A4", .5), ("D5", 1.0), ("C5", .25), ("B4", .25), ("A4", .5), ("F#4", .5), ("D4", 1.0)]
SWAGGER_BPM = 108
SWAGGER_BASS = ["D2", "D2", "A2", "C3", "G2", "G2", "A2", "A2"]  # quarter notes per two bars


def tender(motif):
    return [(p.replace("C5", "C#5").replace("C4", "C#4"), b) for p, b in motif]


def beats_len(motif) -> float:
    return sum(b for _, b in motif)


def seq(motif, start: float = 0.0, bpm: float = 60, transpose: int = 0, vel: float = 0.8,
        legato: float = 1.0, swing: float = 0.0, octave: int = 0, accent_first=True):
    """-> [(start_s, dur_s, freq_hz, vel)]. swing delays off-beat eighths (0..0.33 of an eighth)."""
    spb = 60.0 / bpm
    out = []
    b = 0.0
    for i, (p, d) in enumerate(motif):
        f = hz(p) * 2 ** ((transpose + 12 * octave) / 12)
        tb = b
        if swing and abs((b * 2) % 2 - 1) < 1e-6:  # off-beat eighth
            tb = b + swing * 0.5
        v = vel * (1.08 if (accent_first and i == 0) else 1.0) * (0.95 + 0.1 * ((i * 37) % 7) / 7)
        out.append((start + tb * spb, d * spb * legato, f, min(1.0, v)))
        b += d
    return out


def motif_seconds(motif, bpm) -> float:
    return beats_len(motif) * 60.0 / bpm
