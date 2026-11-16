"""Helpers shared by WK scenes 1-3 (scene fork A)."""
from __future__ import annotations

import math
from contextlib import contextmanager

import skia

from .... import core as K, voice
from ....core import W, H, clamp, lerp
from ....timeline import FPS, Shot, Line, Sfx, VOICE_DIR
from .. import rig as R


def ccam(cx, cy, z=1.0):
    """Camera tuple clamped so the view never leaves the 1920x1080 world (no black edges)."""
    z = max(1.0, z)
    hw, hh = W / 2 / z, H / 2 / z
    return (clamp(cx, hw, W - hw), clamp(cy, hh, H - hh), z)


def cam_move(u, a, b, ease=K.ease_in_out):
    e = ease(u)
    return ccam(lerp(a[0], b[0], e), lerp(a[1], b[1], e), lerp(a[2], b[2], e))


@contextmanager
def cam(cv, c):
    with K.camera(cv, c[0], c[1], c[2]):
        yield cv


def dur_of(char, text):
    return voice.synth(char, text, VOICE_DIR)["duration"]


def seq(start, items):
    """items: [(char, text, gap_before), ...] -> list[Line] laid end to end."""
    out, t = [], start
    for char, text, gap in items:
        t += gap
        out.append(Line(char, text, at=round(t, 2)))
        t += dur_of(char, text)
    return out


def S(sid, fn, dur=None, lines=(), sfx=(), bed=None, bed_db=-16, music=None, hits=(), tr="cut", td=0.6,
      tail=1.0):
    """Build a Shot whose duration is known now (lines synthesized), with an ambience bed fitted to it."""
    sh = Shot(sid, fn, duration=None, lines=list(lines), sfx=list(sfx), music=music, music_hits=list(hits),
              transition=tr, trans_dur=td, tail=tail)
    sh.resolve()
    if dur is not None:
        sh.duration = max(dur, sh.duration if lines else 0.0)
    sh.duration = round(sh.duration * FPS) / FPS
    if bed:
        sh.sfx.insert(0, Sfx(bed, 0.0, bed_db, dur=sh.duration))
    return sh


def lying(cv, who, x, y, s, t, **pose):
    """A character lying on the floor on their side, head to the left, feet at (x, y)."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(-88)
    R.draw(cv, who, x=0, y=0, s=s, t=t, breathe=0.4, **pose)
    cv.restore()


def wiggle(t, amt=1.0, speed=1.0, seed=0):
    return amt * K.noise1(t * speed, seed)


def bob(t, amt=3.0, speed=2.0):
    return amt * math.sin(t * speed)


def title(cv, a, t):
    """'The Weather Keeper of Block C' in flat graphic lettering on the white sky."""
    if a <= 0.01:
        return
    y = 330 + (1 - K.ease_out(a)) * 18
    f1 = K.font(118, "DejaVu Sans", bold=True)
    f2 = K.font(58, "DejaVu Sans", bold=True)
    s1, s2 = "THE WEATHER KEEPER", "of Block C"
    w1, w2 = f1.measureText(s1), f2.measureText(s2)
    # flat offset shadow + ink
    cv.drawString(s1, W / 2 - w1 / 2 + 6, y + 6, f1, K.fill("#d6a46a", 0.9 * a))
    cv.drawString(s1, W / 2 - w1 / 2, y, f1, K.fill("#4a2c1a", a))
    cv.drawString(s2, W / 2 - w2 / 2 + 4, y + 84, f2, K.fill("#d6a46a", 0.9 * a))
    cv.drawString(s2, W / 2 - w2 / 2, y + 80, f2, K.fill("#c0502f", a))
