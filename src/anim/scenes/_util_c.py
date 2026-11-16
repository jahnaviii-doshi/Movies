"""Helpers shared by sc07 / sc08 (scene fork C)."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import fill, stroke
from ..rig import chars
from ..rig.human import Pose, auto_blink
from ..rig import animals as A
from ..timeline import Sfx


_BEDS: set[int] = set()


def bed(name, dur=None, gain=-18.0):
    """Ambience bed covering the whole shot (dur is fitted to the shot by fit_beds)."""
    x = Sfx(name, 0.0, gain, dur=dur)
    _BEDS.add(id(x))
    return x


def fit_beds(shots):
    """Resolve shots (voices are cached) and stretch every bed to exactly the shot length."""
    for s in shots:
        s.resolve()
        for x in s.sfx:
            if id(x) in _BEDS:
                x.dur = round(s.duration - x.at, 3)
    return shots


def pan_pos(tx, ty, ts, side="l", tilt=0.0):
    """Screen position of the top centre of a Tola pan (where a bubble sits)."""
    a = math.radians(tilt)
    ex = -180 if side == "l" else 180
    px, py = ex * math.cos(a), -330 + ex * math.sin(a)
    return tx + px * ts, ty + (py + 150) * ts


def reach(sx, sy, tx, ty, side="r", flip=False):
    """Shoulder angle (deg) for a straight arm from shoulder (sx,sy) toward target (tx,ty).
    Rig angle convention: 0 = down, + = outward for that side."""
    dx, dy = tx - sx, ty - sy
    if flip:
        dx = -dx
    sgn = 1 if side == "r" else -1
    a = math.degrees(math.atan2(dx * sgn, dy))
    return a


def shoulder(who, x, y, s, side="r", flip=False):
    rig = chars.CAST[who]
    sgn = (-1 if side == "l" else 1) * (-1 if flip else 1)
    return x + sgn * (rig.shoulder_w + 4) * s, y + (rig.neck_y + 16) * s


def amma_specs(cv, x, y, s, t, alpha=1.0, turn=0.35, head_tilt=0.0, flip=False):
    """Draw only Mishri Amma's round gold spectacles (and a hint of her eyes) at her head position."""
    rig = chars.CAST["amma"]
    p = Pose(x=x, y=y, s=s, t=t, turn=turn, head_tilt=head_tilt, flip=flip)
    breath = math.sin(t * 2.1 + rig.seed) * 1.4
    cv.save()
    cv.translate(x, y)
    cv.scale(-s if flip else s, s)
    hx, hy = rig.head_anchor(p)
    cv.translate(hx, hy + breath * 0.5)
    cv.rotate(head_tilt + rig.stoop * 0.4)
    pt = skia.Paint(); pt.setAlphaf(K.clamp(alpha))
    cv.saveLayer(None, pt)
    rig.draw_head_extra(cv, p)
    cv.restore()
    cv.restore()


def amma(cv, x, y, s, t, alpha=1.0, desat=0.0, light="shop", specs_boost=0.0, sparkle=0.0, **pose):
    """Mishri Amma; faint when alpha<1 (+ desaturated), with stronger spectacles and drifting sparkles."""
    with K.lit(cv, light, alpha=alpha, desat=desat):
        chars.draw(cv, "amma", x=x, y=y, s=s, t=t, **pose)
    if specs_boost > 0:
        amma_specs(cv, x, y, s, t, alpha=specs_boost, turn=pose.get("turn", 0.35),
                   head_tilt=pose.get("head_tilt", 0.0), flip=pose.get("flip", False))
    if sparkle > 0:
        # motes of sugar drifting up off her, like she is evaporating
        r = K.rng(77)
        for i in range(26):
            ph = r.uniform(0, 1)
            u = (t * r.uniform(0.12, 0.25) + ph) % 1.0
            px = x + r.uniform(-60, 60) * s + math.sin(t * 1.3 + i) * 10
            py = y - r.uniform(20, 200) * s - u * 160 * s
            a = sparkle * (1 - u) * (0.5 + 0.5 * math.sin(t * 3 + i))
            fx.star4(cv, px, py, 5 * s * (1 - u * 0.5), "#ffe0ec", a)


def sugar_rain(cv, t, rect, n=70, a=1.0, seed=5, color="#ffe0ec"):
    """Sparkles drifting DOWN like soft rain."""
    x0, y0, x1, y1 = rect
    r = K.rng(seed)
    for i in range(n):
        sx = r.uniform(x0, x1)
        sp = r.uniform(60, 140)
        y = y0 + (r.uniform(0, y1 - y0) + t * sp) % (y1 - y0)
        x = sx + math.sin(t * 1.5 + i) * 8
        tw = 0.5 + 0.5 * math.sin(t * 4 + i * 1.7)
        fx.star4(cv, x, y, r.uniform(3, 6), color, a * tw)
        cv.drawLine(x, y - 10, x, y - 22, stroke(color, 1.2, a * 0.35 * tw))


def flicker_val(t, base=0.6, seed=3):
    """A dying-bulb stutter around `base`."""
    n = K.noise1(t * 9, seed) * 0.5 + K.noise1(t * 23, seed + 4) * 0.5
    drop = 1.0 if (math.sin(t * 7.3) > 0.82 or math.sin(t * 3.1 + 1) > 0.93) else 0.0
    return K.clamp(base * (0.75 + 0.35 * n) * (1 - 0.7 * drop))


def thali(cv, x, y, s=1.0):
    cv.drawOval(skia.Rect.MakeLTRB(x - 34 * s, y - 10 * s, x + 34 * s, y + 10 * s), K.lin(
        (x - 34 * s, 0), (x + 34 * s, 0), ["#9aa1ad", "#e7ebf2", "#8a909c"]))
    cv.drawOval(skia.Rect.MakeLTRB(x - 34 * s, y - 10 * s, x + 34 * s, y + 10 * s), stroke("line", 2))
    cv.drawOval(skia.Rect.MakeLTRB(x - 14 * s, y - 6 * s, x + 2 * s, y + 1 * s), fill("#e3a72f"))
    cv.drawOval(skia.Rect.MakeLTRB(x + 4 * s, y - 6 * s, x + 20 * s, y + 0 * s), fill("#f3eadb"))
    cv.drawOval(skia.Rect.MakeLTRB(x - 24 * s, y - 2 * s, x - 6 * s, y + 5 * s), fill("#c9a06a"))


def tola(cv, x, y, s, t, **kw):
    A.draw_scale(cv, A.ScalePose(x=x, y=y, s=s, t=t, **kw))


def blink(t, seed):
    return auto_blink(t, seed)


def cam(cv, cx, cy, zoom=1.0, rot=0.0, shake=0.0, t=0.0):
    """core.camera with the view clamped inside the 1920x1080 world (no black edges)."""
    zoom = max(1.0, zoom)
    hw, hh = K.W / (2 * zoom), K.H / (2 * zoom)
    cx = K.clamp(cx, hw, K.W - hw)
    cy = K.clamp(cy, hh, K.H - hh)
    return K.camera(cv, cx, cy, zoom, rot=rot, shake=shake, t=t)


def torch_light(cv, t, x, y, ang):
    """stairwell.draw_torch_light works in device space (it resets the matrix); map the torch
    position through the current transform so it follows cameras, bubbles and draft scale."""
    from ..sets import stairwell as ST
    m = cv.getTotalMatrix()
    p = m.mapXY(x, y)
    ST.draw_torch_light(cv, t, (p.x(), p.y(), ang))
