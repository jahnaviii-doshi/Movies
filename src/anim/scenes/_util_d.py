"""Helpers for sc09 / sc10 / credits (fork D): hand positions, the remembering thread,
Amma's wink, the little cousins, long sunrise shadows."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import fill, stroke, ellipse, smooth_path
from ..rig import chars
from ..rig.chars import Toddler
from ..rig.human import Pose


def hand_pos(who: str, x, y, s, arms=None, flip=False, legs="stand", side="r", frac=1.0):
    """Screen position of a rig's hand (frac<1 = point along the forearm, e.g. the wrist)."""
    rig = chars.CAST[who]
    default = (8, 10)
    sh, el = (arms or {}).get(side, default)
    sgn = -1 if side == "l" else 1
    sx, sy = sgn * (rig.shoulder_w + 4), rig.neck_y + 16
    a1 = math.radians(sh) * sgn
    ex, ey = sx + math.sin(a1) * rig.upper_arm, sy + math.cos(a1) * rig.upper_arm
    a2 = a1 - math.radians(el) * sgn
    hx, hy = ex + math.sin(a2) * rig.fore_arm * frac, ey + math.cos(a2) * rig.fore_arm * frac
    if legs == "sit":
        hy += -rig.hip_y - 4
    return (x + (-hx if flip else hx) * s, y + hy * s), a2


def thread_band(cv, x, y, s, t, a=1.0):
    """The glowing sugar thread tied round a wrist."""
    if a <= 0.01:
        return
    r = 11 * s
    fx.glow_dot(cv, x, y, r * 2.6, "#ffb3d1", 0.55 * a)
    cv.save(); cv.translate(x, y); cv.scale(1, 0.55)
    cv.drawCircle(0, 0, r, stroke("#ffe3ef", 3.2 * s, a))
    cv.drawCircle(0, 0, r, stroke("#ff8fbd", 1.4 * s, a))
    cv.restore()
    # little tail ends of the knot
    cv.drawPath(smooth_path([(x + r * 0.6, y + 2), (x + r * 1.2, y + r * 0.9 + math.sin(t * 3) * 2),
                             (x + r * 1.0, y + r * 1.5)], close=False), stroke("#ffd1e4", 2.0 * s, a))
    if math.sin(t * 2.3) > 0.4:
        fx.star4(cv, x - r * 0.6, y - r * 0.4, 5 * s, "#ffffff", a)


def thread_strand(cv, p0, p1, t, a=1.0, sag=30.0, width=3.0):
    """A glowing strand of sugar thread between two points."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag + math.sin(t * 2.5) * 4
    path = skia.Path(); path.moveTo(x0, y0); path.quadTo(mx, my, x1, y1)
    cv.drawPath(path, stroke("#ff9cc7", width * 4, 0.18 * a))
    cv.drawPath(path, stroke("#ffd6e8", width * 1.8, 0.45 * a))
    cv.drawPath(path, stroke("#fff4f8", width * 0.8, a))
    for i in range(6):
        u = ((t * 0.6 + i / 6) % 1)
        px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1
        py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1
        fx.star4(cv, px, py, 4 + 3 * math.sin(t * 5 + i), "#ffffff", a * 0.9)


def amma_wink(cv, x, y, s, t, turn=0.35, head_tilt=0.0, flip=False, side=-1, amount=1.0):
    """Close one of Amma's eyes (draw AFTER Amma). side=-1 = screen-left eye (when not flipped)."""
    if amount <= 0.01:
        return
    rig = chars.CAST["amma"]
    hx, hy = rig.head_anchor(Pose(turn=turn))
    breath = math.sin(t * 2.1 + rig.seed) * 1.4
    cv.save()
    cv.translate(x, y)
    cv.scale(-s if flip else s, s)
    cv.translate(hx, hy + breath * 0.5)
    cv.rotate(head_tilt + rig.stoop * 0.4)
    ox = rig.face_offset(Pose(turn=turn))
    far = side == 1
    ex = side * rig.eye_dx * (1 - 0.25 * turn if far else 1) + ox
    ey = rig.eye_y
    cv.drawOval(skia.Rect.MakeLTRB(ex - 12, ey - 15, ex + 12, ey + 14), fill(rig.skin, amount))
    cv.drawPath(smooth_path([(ex - 9, ey + 1), (ex, ey - 5), (ex + 9, ey + 1)], close=False),
                stroke("line", 3.2, amount))
    cv.drawCircle(ex, ey, 17, fill("#ffffff", 0.16 * amount))
    cv.drawCircle(ex, ey, 17, stroke("amma_spec", 3.4, amount))
    cv.restore()


# ---------------------------------------------------------------- the little cousins (sc10)
class CousinBoy(Toddler):
    name = "cousin_boy"
    seed = 11
    height = 170
    head_r = 46

    def body_colors(self):
        return ("#6fb3e8", "#3f7fb8")

    def sleeve(self):
        return ("#6fb3e8", 0.35)

    def leg_colors(self):
        return ("#3f5a8a", "skin")

    def draw_hair_front(self, cv, p):
        r = self.head_r
        cap = smooth_path([(-r * 1.0, -r * 0.1), (-r * 0.9, -r * 0.75), (0, -r * 1.06), (r * 0.9, -r * 0.75),
                           (r * 1.0, -r * 0.1), (r * 0.6, -r * 0.55), (0, -r * 0.62), (-r * 0.6, -r * 0.55)],
                          tension=0.5)
        cv.drawPath(cap, fill("hair")); cv.drawPath(cap, stroke("line", 2.6))


class CousinGirl(Toddler):
    name = "cousin_girl"
    seed = 12
    height = 175
    head_r = 47
    lash = True

    def body_colors(self):
        return ("#f08bb4", "#c9608c")

    def sleeve(self):
        return ("#f08bb4", 0.35)

    def leg_colors(self):
        return ("#f6d36a", "skin")

    def draw_hair_back(self, cv, p):
        r = self.head_r
        for side in (-1, 1):
            cv.drawCircle(side * r * 0.95, -r * 0.55, r * 0.36, fill("hair"))
            cv.drawCircle(side * r * 0.95, -r * 0.55, r * 0.36, stroke("line", 2.4))
            cv.drawCircle(side * r * 0.72, -r * 0.4, 5, fill("#ffd23f"))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        cap = smooth_path([(-r * 1.0, -r * 0.05), (-r * 0.9, -r * 0.75), (0, -r * 1.06), (r * 0.9, -r * 0.75),
                           (r * 1.0, -r * 0.05), (r * 0.7, -r * 0.5), (0, -r * 0.7), (-r * 0.7, -r * 0.5)],
                          tension=0.5)
        cv.drawPath(cap, fill("hair")); cv.drawPath(cap, stroke("line", 2.6))


COUSINS = {"cousin_boy": CousinBoy(), "cousin_girl": CousinGirl()}


def draw_cousin(cv, who, **pose):
    rig = COUSINS[who]
    p = Pose(**pose)
    if "blink" not in pose:
        from ..rig.human import auto_blink
        p.blink = auto_blink(p.t, rig.seed)
    rig.draw(cv, p)


# ---------------------------------------------------------------- long sunrise shadows
def long_shadows(cv, draw_fns, a=0.38, stretch=2.4, color="#3b1f3a"):
    """draw_fns: list of (fn(cv), foot_x, foot_y). Each figure is flipped downward from its feet
    and stretched toward the camera (sun low behind them)."""
    r, g, b = K.hexrgb(color)
    m = [0, 0, 0, 0, r, 0, 0, 0, 0, g, 0, 0, 0, 0, b, 0, 0, 0, a, 0]
    with K.layer(cv, color_filter=K.matrix_filter(m), image_filter=K.blur_filter(3)):
        for fn, fx_, fy_ in draw_fns:
            cv.save()
            cv.translate(fx_, fy_)
            cv.scale(1.0, -stretch * 0.45)
            cv.skew(0.0, 0.0)
            cv.translate(-fx_, -fy_)
            fn(cv)
            cv.restore()
