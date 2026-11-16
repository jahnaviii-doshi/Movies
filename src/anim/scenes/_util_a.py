"""Helpers shared by scenes 1-3 (fork A)."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import W, H
from ..rig import chars, animals as A
from ..sets import rooftop as RT
from ..timeline import Sfx


def bed(name: str, dur: float, gain: float = -14.0, at: float = 0.0) -> Sfx:
    return Sfx(name, at, gain, dur=dur)


def seat(key: str, sk: float = 1.5):
    """Seat point + scale for a kid/Nani sitting on a rooftop charpai."""
    a = RT.ANCHORS[key]
    x, y = a["surface"]
    return x, y + 10, a["s"] * sk


def bed_surface(key: str):
    return RT.ANCHORS[key]["surface"]


def head_y(who: str, y: float, s: float, sitting=True) -> float:
    """Approximate screen y of a character's head centre (for framing close-ups)."""
    rig = chars.CAST[who]
    off = (-rig.hip_y - 4) if sitting else 0
    return y + (rig.neck_y - rig.head_r * 0.82 + off) * s


def look_dart(t: float, seed: int = 0, amt: float = 0.5):
    """Little natural eye darts (dx, dy)."""
    return (amt * K.noise1(t * 0.8, seed), 0.25 * amt * K.noise1(t * 0.6, seed + 3))


def amma(cv, t, x, y, s, mouth=0.0, alpha=0.85, desat=0.15, light="shop", sparkle=True, **pose):
    """Mishri Amma, faintly see-through, with sugar sparkles drifting off her."""
    if pose.get("expr", "neutral") in ("happy", "laugh", "neutral", "smug", "awe", "surprised", "grin"):
        pose.setdefault("brow", 0.7)
    with K.lit(cv, light, alpha=alpha, desat=desat):
        chars.draw(cv, "amma", x=x, y=y, s=s, t=t, mouth=mouth, **pose)
    if sparkle:
        fx.sparkles(cv, t, x, y - 130 * s, spread=80 * s, n=8, color="#ffd9ea", size=5, seed=33,
                    a=0.6 * (1 - alpha + 0.4), rise=0.5)


def tola(cv, t, x, y, s, **kw):
    A.draw_scale(cv, A.ScalePose(x=x, y=y, s=s, t=t, **kw))


def dog(cv, **kw):
    A.draw_dog(cv, A.DogPose(**kw))


def title_text(cv, text, x, y, size, a, color="#ffe9b8"):
    if a <= 0.01:
        return
    f = K.font(size, "DejaVu Serif", True, True)
    w = f.measureText(text)
    # soft warm glow behind the lettering
    p = skia.Paint(AntiAlias=True, Color=K.C("#ffb02e", 0.55 * a))
    p.setImageFilter(skia.ImageFilters.Blur(18, 18))
    cv.drawString(text, x - w / 2, y, f, p)
    cv.drawString(text, x - w / 2 + 3, y + 4, f, K.fill("#1a0c14", 0.5 * a))
    cv.drawString(text, x - w / 2, y, f, K.fill(color, a))


def cam(cx, cy, z):
    """Clamp a camera so a 1920x1080 set never shows its edges."""
    z = max(1.0, z)
    hw, hh = W / 2 / z, H / 2 / z
    return (min(max(cx, hw), W - hw), min(max(cy, hh), H - hh), z)


def camd(cx, cy, z):
    x, y, z = cam(cx, cy, z)
    return dict(cx=x, cy=y, zoom=z)
