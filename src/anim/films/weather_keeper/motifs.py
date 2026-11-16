"""The three original leitmotifs of The Weather Keeper of Block C. Key: Sa = G.

The score lives in a monsoon-raag colour (Megh-like pentatonic G A C D F: Sa Re ma Pa komal-ni)
for the Keeper and the Monsoon, and in bright G major for Bhaap. Notes are (pitch, beats);
use anim.audio.motifs.seq() to turn them into timed events.
"""
from __future__ import annotations

SA_G = 98.0          # G2: the drone's low Sa

# 1. KEEPER'S THEME: 4/4, ♩=56. A lonely, slow solo melody (sarangi), 16 beats.
#    It gains harmony as the kids join: a counter-line (2 voices), then a bass + bell
#    line (3 voices). It ends on Sa only in its 3-voice form (the work handed on).
KEEPER = [("G4", 1.0), ("A4", 0.5), ("C5", 1.5), ("D5", 1.0),
          ("C5", 0.5), ("A4", 0.5), ("G4", 3.0),
          ("F4", 1.0), ("G4", 0.5), ("A4", 0.5), ("C5", 1.0), ("A4", 1.0),
          ("G4", 4.0)]
KEEPER_BPM = 56
# second voice (a kid joining): sustained notes under the melody, 16 beats
KEEPER_V2 = [("D4", 4.0), ("F4", 2.0), ("D4", 2.0), ("C4", 2.0), ("F4", 2.0), ("D4", 4.0)]
# third voice: bass walking Sa-ni-ma-Sa, 16 beats
KEEPER_V3 = [("G2", 4.0), ("F2", 2.0), ("C3", 2.0), ("F2", 2.0), ("A2", 2.0), ("G2", 4.0)]
KEEPER_CHORDS = [(0, ["G2", "D3", "A3"]), (4, ["F2", "C3", "G3"]), (8, ["C3", "G3", "D4"]), (12, ["G2", "D3", "G3"])]

# 2. BHAAP'S THEME: 2/4, ♩=132, bright G major, pizzicato + glockenspiel.
#    (10 beats incl. the closing rest.) The little cloud's bounce: a skip down-and-up, then a hop to the top.
BHAAP = [("D5", 0.25), ("E5", 0.25), ("D5", 0.5), ("B4", 0.5), ("G4", 0.5),
         ("A4", 0.25), ("B4", 0.25), ("D5", 0.5), ("G5", 1.0),
         ("E5", 0.25), ("D5", 0.25), ("B4", 0.5), ("A4", 0.25), ("G4", 0.25), ("E4", 0.5),
         ("G4", 0.5), ("A4", 0.5), ("B4", 0.5), ("G4", 1.0), ("rest", 1.5)]   # 10 beats = 5 bars of 2/4
BHAAP_BPM = 132
BHAAP_BASS = ["G2", "D3", "C3", "D3", "E2", "B2", "C3", "D3"]   # quarter-note pizz bass, 8 beats
BHAAP_CHORDS = [["G3", "B3", "D4"], ["C3", "E3", "G3"], ["E3", "G3", "B3"], ["D3", "F#3", "A3"]]


def bhaap_sad(motif=BHAAP):
    """Small and sad (drizzling): B -> Bb, E -> Eb; played slow."""
    return [(p.replace("B4", "A#4").replace("E5", "D#5").replace("E4", "D#4"), b) for p, b in motif]


# 3. MONSOON THEME: 4/4, ♩=72, swelling. 28 beats. Megh-like (G A C D F), rising leaps.
#    The 4-note HINT (Varsha's memory) is its opening C D F D.
MONSOON = [("C5", 1.0), ("D5", 1.0), ("F5", 1.5), ("D5", 0.5), ("C5", 1.0), ("A4", 1.0), ("G4", 2.0),
           ("A4", 1.0), ("C5", 1.0), ("D5", 1.0), ("G5", 1.0), ("F5", 1.5), ("D5", 0.5), ("C5", 2.0),
           ("D5", 1.0), ("F5", 1.0), ("G5", 1.0), ("A5", 1.0), ("G5", 1.5), ("F5", 0.5), ("D5", 1.0),
           ("C5", 1.0), ("G5", 4.0)]
MONSOON_HINT = [("C5", 1.0), ("D5", 1.0), ("F5", 1.5), ("D5", 2.5)]
MONSOON_BPM = 72
MONSOON_CHORDS = [(0, ["G2", "D3", "A3"]), (4, ["F2", "C3", "G3"]), (8, ["C3", "G3", "D4"]),
                  (12, ["F2", "C3", "A3"]), (16, ["D3", "G3", "A3"]), (20, ["F2", "C3", "G3"]),
                  (24, ["G2", "D3", "G3", "D4"])]


def strip_rests(motif):
    return [(p, b) for p, b in motif]
