"""Helpers shared by sc06 / sc07 (Weather Keeper scene fork C)."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, clamp, lerp
from ....timeline import Sfx
from .. import rig as R
from ..rig import draw, draw_bhaap
from ..sets import roof, weather_fx as WF

_BEDS: set[int] = set()


def bed(name, gain=-18.0, **params):
    """Ambience bed covering the whole shot (dur fitted to the shot by fit_beds)."""
    x = Sfx(name, 0.0, gain, dur=None, params=params)
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


def ccam(cx, cy, z):
    """Clamp a camera so a 1920x1080 world never shows black edges."""
    hw, hh = W / (2 * z), H / (2 * z)
    return (clamp(cx, hw, W - hw), clamp(cy, hh, H - hh), z)


def push(c, a, b, ease=K.ease_in_out):
    """Interpolate camera tuples a -> b over the shot, clamped."""
    e = ease(c.u)
    return ccam(lerp(a[0], b[0], e), lerp(a[1], b[1], e), lerp(a[2], b[2], e))


def roof_bg(cv, c, weather, cam, **kw):
    roof.draw_roof(cv, c.t, weather, cam=cam, **kw)


def night_sky(cv, t, top="#0c1230", bottom="#2a3560", stars=True):
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), [top, bottom]))
    if stars:
        K.stars(cv, W, H, t, n=200, seed=17, alpha=0.9)


def plane(cv, t, x0, y0, x1, y1, t0, t1, s=1.0):
    """A tiny plane blinking across the sky."""
    u = (t - t0) / (t1 - t0)
    if u < 0 or u > 1:
        return
    x, y = lerp(x0, x1, u), lerp(y0, y1, u)
    cv.drawCircle(x, y, 2.2 * s, fill("#e8ecff", 0.8))
    if int(t * 2.2) % 2 == 0:
        cv.drawCircle(x - 6 * s, y, 3.0 * s, fill("#ff5a5a", 0.95))
        fx.glow_dot(cv, x - 6 * s, y, 10 * s, "#ff5a5a", 0.6)


def lying_meghnath(cv, x, y, s, t, expr="sad", blink=0.0, look=(0, -0.6), brow_lift=-0.2):
    """Meghnath lying in bed under a blanket, head on the pillow at (x, y) (head centre), body to the right."""
    rig = R.CAST["meghnath"]
    # blanket mound
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    br = math.sin(t * 1.4) * 2
    blanket = K.smooth_path([(30, -10), (120, -46 - br), (260, -40 - br), (380, -30), (430, 0), (430, 40),
                             (30, 46)], tension=0.4)
    cv.drawPath(blanket, fill("#5a6a8c"))
    cv.drawPath(blanket, stroke("line", 3))
    for k in range(4):
        cv.drawLine(90 + k * 80, -30 - br, 110 + k * 80, 36, stroke("#4a587a", 2))
    cv.drawPath(K.rrect(-10, -26, 70, 30, 12), fill("#8a5a34"))       # cardigan sleeve over the blanket
    cv.drawPath(K.rrect(-10, -26, 70, 30, 12), stroke("line", 2.4))
    cv.restore()
    cv.save(); cv.translate(x - 12 * s, y - 36 * s); cv.rotate(-14); cv.scale(s, s)
    from ....rig.human import Pose
    rig.draw_head(cv, Pose(expr=expr, blink=blink, t=t, look=look, extra={"brow_lift": brow_lift, "sling": True}))
    cv.restore()


def photo_back(cv, x, y, s=1.0, up=0.0, t=0.0):
    """Varsha's photo frame on the bedside table: up 0 = lying face down, 1 = standing upright."""
    if up >= 0.98:
        R.draw_varsha_photo(cv, x, y, s, t)
        return
    cv.save(); cv.translate(x, y)
    # hinge at the front-bottom edge: draw as a frame rotated back toward lying
    h = 110 * s
    vis = lerp(0.12, 1.0, K.ease_in_out(up))
    cv.scale(1, vis)
    frame = K.rrect(-50 * s, -h, 100 * s, h, 6 * s)
    cv.drawPath(frame, fill("#6a4a32"))
    cv.drawPath(frame, stroke("line", 2.6))
    cv.drawRect(skia.Rect.MakeLTRB(-38 * s, -h + 12 * s, 38 * s, -12 * s), fill("#4e3624"))
    cv.restore()


def tumble_bhaap(cv, x, y, s, t, rot, **kw):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    draw_bhaap(cv, 0, 0, s, t, **kw)
    cv.restore()


def dust_world(cv, amount=1.0):
    """Context manager: draw through the brown-orange monochrome dust grade."""
    return WF.dust_grade(cv, amount)


def torch_glow(cv, x, y, ang, length=520, spread=26, a=0.35):
    """A warm torch cone (additive feel) in world coords."""
    r = math.radians(ang)
    pts = [(x, y)]
    for k in (-1, 1):
        rr = r + math.radians(spread) * k
        pts.append((x + math.cos(rr) * length, y + math.sin(rr) * length))
    p = K.poly([pts[0], pts[1], pts[2]])
    cv.drawPath(p, K.lin_a((x, y), (x + math.cos(r) * length, y + math.sin(r) * length),
                           [("#ffe6a8", a), ("#ffe6a8", 0)]))
    fx.glow_dot(cv, x, y, 30, "#fff1c8", 0.8)


def paper_plan(cv, t, prog, x=960, y=540, s=1.0):
    """Tara's torn notebook page: a pencil plan of who-stands-where around the trunk, revealed by prog 0..1."""
    cv.save(); cv.translate(x, y); cv.rotate(-3); cv.scale(s, s)
    page = K.poly([(-420, -300), (400, -310), (420, 290), (-410, 305), (-430, 120), (-418, 0)])
    cv.drawPath(page, fill("#000000", 0.25)) if False else None
    cv.drawRect(skia.Rect.MakeLTRB(-414, -296, 426, 316), fill("#000000", 0.18))
    cv.drawPath(page, fill("#fbf6e8"))
    for k in range(-5, 7):
        cv.drawLine(-410, k * 48, 410, k * 48 - 4, stroke("#a9c6e0", 1.6, 0.6))
    cv.drawLine(-330, -300, -330, 300, stroke("#e88a8a", 2, 0.6))
    # torn left edge
    for k in range(14):
        yy = -300 + k * 44
        cv.drawCircle(-420, yy, 9, fill("#2b2f3a"))
    pencil = stroke("#3a3f4a", 4.5)

    def seg(a, b):
        return clamp((prog - a) / (b - a))

    # trunk rectangle
    k = seg(0.0, 0.2)
    if k > 0:
        pts = [(-140, -40), (140, -40), (140, 120), (-140, 120), (-140, -40)]
        tot = 4
        n = k * tot
        for i in range(4):
            f = clamp(n - i)
            if f > 0:
                (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                cv.drawLine(x0, y0, lerp(x0, x1, f), lerp(y0, y1, f), pencil)
    # three keyholes on it
    for i, (kx, ky) in enumerate([(-80, 0), (80, 0), (0, 70)]):
        if prog > 0.2 + i * 0.05:
            cv.drawCircle(kx, ky, 10, pencil)
    # three stick figures + arrows
    figs = [(-300, 20, 0.35), (300, 20, 0.5), (0, 250, 0.65)]
    for (fx_, fy, st) in figs:
        k = seg(st, st + 0.12)
        if k > 0:
            cv.drawCircle(fx_, fy - 60, 18 * min(1, k * 2), pencil)
            if k > 0.5:
                cv.drawLine(fx_, fy - 42, fx_, fy + 10, pencil)
                cv.drawLine(fx_ - 24, fy - 20, fx_ + 24, fy - 20, pencil)
                cv.drawLine(fx_, fy + 10, fx_ - 18, fy + 46, pencil)
                cv.drawLine(fx_, fy + 10, fx_ + 18, fy + 46, pencil)
            if k > 0.9:
                tx = fx_ * 0.45
                ty = (fy - 20) * 0.5 + 20
                cv.drawLine(fx_ * 0.82, fy - 20, tx, ty, pencil)
                cv.drawLine(tx, ty, tx + (8 if fx_ < 0 else -8 if fx_ > 0 else 6), ty - 12, pencil)
                cv.drawLine(tx, ty, tx + (10 if fx_ < 0 else -10 if fx_ > 0 else -6), ty + 6, pencil)
    # a little cloud next to the boy's figure
    k = seg(0.85, 1.0)
    if k > 0:
        for i, (dx, dy, rr) in enumerate([(80, 190, 22), (108, 180, 26), (136, 192, 20)]):
            if k > i / 3:
                cv.drawCircle(dx, dy, rr, pencil)
    cv.restore()


def head_y(who, y, s, sit=False):
    """Screen y of a character's head centre (feet at y, or seat point at y when sit=True)."""
    rig = R.CAST[who]
    hy = (rig.neck_y - rig.head_r * 0.82) * s
    if sit:
        hy += (-rig.hip_y - 4) * s
    return y + hy


def frame_head(x, hy, z, at=0.36, dx=0.0):
    """Camera that puts a head at `at` (fraction from top) of the frame."""
    return ccam(x + dx, hy + (0.5 - at) * H / z, z)


def renumber(shots, scene):
    """Sequential ids S0N_SHnn (so inserted shots keep a clean numbering)."""
    for i, s in enumerate(shots, 1):
        s.id = f"S{scene:02d}_SH{i:02d}"
    return shots
