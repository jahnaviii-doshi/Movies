"""Shots, dialogue lines, sound cues: the film's single source of truth.

Scene modules (anim/scenes/scNN.py) each export SHOTS: list[Shot]. `build_film()` loads
them in order, synthesizes dialogue (cached), resolves timing, and writes
films/midnight_sweet_shop/edit/timeline.json for the audio mixer.
"""
from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import voice

FILM = os.environ.get("FILM", "midnight_sweet_shop")
FILM_DIR = Path(__file__).resolve().parents[2] / "films" / FILM
# film 1 keeps its original package; later films live in anim/films/<slug>/scenes
SCENE_PKG = "anim.scenes" if FILM == "midnight_sweet_shop" else f"anim.films.{FILM}.scenes"
VOICE_DIR = FILM_DIR / "assets" / "voice"
FPS = 24
W, H = 1920, 1080


@dataclass
class Line:
    char: str
    text: str
    at: float = 0.0              # seconds into the shot
    onscreen: bool = True        # drives mouth animation if the speaker is drawn
    meta: dict = field(default_factory=dict)   # filled by build: wav, duration, mouth

    @property
    def end(self) -> float:
        return self.at + self.meta.get("duration", 0.0)


@dataclass
class Sfx:
    name: str
    at: float = 0.0
    gain_db: float = 0.0
    dur: float | None = None
    params: dict = field(default_factory=dict)


@dataclass
class Shot:
    id: str
    draw: Callable                # draw(canvas, ctx)
    duration: float | None = None # None -> last line end + tail
    lines: list[Line] = field(default_factory=list)
    sfx: list[Sfx] = field(default_factory=list)
    music: str | None = None      # music cue id that STARTS at this shot ("" = stop music)
    music_hits: list[float] = field(default_factory=list)  # accent times (s into shot) for the cue
    transition: str = "cut"       # cut | dissolve | fade_black | fade_white
    trans_dur: float = 0.5
    tail: float = 1.0
    notes: str = ""
    scene: int = 0
    start: float = 0.0            # filled by build

    def resolve(self):
        for ln in self.lines:
            if not ln.meta:
                ln.meta = voice.synth(ln.char, ln.text, VOICE_DIR)
        if self.duration is None:
            self.duration = max([ln.end for ln in self.lines] + [2.0]) + self.tail
        self.duration = round(self.duration * FPS) / FPS
        return self


class Ctx:
    """Per-frame context passed to a shot's draw function."""

    def __init__(self, shot: Shot, frame: int):
        self.shot = shot
        self.frame = frame
        self.t = frame / FPS
        self.dur = shot.duration
        self.u = min(1.0, self.t / max(1e-6, self.dur))

    def mouth(self, char: str) -> float:
        """Mouth openness 0..1 for `char` at this frame (from the dialogue audio)."""
        for ln in self.shot.lines:
            if ln.char == char and ln.onscreen and ln.at <= self.t < ln.end:
                env = ln.meta["mouth"]
                i = int((self.t - ln.at) * FPS)
                return env[min(i, len(env) - 1)]
        return 0.0

    def speaking(self, char: str) -> bool:
        return any(ln.char == char and ln.at <= self.t < ln.end for ln in self.shot.lines)

    def seg(self, a: float, b: float) -> float:
        """0..1 progress between absolute shot times a and b (clamped)."""
        return 0.0 if self.t <= a else 1.0 if self.t >= b else (self.t - a) / (b - a)


SCENES = [f"sc{n:02d}" for n in range(1, 13)] + ["credits"]


def load_scenes(only: list[str] | None = None) -> list[Shot]:
    shots: list[Shot] = []
    for name in SCENES:
        if only and name not in only:
            continue
        try:
            mod = importlib.import_module(f"{SCENE_PKG}.{name}")
        except ModuleNotFoundError:
            continue
        for s in mod.SHOTS:
            s.scene = s.scene or (int(name[2:]) if name.startswith("sc") else 99)
            shots.append(s)
    return shots


def build_film(only: list[str] | None = None, write: bool = True) -> list[Shot]:
    shots = [s.resolve() for s in load_scenes(only)]
    t = 0.0
    for s in shots:
        s.start = round(t, 4)
        t += s.duration
    if write:
        tl = {
            "fps": FPS, "duration": round(t, 3),
            "shots": [{"id": s.id, "scene": s.scene, "start": s.start, "duration": s.duration,
                       "transition": s.transition} for s in shots],
            "dialogue": [{"shot": s.id, "char": ln.char, "text": ln.text, "start": round(s.start + ln.at, 3),
                          "duration": round(ln.meta["duration"], 3), "wav": ln.meta["wav"]}
                         for s in shots for ln in s.lines],
            "sfx": [{"shot": s.id, "name": x.name, "start": round(s.start + x.at, 3), "gain_db": x.gain_db,
                     "dur": x.dur, "params": x.params} for s in shots for x in s.sfx],
            "music": [{"cue": s.music, "start": s.start, "hits": [round(s.start + h, 3) for h in s.music_hits]}
                      for s in shots if s.music is not None],
        }
        (FILM_DIR / "edit").mkdir(parents=True, exist_ok=True)
        (FILM_DIR / "edit" / "timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False))
    return shots
