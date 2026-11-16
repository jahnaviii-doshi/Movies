"""Hand-held props and small objects, drawn in rig-local units."""
from __future__ import annotations

import math

import skia

from .. import core as K
from ..core import fill, stroke, ellipse, smooth_path, limb


def held(cv, name, x, y, ang, p):
    cv.save()
    cv.translate(x, y + 4)
    f = PROPS.get(name)
    if f:
        f(cv, p)
    cv.restore()


def bottle(cv, p):
    b = K.rrect(-9, -30, 18, 40, 5)
    cv.drawPath(b, fill("#9fd3e8", 0.85)); cv.drawPath(b, stroke("line", 2.4))
    cv.drawRect(skia.Rect.MakeXYWH(-6, -38, 12, 8), fill("#3a7bd5")); cv.drawRect(skia.Rect.MakeXYWH(-6, -38, 12, 8), stroke("line", 2))


def torch(cv, p):
    body = K.rrect(-8, -6, 16, 44, 4)
    cv.drawPath(body, fill("#4a4f5c")); cv.drawPath(body, stroke("line", 2.4))
    cv.drawPath(K.rrect(-11, -14, 22, 12, 3), fill("#9aa1ad"))


def book(cv, p):
    bk = K.poly([(-26, -4), (0, 2), (26, -4), (26, 22), (0, 28), (-26, 22)])
    cv.drawPath(bk, fill("#f6efe0")); cv.drawPath(bk, stroke("line", 2.4))
    cv.drawLine(0, 2, 0, 28, stroke("line", 2))
    cv.drawPath(K.poly([(-26, 22), (0, 28), (26, 22), (26, 26), (0, 32), (-26, 26)]), fill("#d8333d"))


def laddoo(cv, p):
    cv.drawCircle(0, -10, 22, K.rad_a((0, -10), 22, [("gold", 0.5), ("gold", 0)]))
    cv.drawCircle(0, -10, 11, K.rad((-3, -14), 12, ["#ffe08a", "saffron", "#c97a12"]))
    for i in range(6):
        a = i * 1.05
        cv.drawCircle(math.cos(a) * 6, -10 + math.sin(a) * 6, 1.6, fill("#fff2c0"))
    cv.drawCircle(0, -10, 11, stroke("line", 2))


def toffee(cv, p):
    cv.drawPath(K.poly([(-18, -14), (-8, -8), (-18, -2)]), fill("#ff6fa5"))
    cv.drawPath(K.poly([(18, -14), (8, -8), (18, -2)]), fill("#ff6fa5"))
    cv.drawPath(ellipse(0, -8, 10, 7), fill("#ffd36b")); cv.drawPath(ellipse(0, -8, 10, 7), stroke("line", 2))


def kulfi(cv, p):
    cup = K.poly([(-12, -4), (12, -4), (8, 16), (-8, 16)])
    cv.drawPath(cup, fill("#b4613f")); cv.drawPath(cup, stroke("line", 2))
    cv.drawPath(ellipse(0, -6, 12, 7), fill("#f6f0d8")); cv.drawCircle(0, -10, 5, fill("pistachio"))
    cv.drawCircle(0, -8, 22, K.rad_a((0, -8), 22, [("pistachio", 0.35), ("pistachio", 0)]))


def lota(cv, p):
    body = ellipse(0, 6, 15, 13)
    cv.drawPath(body, K.rad((-4, 2), 16, ["brass_light", "brass", "brass_dark"])); cv.drawPath(body, stroke("line", 2))
    cv.drawPath(K.rrect(-7, -12, 14, 8, 3), fill("brass")); cv.drawPath(K.rrect(-7, -12, 14, 8, 3), stroke("line", 2))


def slippers(cv, p):
    for dx in (-8, 8):
        s = K.rrect(dx - 7, -6, 14, 32, 7)
        cv.drawPath(s, fill("#7b4a8f")); cv.drawPath(s, stroke("line", 2))


def fan(cv, p):
    cv.drawLine(0, 0, 0, -26, stroke("wood", 4))
    f = smooth_path([(0, -26), (-30, -40), (-34, -70), (0, -82), (34, -70), (30, -40)], tension=0.5)
    cv.drawPath(f, fill("#d7b46a")); cv.drawPath(f, stroke("line", 2.2))
    for i in range(-3, 4):
        cv.drawLine(0, -28, i * 9, -78, stroke("#b08a40", 1.2))


def cap(cv, p):
    d = ellipse(0, -10, 24, 16)
    cv.drawPath(d, fill("cap_red")); cv.drawPath(d, stroke("line", 2.4))
    cv.drawPath(K.rrect(-40, -6, 30, 8, 4), fill(K.shade("cap_red", -0.15)))


def jar_small(cv, p):
    j = K.rrect(-16, -40, 32, 46, 8)
    cv.drawPath(j, fill("violet", 0.35)); cv.drawPath(j, stroke("line", 2.4))
    cv.drawRect(skia.Rect.MakeXYWH(-18, -46, 36, 8), fill("brass"))


def specs(cv, p):
    for dx in (-12, 12):
        cv.drawOval(skia.Rect.MakeLTRB(dx - 10, -8, dx + 10, 8), stroke("#9aa1ad", 2.4))
    cv.drawLine(-2, -2, 2, -2, stroke("#9aa1ad", 2))


def glove(cv, p):
    cv.drawPath(ellipse(0, 2, 14, 15), fill("#5b6b8c")); cv.drawPath(ellipse(0, 2, 14, 15), stroke("line", 2.4))


def crystal_hand(cv, p, amount=1.0):
    """Overlay for Kabir's sugar-crystal hand (amount 0..1)."""
    pts = [(-11, -6), (-4, -14), (6, -12), (12, -2), (8, 10), (-6, 12), (-12, 4)]
    cv.drawPath(K.poly(pts), fill("#e9f6ff", 0.8 * amount))
    for i in range(len(pts)):
        cv.drawLine(0, 0, *pts[i], stroke("#ffffff", 1.4, 0.8 * amount))
    cv.drawPath(K.poly(pts), stroke("#9fc7e8", 2, amount))


PROPS = {"bottle": bottle, "torch": torch, "book": book, "laddoo": laddoo, "toffee": toffee, "kulfi": kulfi,
         "lota": lota, "slippers": slippers, "fan": fan, "cap": cap, "jar": jar_small, "specs": specs,
         "glove": glove, "crystal": crystal_hand}
