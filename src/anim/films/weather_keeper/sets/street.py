"""The school road on a hot, bright day (coda).

draw_street(cv, t, weather='heat', scroll=0.0, kids=True, cam=None)
  A side view: a boundary wall with a painted band, a green iron school gate, a big gulmohar tree with flat
  red flower clusters, a dusty road, power lines, a couple of small distant kids walking with bags.
  scroll (px) slides the background slowly for a tracking shot (seamless repeats every 2400 px).
Anchors: WALK_Y = 930 (Ishaan's feet line, s≈1.6); WALK_LINE = ((260, 930), (1660, 930));
  GATE_X = 1250 (gate centre at scroll 0).
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF

WALK_Y = 930
WALK_LINE = ((260, 930), (1660, 930))
GATE_X = 1250
TILE = 2400


def _strip(weather):
    p = C.pal(weather)

    def draw(c):
        # boundary wall
        c.drawRect(skia.Rect.MakeLTRB(0, 520, TILE, 860), fill("#efe2c4"))
        c.drawRect(skia.Rect.MakeLTRB(0, 760, TILE, 820), fill("#d77b6a"))
        c.drawRect(skia.Rect.MakeLTRB(0, 500, TILE, 524), fill("#e2d2ae"))
        c.drawLine(0, 524, TILE, 524, stroke(p["line"], 2.4))
        for x in range(0, TILE, 240):
            c.drawRect(skia.Rect.MakeXYWH(x, 500, 30, 360), fill("#e6d6b4"))
            c.drawLine(x, 500, x, 860, stroke(p["line"], 1.6, 0.6))
        # gate
        gx = GATE_X
        c.drawRect(skia.Rect.MakeXYWH(gx - 220, 440, 50, 420), fill("#e2d2ae"))
        c.drawRect(skia.Rect.MakeXYWH(gx + 170, 440, 50, 420), fill("#e2d2ae"))
        c.drawRect(skia.Rect.MakeXYWH(gx - 170, 540, 340, 320), fill("#a8b8a0"))
        for k in range(13):
            c.drawLine(gx - 160 + k * 26, 540, gx - 160 + k * 26, 860, stroke("#2f7a4a", 7))
        c.drawLine(gx - 170, 600, gx + 170, 600, stroke("#2f7a4a", 7))
        c.drawLine(gx - 170, 800, gx + 170, 800, stroke("#2f7a4a", 7))
        c.drawRect(skia.Rect.MakeXYWH(gx - 220, 440, 440, 420), stroke(p["line"], 2.6))
        # school building beyond the wall
        C.flat_building(c, gx - 360, 520, 720, 220, "#f2d6a2", "#c98a5a", seed=3, floors=2, line=p["line"])
        # gulmohar tree
        tx = 520
        c.drawPath(poly([(tx - 26, 860), (tx + 26, 860), (tx + 14, 420), (tx - 14, 420)]), fill("#6a4a30"))
        c.drawLine(tx, 520, tx - 150, 380, stroke("#6a4a30", 18))
        c.drawLine(tx, 500, tx + 170, 360, stroke("#6a4a30", 16))
        r = K.rng(4)
        for k in range(26):
            cx, cy = tx + r.uniform(-330, 330), 300 + r.uniform(-140, 120)
            rr = r.uniform(50, 90)
            c.drawCircle(cx + 8, cy + 10, rr, fill("#3f7a3a"))
            c.drawCircle(cx, cy, rr, fill("#5a9a48"))
        for k in range(60):
            cx, cy = tx + r.uniform(-340, 340), 300 + r.uniform(-150, 140)
            c.drawCircle(cx, cy, r.uniform(10, 20), fill("#e8442e"))
            c.drawCircle(cx - 3, cy - 3, 5, fill("#ff8a5a"))
        # power pole + lines
        c.drawRect(skia.Rect.MakeXYWH(1900, 200, 18, 660), fill("#8a8a90"))
        for k in range(3):
            C.wire(c, 0, 230 + k * 20, TILE, 250 + k * 20, 60, p["line"], 2)
    return C.cached(("street_strip", weather), draw, TILE, H)


def draw_street(cv, t, weather="heat", scroll=0.0, kids=True, cam=None):
    p = C.pal(weather)
    with C.apply_cam(cv, cam):
        C.sky(cv, weather, W, H, H)
        if weather == "heat":
            cv.drawCircle(1600, 140, 70, fill("#fffdf6"))
            cv.drawCircle(1600, 140, 140, fill("#ffffff", 0.25))
        strip = _strip(weather)
        off = -(scroll % TILE)
        for k in range(2):
            C.blit(cv, strip, off + k * TILE, 0)
        # road
        cv.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), fill("#d9b77e"))
        cv.drawRect(skia.Rect.MakeLTRB(0, 860, W, 880), fill("#c9a36a"))
        r = K.rng(2)
        for i in range(20):
            x = (r.uniform(0, TILE) - scroll) % TILE
            if x < W:
                cv.drawPath(ellipse(x, r.uniform(900, H), r.uniform(20, 60), 6), fill("#c9a36a", 0.7))
        if kids:
            from .ground import draw_player
            for i, (x0, col) in enumerate(((1500, "#6f9ac0"), (1640, "#e8a3a0"), (300, "#f2e2a8"))):
                x = (x0 - scroll * 0.5 + t * 30) % (W + 200) - 100
                draw_player(cv, x, 860, 1.6, t, run=0.4, col=col)
                cv.drawPath(rrect(x - 12, 860 - 50, 24, 22, 4), fill("#5a6aa8"))   # school bag
        WF.heat_shimmer(cv, t, (0, 500, W, 900), 0.6)
