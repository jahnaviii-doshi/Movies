"""Helpers for WK sc08 / sc09 / credits (scene fork D)."""
from __future__ import annotations

import math
from contextlib import contextmanager

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, ellipse, smooth_path, lerp, clamp
from ..rig import CAST
from ..sets import weather_fx as WX


# ------------------------------------------------------------------ colour flood
@contextmanager
def graded(cv, light="monsoon", amount=1.0):
    """Full-frame grade (one layer): the monsoon colours flooding in."""
    if amount <= 0.01:
        yield cv
        return
    with K.lit(cv, light, amount=clamp(amount)):
        yield cv


def crossfade(cv, draw_a, draw_b, k):
    """Draw scene A, then scene B over it at alpha k (both full frames)."""
    draw_a(cv)
    if k > 0.01:
        with K.layer(cv, alpha=clamp(k)):
            draw_b(cv)


# ------------------------------------------------------------------ rig geometry
def hand_pos(who, x, y, s, side="r", flip=False, lean=0.0, arms=None, legs="stand"):
    """World position of a character's hand (replicates Human.draw_arm geometry)."""
    rig = CAST[who]
    arms = arms or {}
    sh_deg, el_deg = arms.get(side, (8, 10))
    sgn = -1 if side == "l" else 1
    sx, sy = sgn * (rig.shoulder_w + 4), rig.neck_y + 16
    a1 = math.radians(sh_deg) * sgn
    ex, ey = sx + math.sin(a1) * rig.upper_arm, sy + math.cos(a1) * rig.upper_arm
    a2 = a1 - math.radians(el_deg) * sgn
    hx, hy = ex + math.sin(a2) * rig.fore_arm, ey + math.cos(a2) * rig.fore_arm
    if legs == "sit":
        hy += -rig.hip_y - 4
    r = math.radians(lean)
    rx, ry = hx * math.cos(r) - hy * math.sin(r), hx * math.sin(r) + hy * math.cos(r)
    return (x + (-rx if flip else rx) * s, y + ry * s)


def head_pos(who, x, y, s, flip=False, lean=0.0, turn=0.35, legs="stand"):
    rig = CAST[who]
    hx, hy = rig.stoop * 0.8 + turn * 4, rig.neck_y - rig.head_r * 0.82
    if legs == "sit":
        hy += -rig.hip_y - 4
    r = math.radians(lean)
    rx, ry = hx * math.cos(r) - hy * math.sin(r), hx * math.sin(r) + hy * math.cos(r)
    return (x + (-rx if flip else rx) * s, y + ry * s)


def draw_lying_head(cv, who, x, y, s, t, rot=-78, **pose):
    """Just the rig's head, rotated (lying on a pillow). (x, y) = head centre."""
    from ....rig.human import Pose
    rig = CAST[who]
    p = Pose(t=t, **pose)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.rotate(rot)
    rig.draw_head(cv, p)
    cv.restore()


# ------------------------------------------------------------------ props
def schoolbag(cv, x, y, s, t, color="#3d7fc4"):
    """A small backpack centred at (x, y) (draw BEHIND the character, peeking out at the sides)."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    b = K.rrect(-46, -60, 92, 110, 18)
    cv.drawPath(b, fill(color)); cv.drawPath(b, stroke("line", 3))
    cv.drawPath(K.rrect(-34, 10, 68, 34, 10), fill(K.shade(color, -0.15)))
    cv.drawPath(K.rrect(-34, 10, 68, 34, 10), stroke("line", 2.4))
    cv.restore()


def lota_pour(cv, x0, y0, x1, y1, t, a=1.0):
    """A thin silvery water stream from (x0,y0) curving down to (x1,y1), with droplets."""
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(x0 + (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.1, x1, y1)
    cv.drawPath(p, stroke("#bfe3ff", 5, 0.85 * a))
    cv.drawPath(p, stroke("#ffffff", 1.6, 0.8 * a))
    r = K.rng(5)
    for i in range(6):
        ph = (t * 3 + r.random()) % 1
        cv.drawCircle(x1 + r.uniform(-14, 14), y1 - 6 + ph * 18, 2.6, fill("#cfeaff", (1 - ph) * a))


def notebook_spread(cv, cx, cy, w, t, wet=0.0):
    """The weather notebook open flat: left page Meghnath's old cramped diagrams (water-stained),
    right page Tara's neat new ones (arrows, a cloud, a little wavy doodle). No legible words."""
    h = w * 0.62
    cv.save(); cv.translate(cx, cy)
    # cover + string
    cv.drawPath(K.rrect(-w / 2 - 14, -h / 2 - 12, w + 28, h + 24, 10), fill("#6b4a2e"))
    cv.drawPath(K.rrect(-w / 2 - 14, -h / 2 - 12, w + 28, h + 24, 10), stroke("line", 3))
    for d in (-1, 1):
        pg = K.poly([(0, -h / 2 + 4), (d * w / 2, -h / 2), (d * w / 2, h / 2), (0, h / 2 + 6)])
        cv.drawPath(pg, fill("#f7efdc" if d == 1 else "#ece0c4")); cv.drawPath(pg, stroke("line", 2.4))
    cv.drawLine(0, -h / 2 + 4, 0, h / 2 + 6, stroke("#b79c74", 3))
    # water stains on the old page
    for (sx, sy, rr) in [(-w * 0.32, -h * 0.18, w * 0.08), (-w * 0.12, h * 0.22, w * 0.06)]:
        cv.drawCircle(sx, sy, rr, stroke("#c9ad7e", 3, 0.6))
        cv.drawCircle(sx, sy, rr * 0.8, fill("#d8c39b", 0.35))
    # old page: cramped scribbled squiggle lines (illegible "handwriting") + a spiral
    r = K.rng(77)
    for j in range(7):
        yy = -h * 0.38 + j * h * 0.11
        pts = [(-w * 0.45 + i * w * 0.035, yy + r.uniform(-2, 2)) for i in range(11)]
        cv.drawPath(smooth_path(pts, close=False), stroke("#5a4a3a", 1.8, 0.7))
    sp = skia.Path()
    for i in range(60):
        a = i * 0.32; rr = 2 + i * 0.6
        px, py = -w * 0.25 + math.cos(a) * rr, h * 0.25 + math.sin(a) * rr
        sp.moveTo(px, py) if i == 0 else sp.lineTo(px, py)
    cv.drawPath(sp, stroke("#5a4a3a", 1.8, 0.7))
    # new page (Tara): neat cloud, arrows, wavy doodle, tidy dashes
    ink = "#2d3a63"
    cx2, cy2 = w * 0.24, -h * 0.12
    for (dx, dy, rr) in [(-26, 6, 20), (0, -8, 26), (26, 6, 20), (0, 12, 18)]:
        cv.drawCircle(cx2 + dx, cy2 + dy, rr, fill("#ffffff"))
    for (dx, dy, rr) in [(-26, 6, 20), (0, -8, 26), (26, 6, 20)]:
        cv.drawCircle(cx2 + dx, cy2 + dy, rr, stroke(ink, 2.6))
    # wavy "warm + slow" doodle under the cloud (no letters)
    wv = [(cx2 - 50 + i * 10, cy2 + 52 + 6 * math.sin(i * 1.2)) for i in range(11)]
    cv.drawPath(smooth_path(wv, close=False), stroke("#ee6f57", 3))
    # arrows
    for (ax, ay, bx, by) in [(w * 0.06, -h * 0.34, w * 0.14, -h * 0.22), (w * 0.42, h * 0.08, w * 0.36, -h * 0.02)]:
        cv.drawLine(ax, ay, bx, by, stroke(ink, 3))
        ang = math.atan2(by - ay, bx - ax)
        for d in (-0.5, 0.5):
            cv.drawLine(bx, by, bx - math.cos(ang + d) * 12, by - math.sin(ang + d) * 12, stroke(ink, 3))
    for j in range(4):
        yy = h * 0.2 + j * h * 0.06
        cv.drawLine(w * 0.08, yy, w * (0.38 - 0.05 * (j % 2)), yy, stroke(ink, 2, 0.75))
    # Tara's tiny sun-crossed-out + raindrop icons, tidy
    cv.drawCircle(w * 0.1, h * 0.38, 8, stroke("#f2c94c", 2.4))
    cv.drawPath(K.poly([(w * 0.2, h * 0.32), (w * 0.215, h * 0.38), (w * 0.185, h * 0.38)]), fill("#5b9bd5"))
    cv.restore()


def drop_on_face(cv, x, y, t, t0, dur=0.55, s=1.0):
    """A single fat raindrop falling to (x, y), arriving at t0 + dur, then a tiny splash."""
    if t < t0:
        return
    k = (t - t0) / dur
    if k < 1:
        yy = lerp(y - 520 * s, y, K.ease_in(k))
        cv.drawPath(K.poly([(x, yy - 16 * s), (x + 7 * s, yy), (x - 7 * s, yy)]), fill("#cfeaff"))
        cv.drawCircle(x, yy + 2 * s, 7 * s, fill("#cfeaff"))
        cv.drawCircle(x - 2 * s, yy - 1 * s, 2 * s, fill("#ffffff"))
    elif k < 2.2:
        u = (k - 1) / 1.2
        for i in range(6):
            a = math.pi + i * math.pi / 5
            rr = 26 * s * K.ease_out(u)
            cv.drawCircle(x + math.cos(a) * rr, y + math.sin(a) * rr * 0.6, 3.5 * s * (1 - u), fill("#cfeaff", 1 - u))


def rain_front(cv, t, amount=1.0, splash_y=None, seed=3, wind=0.08):
    WX.rain(cv, t, amount, wind=wind, splash_y=splash_y, seed=seed)


def sparkle_burst(cv, t, x, y, a=1.0, seed=3, spread=90, color="#fff6c8"):
    fx.sparkles(cv, t, x, y, spread=spread, n=12, color=color, size=7, seed=seed, a=a)


def fit_beds(shots):
    """Stretch every ambience bed (Sfx at 0 with a dur) to its resolved shot length."""
    for s in shots:
        s.resolve()
        for x in s.sfx:
            if x.at == 0 and x.dur is not None:
                x.dur = s.duration
    return shots
