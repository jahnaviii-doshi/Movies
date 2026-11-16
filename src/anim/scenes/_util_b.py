"""Helpers for scenes 4-6 (scene fork B)."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import fill, stroke, ellipse, smooth_path, lerp, clamp
from ..rig import chars
from ..timeline import Sfx


def bed(name, dur, gain=-14):
    return Sfx(name, 0.0, gain, dur=dur)


# ------------------------------------------------------------ IK
def shoulder_world(who, x, y, s, side, flip=False, sit=False):
    rig = chars.CAST[who]
    sgn = -1 if side == "l" else 1
    lx = sgn * (rig.shoulder_w + 4)
    ly = rig.neck_y + 16 + ((-rig.hip_y - 4) if sit else 0)
    if flip:
        lx = -lx
    return x + lx * s, y + ly * s


def _unlean(x, y, target, lean):
    if not lean:
        return target
    a = math.radians(-lean)
    dx, dy = target[0] - x, target[1] - y
    return x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)


def reach(who, x, y, s, side, target, flip=False, sit=False, lean=0.0, branch=1):
    """(shoulder_deg, elbow_deg) so that the hand of `side` lands on target (world px)."""
    rig = chars.CAST[who]
    target = _unlean(x, y, target, lean)
    sx, sy = shoulder_world(who, x, y, s, side, flip, sit)
    dx, dy = (target[0] - sx) / s, (target[1] - sy) / s
    if flip:
        dx = -dx
    U, F = rig.upper_arm, rig.fore_arm
    L = max(1e-3, min(math.hypot(dx, dy), U + F - 0.5))
    th = math.atan2(dx, dy)
    d = math.acos(clamp((U * U + L * L - F * F) / (2 * U * L), -1, 1))
    g = math.acos(clamp((F * F + L * L - U * U) / (2 * F * L), -1, 1))
    if branch < 0:          # elbow-down solution
        d, g = -d, -g
    if side == "r":
        return math.degrees(th + d), math.degrees(d + g)
    return -math.degrees(th - d), math.degrees(d + g)


def head_world(who, x, y, s, flip=False, turn=0.35, sit=False, lean=0.0):
    rig = chars.CAST[who]
    hx, hy = rig.stoop * 0.8 + turn * 4, rig.neck_y - rig.head_r * 0.82
    if sit:
        hy += -rig.hip_y - 4
    dx, dy = (-hx if flip else hx) * s, hy * s
    a = math.radians(lean)
    return x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)


def cam(cv, cx, cy, z=1.0, t=0.0, shake=0.0):
    """core.camera with the view clamped so no black border shows (needs z >= 1)."""
    z = max(1.0, z)
    hw, hh = 960 / z, 540 / z
    cx = clamp(cx, hw, 1920 - hw)
    cy = clamp(cy, hh, 1080 - hh)
    return K.camera(cv, cx, cy, z, t=t, shake=shake)


def ear_flush(cv, who, x, y, s, a, flip=False, turn=0.35):
    """Red embarrassment flush over the ears/cheeks."""
    if a <= 0:
        return
    hx, hy = head_world(who, x, y, s, flip, turn)
    r = chars.CAST[who].head_r * s
    for side in (-1, 1):
        ex = hx + side * r * 0.95
        cv.drawCircle(ex, hy + 4 * s, 16 * s, K.rad_a((ex, hy + 4 * s), 16 * s, [("#ff2a2a", 0.75 * a), ("#ff2a2a", 0)]))
        cx = hx + side * r * 0.5
        cv.drawCircle(cx, hy + 22 * s, 18 * s, K.rad_a((cx, hy + 22 * s), 18 * s, [("#ff3b3b", 0.4 * a), ("#ff3b3b", 0)]))


def dizzy_stars(cv, cx, cy, r, t, a=1.0, n=4):
    for i in range(n):
        ang = t * 5 + i * 2 * math.pi / n
        fx.star4(cv, cx + math.cos(ang) * r, cy + math.sin(ang) * r * 0.35, 13, "#ffe66b", a, rot=t * 90)


# ------------------------------------------------------------ crayon scribble (Kabir's fake kindness)
def _wob(pts, seed, amp=4):
    r = K.rng(seed)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def crayon(cv, pts, col, w=14, seed=1, close=False, passes=2):
    for k in range(passes):
        p = K.poly(_wob(pts, seed + k * 13, 6), close=close)
        cv.drawPath(p, stroke(col, w * (1 - 0.25 * k), 0.85))


def scribble_scene(cv, t=0.0):
    """A five-year-old's crayon drawing: bus in a flood, a helicopter, a rope, a hero (Kabir)."""
    cv.drawRect(skia.Rect.MakeWH(1920, 1080), fill("#fbf7ec"))
    # paper lines
    for i in range(8):
        cv.drawLine(0, 140 + i * 120, 1920, 140 + i * 120, stroke("#cfe0f2", 3))
    # flood waves
    for row in range(3):
        pts = [(x, 760 + row * 70 + 26 * math.sin(x / 60 + row)) for x in range(0, 1960, 40)]
        crayon(cv, pts, "#2f6fe0", 18, seed=10 + row)
    # bus
    crayon(cv, [(420, 520), (1060, 520), (1060, 760), (420, 760)], "#f2b200", 22, seed=3, close=True)
    for i in range(5):
        crayon(cv, [(460 + i * 115, 560), (545 + i * 115, 560), (545 + i * 115, 640), (460 + i * 115, 640)],
               "#2b2b2b", 9, seed=20 + i, close=True)
        cv.drawCircle(500 + i * 115, 600, 14, fill("#e36b8a", 0.8))      # tiny faces
    for wx in (530, 950):
        cv.drawCircle(wx, 770, 50, stroke("#2b2b2b", 14, 0.85))
    # helicopter
    crayon(cv, [(1260, 230), (1560, 230), (1600, 330), (1300, 360), (1240, 300)], "#1a9e5a", 20, seed=5, close=True)
    crayon(cv, [(1240, 170), (1640, 170)], "#2b2b2b", 12, seed=6)
    crayon(cv, [(1440, 170), (1440, 230)], "#2b2b2b", 10, seed=7)
    crayon(cv, [(1560, 290), (1760, 270), (1790, 230)], "#1a9e5a", 14, seed=8)
    # rope down to the bus
    crayon(cv, [(1420, 360), (1380, 450), (1300, 520), (1180, 560)], "#a0522d", 10, seed=9)
    # stick-figure hero with a red cap, flexing
    cv.drawCircle(1520, 520, 44, stroke("#2b2b2b", 10, 0.9))
    crayon(cv, [(1470, 480), (1560, 470)], "#e02a2a", 22, seed=12)
    crayon(cv, [(1520, 565), (1520, 700)], "#2b2b2b", 10, seed=13)
    crayon(cv, [(1440, 560), (1520, 610), (1600, 560)], "#2b2b2b", 10, seed=14)
    crayon(cv, [(1520, 700), (1470, 790)], "#2b2b2b", 10, seed=15)
    crayon(cv, [(1520, 700), (1570, 790)], "#2b2b2b", 10, seed=16)
    # sun with a face
    cv.drawCircle(230, 200, 90, fill("#ffd23f", 0.85))
    for i in range(10):
        a = i * 0.628
        crayon(cv, [(230 + math.cos(a) * 110, 200 + math.sin(a) * 110),
                    (230 + math.cos(a) * 160, 200 + math.sin(a) * 160)], "#ffb000", 10, seed=30 + i)


# ------------------------------------------------------------ props
def crate(cv, x, y, w=180, h=110):
    """Upturned wooden crate; (x, y) = bottom centre."""
    body = K.rrect(x - w / 2, y - h, w, h, 6)
    cv.drawPath(body, K.lin((0, y - h), (0, y), ["#b07a43", "#7a4f28"]))
    for i in range(1, 3):
        cv.drawLine(x - w / 2 + 6, y - h + i * h / 3, x + w / 2 - 6, y - h + i * h / 3, stroke("#5a3618", 3))
    cv.drawLine(x - w / 2 + 8, y - h + 6, x + w / 2 - 8, y - 6, stroke("#8a5a2e", 6))
    cv.drawPath(body, stroke("line", 3.2))


def wrinkled_hand(cv, x, y, s=1.0, thumb=1.0, t=0.0, from_right=True):
    """An old ironing-wala's hand + forearm entering from the right, thumbs-up."""
    cv.save(); cv.translate(x, y); cv.scale(-s if not from_right else s, s)
    skin, dark = "#9a6440", "#6d4228"
    arm = K.limb(260, 40, 0, 0, 70, 56)
    cv.drawPath(arm, fill(skin)); cv.drawPath(arm, stroke("line", 3))
    cv.drawPath(K.limb(260, 40, 120, 22, 80, 74), fill("#f3efe4"))      # vest sleeve
    cv.drawPath(K.limb(260, 40, 120, 22, 80, 74), stroke("line", 3))
    fist = K.rrect(-36, -26, 62, 56, 18)
    cv.drawPath(fist, fill(skin)); cv.drawPath(fist, stroke("line", 3))
    for i in range(3):
        cv.drawLine(-30, -10 + i * 13, 16, -10 + i * 13, stroke(dark, 2.4))
    th = K.limb(-16, -22, -16 - 4 * thumb, -22 - 48 * thumb, 20, 17)
    cv.drawPath(th, fill(skin)); cv.drawPath(th, stroke("line", 3))
    for i in range(3):
        cv.drawLine(40 + i * 40, 4, 60 + i * 40, 30, stroke(dark, 1.6))
    cv.restore()


def shiny_toffee(cv, x, y, s=1.0, t=0.0, a=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawCircle(0, 0, 40, K.rad_a((0, 0), 40, [("rose", 0.45 * a), ("rose", 0)]))
    for d in (-1, 1):
        w = K.poly([(d * 10, -2), (d * 30, -14), (d * 26, 0), (d * 30, 14)])
        cv.drawPath(w, fill("#ff6fa5", a)); cv.drawPath(w, stroke("line", 2, a))
    body = ellipse(0, 0, 14, 10)
    cv.drawPath(body, K.lin((-14, -10), (14, 10), ["#fff0a0", "#ffb02e", "#ff6fa5"], a=a))
    cv.drawPath(body, stroke("line", 2, a))
    cv.drawLine(-6, -5, 2, -7, stroke("#ffffff", 2.4, 0.9 * a))
    cv.restore()


BEDS = {"crickets_bed", "night_bed", "day_bed", "heat_cicadas", "wind_flight", "sparrows_dawn"}


def finalize(shots, scene):
    """Sequential ids S{scene}_SH{n}; ambience beds stretched to each shot's length (line-driven shots
    get a generous bed, the mixer trims at the next bed)."""
    for i, s in enumerate(shots):
        s.id = f"S{scene:02d}_SH{i + 1:02d}"
        if s.duration is None:
            s.resolve()                     # voice lines are cached; fixes the shot length now
        for x in s.sfx:
            if x.name in BEDS:
                x.dur = s.duration + 0.6
    return shots
