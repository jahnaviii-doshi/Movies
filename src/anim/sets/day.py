"""Daytime vignettes for the montage of kindnesses (harsh summer light, dusty ochre + whitewash).

draw_ironing_cart(cv, t, steam=1.0)
  Sun-blasted gali corner with the ironing-wala's cart: stacks of folded clothes, a heavy charcoal
  iron, a tarp shade, steam puffs (live, scaled by `steam`). Left third left clear for Meher.
  MEHER_IRON = (x, y, s) feet position/scale for Meher arriving with laundry.
  HAND_ANCHOR = (x, y) where the ironing-wala's hand reaches in from frame right (he stays off-screen).
  DROP_ANCHOR = (x, y) top of the clothes stack (where Meher sets her pile).

draw_balcony(cv, t, lift=0.0)
  Neighbour's balcony seen from inside: carved railing, the gali's opposite houses beyond in harsh
  light, a row of marigolds in clay pots on a ledge. lift 0..1: wilted/dull -> upright/bright.
  POUR_ANCHOR = (x, y) soil of the first pot (where Meher's lota pours); POTS = list of pot centres;
  MEHER_ANCHOR = (x, y, s) where Meher stands (left, facing right).

draw_room(cv, t, fan=0.0)
  Nani's house interior, hot afternoon: lime-washed walls, shuttered window throwing light stripes,
  striped floor durrie, round bolsters, steel almirah, ceiling fan (still; fan=speed in rev/s).
  SIT_ANCHOR = (x, y, s) origin for Meher sitting on the durrie (legs='sit', facing right) with the
  toddler (place the toddler's head on her lap ~ +70*s to her right).
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import W, H, fill, stroke, smooth_path, poly, ellipse, lerp, clamp
from . import town as T

LINE = "#3a2418"
MEHER_IRON = (430, 960, 1.45)
HAND_ANCHOR = (1790, 600)
DROP_ANCHOR = (1260, 560)
POTS = [(1010 + i * 170, 820) for i in range(5)]
POUR_ANCHOR = (POTS[0][0], POTS[0][1] - 66)
MEHER_ANCHOR = (620, 960, 1.45)
SIT_ANCHOR = (700, 905, 1.3)


def _sun_wall(cv, x0, y0, x1, y1, col, rng, bricks=3):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), K.lin((0, y0), (0, y1), [K.shade(col, 0.1), col, K.shade(col, -0.06)]))
    for _ in range(int((x1 - x0) * (y1 - y0) / 60000)):
        cv.drawOval(skia.Rect.MakeXYWH(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(30, 90), rng.uniform(8, 22)),
                    fill(K.shade(col, -0.1), 0.35))
    for _ in range(bricks):
        px, py = rng.uniform(x0 + 20, x1 - 80), rng.uniform(y0 + 20, y1 - 40)
        cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px, py, 70, 34), 12, 12), doAntiAlias=True)
        for r_ in range(6):
            for c_ in range(7):
                cv.drawRect(skia.Rect.MakeXYWH(px + c_ * 12 - (r_ % 2) * 6, py + r_ * 7, 10, 5), fill("brick", 0.8))
        cv.restore()


# ------------------------------------------------------------------ ironing cart
@lru_cache(maxsize=2)
def _iron_static():
    rng = K.rng(91)

    def paint(cv):
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("day_sky"))
        # back wall of the gali (whitewash) with a blue door and a window
        _sun_wall(cv, -20, -20, W + 20, 780, "whitewash", rng, bricks=4)
        cv.drawRect(skia.Rect.MakeLTRB(-20, 700, W + 20, 790), fill("#d9c7a6"))      # dado band
        door = T.window_path(150, 360, 200, 420)
        cv.drawPath(door, fill("#3d78b8")); cv.drawPath(door, stroke(LINE, 3))
        cv.drawLine(250, 420, 250, 780, stroke(LINE, 2))
        for k in range(4):
            cv.drawCircle(205 + (k % 2) * 90, 520 + (k // 2) * 120, 5, fill("brass"))
        T.arched_window(cv, 820, 180, 110, 210, frame=LINE, lw=3)
        cv.drawRect(skia.Rect.MakeLTRB(780, 160, 815, 400), fill("#5f8fb7")); cv.drawRect(skia.Rect.MakeLTRB(935, 160, 970, 400), fill("#5f8fb7"))
        # harsh cast shadow from a balcony above (diagonal)
        cv.drawPath(poly([(-20, -20), (1300, -20), (900, 260), (-20, 520)]), fill("#7a5a6a", 0.22))
        # ground
        cv.drawRect(skia.Rect.MakeLTRB(-20, 780, W + 20, H + 20), K.lin((0, 780), (0, H), ["#d8b98a", "#e6c99a", "#c9a676"]))
        for _ in range(40):
            cv.drawCircle(rng.uniform(0, W), rng.uniform(800, H), rng.uniform(2, 5), fill("#b8955f", 0.5))
        cv.drawLine(-20, 780, W + 20, 780, stroke(LINE, 2))
        # the cart
        cx, cy = 1260, 880
        cv.drawOval(skia.Rect.MakeLTRB(cx - 420, cy + 50, cx + 420, cy + 100), fill("#5a3a2a", 0.3))
        for wx in (cx - 300, cx + 300):
            cv.drawCircle(wx, cy + 40, 48, fill("#4a3a30")); cv.drawCircle(wx, cy + 40, 48, stroke(LINE, 3))
            cv.drawCircle(wx, cy + 40, 12, fill("#9aa1ad"))
            for k in range(6):
                a = k * math.pi / 3
                cv.drawLine(wx, cy + 40, wx + math.cos(a) * 40, cy + 40 + math.sin(a) * 40, stroke("#8a6a50", 4))
        body = skia.Rect.MakeLTRB(cx - 380, cy - 230, cx + 380, cy - 20)
        cv.drawRect(body, K.lin((0, cy - 230), (0, cy - 20), ["#a86a3a", "#8a5530"]))
        for i in range(8):
            cv.drawLine(cx - 380 + i * 95, cy - 220, cx - 380 + i * 95, cy - 20, stroke("#6e4226", 2))
        cv.drawRect(body, stroke(LINE, 3))
        # ironing cloth on top
        top = poly([(cx - 400, cy - 230), (cx + 400, cy - 230), (cx + 380, cy - 270), (cx - 380, cy - 270)])
        cv.drawPath(top, fill("#e9e2d2")); cv.drawPath(top, stroke(LINE, 2.6))
        cv.drawPath(poly([(cx - 400, cy - 230), (cx + 400, cy - 230), (cx + 400, cy - 190), (cx - 400, cy - 190)]),
                    fill("#d8333d"))
        for i in range(16):
            cv.drawLine(cx - 400 + i * 50, cy - 230, cx - 390 + i * 50, cy - 190, stroke("#f2c94c", 3))
        # folded clothes stacks
        cols = ["#3a6fd8", "#f5f0e6", "#7a9a6a", "#e37f6a", "#f2c94c", "#8e6cc9", "#d8333d", "#5f8fb7"]
        for sx in (cx - 300, cx + 120, cx + 280):
            y = cy - 270
            for k in range(rng.randint(4, 7)):
                h = rng.uniform(14, 22)
                r_ = K.rrect(sx - 70 + rng.uniform(-6, 6), y - h, 140, h, 5)
                cv.drawPath(r_, fill(rng.choice(cols))); cv.drawPath(r_, stroke(LINE, 1.8))
                y -= h
        # charcoal iron
        ix, iy = cx - 80, cy - 270
        iron = smooth_path([(ix - 80, iy), (ix + 70, iy), (ix + 90, iy - 30), (ix - 60, iy - 50)], tension=0.3)
        cv.drawPath(iron, K.lin((0, iy - 50), (0, iy), ["#4a4f5c", "#22242c"])); cv.drawPath(iron, stroke(LINE, 2.6))
        for k in range(5):
            cv.drawCircle(ix - 50 + k * 26, iy - 22, 5, fill("#ff7a3a", 0.85))      # glowing coals through vents
        cv.drawLine(ix - 40, iy - 50, ix - 30, iy - 96, stroke("#22242c", 6))
        cv.drawLine(ix + 50, iy - 40, ix + 40, iy - 96, stroke("#22242c", 6))
        cv.drawPath(K.rrect(ix - 46, iy - 110, 100, 22, 10), fill("#8a5530")); cv.drawPath(K.rrect(ix - 46, iy - 110, 100, 22, 10), stroke(LINE, 2.4))
        # tarp shade on bamboo poles
        for px in (cx - 360, cx + 360):
            cv.drawLine(px, cy - 230, px, 300, stroke("#c9a46a", 8))
            cv.drawLine(px, cy - 230, px, 300, stroke(LINE, 1.6, 0.5))
        tarp = smooth_path([(cx - 420, 300), (cx, 270), (cx + 420, 300), (cx + 400, 340), (cx, 320), (cx - 400, 340)], tension=0.4)
        cv.drawPath(tarp, fill("#2f7d6a")); cv.drawPath(tarp, stroke(LINE, 2.6))
        for i in range(9):
            cv.drawPath(poly([(cx - 400 + i * 100, 336), (cx - 350 + i * 100, 336), (cx - 375 + i * 100, 360)]), fill("#f2c94c"))
        # tarp shadow on the cart
        cv.drawPath(poly([(cx - 380, cy - 270), (cx + 380, cy - 270), (cx + 300, cy - 200), (cx - 460, cy - 200)]),
                    fill("#3a2a3a", 0.12))
        # a sleeping cat under the cart, flower pot, a broom
        cv.drawPath(ellipse(cx - 90, cy + 70, 46, 18), fill("#2a2a30")); cv.drawCircle(cx - 132, cy + 60, 16, fill("#2a2a30"))
        cv.drawPath(poly([(cx - 146, cy + 48), (cx - 140, cy + 34), (cx - 132, cy + 46)]), fill("#2a2a30"))
        cv.drawLine(1820, 780, 1880, 1000, stroke("#c9a46a", 6))
        cv.drawPath(poly([(1860, 960), (1900, 960), (1920, 1060), (1840, 1060)]), fill("#d8b06a"))
        # harsh-sun bloom
        cv.drawRect(skia.Rect.MakeWH(W, H), K.rad_a((1700, -100), 1400, [("#fff3d0", 0.35), ("#fff3d0", 0)]))
    return K.render_to_image(W, H, paint)


def draw_ironing_cart(cv, t, steam=1.0):
    cv.drawImage(_iron_static(), 0, 0)
    ix, iy = 1260 - 80, 880 - 270 - 110
    for k in range(7):
        ph = (t * 0.45 + k / 7) % 1.0
        x = ix + math.sin(ph * 6 + k) * 24 + ph * 40
        y = iy - ph * 260
        r = 18 + ph * 46
        a = steam * 0.4 * math.sin(ph * math.pi)
        cv.drawCircle(x, y, r, K.rad_a((x, y), r, [("#ffffff", a), ("#ffffff", 0)]))
    # heat shimmer over the ground
    for i in range(4):
        y0 = 830 + i * 50
        p = skia.Path(); p.moveTo(0, y0)
        for xx in range(0, W + 60, 60):
            p.lineTo(xx, y0 + math.sin(xx * 0.015 + t * 2.4 + i) * 4)
        cv.drawPath(p, stroke("#fff3d6", 6, 0.06))


# ------------------------------------------------------------------ balcony
@lru_cache(maxsize=2)
def _balcony_static():
    rng = K.rng(92)

    def paint(cv):
        # opposite houses across the gali, in harsh light
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("day_sky"))
        x = -40
        T.clouds(cv, rng, W, 60, 200, "#ffffff", a=0.35, n=4)
        while x < W:
            w = rng.uniform(260, 420)
            T.haveli(cv, x, 700, w, rng.uniform(380, 560), rng, detail=1.0, lw=2.4,
                     tank=rng.uniform(0.2, 0.8) if rng.random() < 0.6 else None)
            x += w + 6
        cv.drawRect(skia.Rect.MakeWH(W, 700), fill("#fff6e0", 0.25))     # bleaching sun
        # wires across
        for i in range(3):
            T.wire(cv, -10, 120 + i * 40, W + 10, 160 + i * 30, sag=30, w=2)
        # our balcony: side walls framing the view, floor, ledge, carved railing
        cv.drawPath(poly([(-20, -20), (140, -20), (200, 980), (-20, H + 20)]), K.lin((0, 0), (200, 0), ["#cfae86", "#e2c79e"]))
        cv.drawPath(poly([(W + 20, -20), (W - 140, -20), (W - 200, 980), (W + 20, H + 20)]),
                    K.lin((W, 0), (W - 200, 0), ["#b8946c", "#d6b48a"]))
        cv.drawRect(skia.Rect.MakeLTRB(-20, -20, W + 20, 60), fill("#b8946c"))   # lintel shade
        cv.drawRect(skia.Rect.MakeLTRB(-20, -20, W + 20, 60), stroke(LINE, 2))
        # railing (carved wood balusters) below the view
        rail_top, rail_bot = 640, 860
        cv.drawRect(skia.Rect.MakeLTRB(140, rail_top - 18, W - 140, rail_top + 4), fill("#8a5530"))
        cv.drawRect(skia.Rect.MakeLTRB(140, rail_top - 18, W - 140, rail_top + 4), stroke(LINE, 2.4))
        for i in range(30):
            bx = 170 + i * 55
            if bx > W - 160:
                break
            bal = smooth_path([(bx - 8, rail_top + 4), (bx + 8, rail_top + 4), (bx + 12, rail_top + 50), (bx + 7, rail_top + 100),
                               (bx + 12, rail_top + 150), (bx + 8, rail_bot), (bx - 8, rail_bot), (bx - 12, rail_top + 150),
                               (bx - 7, rail_top + 100), (bx - 12, rail_top + 50)], tension=0.4)
            cv.drawPath(bal, K.lin((bx - 12, 0), (bx + 12, 0), ["#b07a46", "#8a5530", "#6e4226"]))
            cv.drawPath(bal, stroke(LINE, 1.8))
        # ledge / floor
        cv.drawRect(skia.Rect.MakeLTRB(-20, rail_bot, W + 20, H + 20), K.lin((0, rail_bot), (0, H), ["#e6d3b0", "#d2b98e"]))
        for i in range(-12, 13):
            cv.drawLine(960 + i * 40, rail_bot, 960 + i * 150, H, stroke("#bfa27a", 1.6, 0.7))
        cv.drawLine(-20, rail_bot, W + 20, rail_bot, stroke(LINE, 2.4))
        # cast shadow of the railing on the floor
        cv.drawRect(skia.Rect.MakeLTRB(-20, rail_bot, W + 20, rail_bot + 60), K.lin_a((0, rail_bot), (0, rail_bot + 60),
                    [("#3a2a3a", 0.25), ("#3a2a3a", 0)]))
        # a hanging bird cage, empty, for texture
        cv.drawLine(1700, 60, 1700, 150, stroke(LINE, 2))
        cv.drawPath(T.window_path(1660, 150, 80, 110), stroke("#b08a40", 2.4))
        for k in range(5):
            cv.drawLine(1668 + k * 16, 170, 1668 + k * 16, 260, stroke("#b08a40", 1.4))
        cv.drawRect(skia.Rect.MakeWH(W, H), K.rad_a((1500, -200), 1500, [("#fff3d0", 0.3), ("#fff3d0", 0)]))
    return K.render_to_image(W, H, paint)


def _marigold_pot(cv, x, y, lift, t, i):
    # clay pot
    pot = poly([(x - 52, y - 70), (x + 52, y - 70), (x + 38, y + 20), (x - 38, y + 20)])
    cv.drawPath(pot, K.lin((x - 52, 0), (x + 52, 0), ["#c4724a", "#b05a36", "#8a4228"])); cv.drawPath(pot, stroke(LINE, 2.4))
    cv.drawPath(K.rrect(x - 58, y - 84, 116, 18, 6), fill("#c4724a")); cv.drawPath(K.rrect(x - 58, y - 84, 116, 18, 6), stroke(LINE, 2.2))
    cv.drawPath(ellipse(x, y - 76, 50, 7), fill(K.mix("#8a6a4a", "#4e3a2a", lift)))   # soil (darker when watered)
    rng = K.rng(300 + i)
    for k in range(4):
        base_a = -math.pi / 2 + (k - 1.5) * 0.35
        droop = (1 - lift) * (0.9 + rng.uniform(-0.2, 0.3)) * (1 if k > 1.5 else -1)
        sway = math.sin(t * 1.5 + k + i) * 0.04 * lift
        L = 120 + rng.uniform(-20, 20)
        pts = []
        for j in range(5):
            u = j / 4
            a = base_a + droop * u * u * 1.6 + sway
            if j == 0:
                px, py = x + (k - 1.5) * 10, y - 78
            else:
                px, py = pts[-1][0] + math.cos(a) * L / 4, pts[-1][1] + math.sin(a) * L / 4
            pts.append((px, py))
        stem = K.mix("#8a8a4a", "#3f7a3a", lift)
        cv.drawPath(smooth_path(pts, close=False), stroke(stem, 4))
        for j in (1, 2, 3):
            lx, ly = pts[j]
            cv.drawPath(ellipse(lx + 10, ly, 12, 5), fill(K.mix("#9a9a5a", "#4f8a43", lift)))
        fx, fy = pts[-1]
        petal = K.mix("#a8743a", "#ff9a1f", lift)
        inner = K.mix("#8a5a2a", "#ffbf2f", lift)
        r = lerp(13, 20, lift)
        for p in range(10):
            a = p * math.pi / 5
            cv.drawCircle(fx + math.cos(a) * r * 0.6, fy + math.sin(a) * r * 0.6, r * 0.55, fill(petal))
        cv.drawCircle(fx, fy, r * 0.6, fill(inner))
        cv.drawCircle(fx, fy, r * 1.05, stroke(LINE, 1.6, 0.6))


def draw_balcony(cv, t, lift=0.0):
    cv.drawImage(_balcony_static(), 0, 0)
    lift = clamp(lift)
    for i, (x, y) in enumerate(POTS):
        li = clamp(lift * 1.6 - i * 0.15)   # perk up one after another
        _marigold_pot(cv, x, y, li, t, i)
        if li > 0.05:
            cv.drawCircle(x, y - 120, 140, K.rad_a((x, y - 120), 140, [("#ffcf5a", 0.12 * li), ("#ffcf5a", 0)]))


# ------------------------------------------------------------------ room
@lru_cache(maxsize=2)
def _room_static():
    rng = K.rng(93)

    def paint(cv):
        # lime-washed walls (pale aqua) + floor
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, 760), K.lin((0, 0), (0, 760), ["#bfe0d6", "#a9d0c4"]))
        for _ in range(16):
            cv.drawOval(skia.Rect.MakeXYWH(rng.uniform(0, W), rng.uniform(0, 700), rng.uniform(40, 140), rng.uniform(14, 34)),
                        fill("#94bdb0", 0.35))
        cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, 760), fill("#7fb0a2"))       # dado
        cv.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), K.lin((0, 760), (0, H), ["#c9a77a", "#b8915f"]))
        cv.drawLine(0, 760, W, 760, stroke(LINE, 2))
        # shuttered window (right) with bright slits
        wx, wy = 1300, 160
        cv.drawRect(skia.Rect.MakeXYWH(wx - 20, wy - 20, 360, 440), fill("#e9dcc0")); cv.drawRect(skia.Rect.MakeXYWH(wx - 20, wy - 20, 360, 440), stroke(LINE, 2.4))
        for side in (0, 1):
            sx = wx + side * 160
            cv.drawRect(skia.Rect.MakeXYWH(sx, wy, 160, 400), fill("#2f7d6a"))
            for k in range(14):
                yy = wy + 14 + k * 27
                cv.drawRect(skia.Rect.MakeXYWH(sx + 10, yy, 140, 12), fill("#fff3c8"))
                cv.drawLine(sx + 10, yy + 12, sx + 150, yy + 12, stroke("#1f5a4a", 3))
            cv.drawRect(skia.Rect.MakeXYWH(sx, wy, 160, 400), stroke(LINE, 2.4))
        # steel almirah (left)
        ax = 120
        al = skia.Rect.MakeXYWH(ax, 220, 300, 560)
        cv.drawRect(al, K.lin((ax, 0), (ax + 300, 0), ["#c9ced8", "#e9edf3", "#a9b0bd"]))
        cv.drawLine(ax + 150, 230, ax + 150, 770, stroke("#7d8594", 2.4))
        cv.drawRect(skia.Rect.MakeXYWH(ax + 170, 260, 110, 300), fill("#d9e6f2"))          # mirror
        cv.drawLine(ax + 190, 280, ax + 230, 330, stroke("#ffffff", 4, 0.7))
        cv.drawRect(skia.Rect.MakeXYWH(ax + 170, 260, 110, 300), stroke("#7d8594", 2))
        cv.drawPath(K.rrect(ax + 120, 470, 14, 50, 5), fill("#7d8594")); cv.drawPath(K.rrect(ax + 166, 470, 14, 50, 5), fill("#7d8594"))
        cv.drawRect(al, stroke(LINE, 2.6))
        cv.drawRect(skia.Rect.MakeXYWH(ax + 20, 180, 120, 40), fill("#d8333d")); cv.drawRect(skia.Rect.MakeXYWH(ax + 20, 180, 120, 40), stroke(LINE, 2))   # suitcase on top
        # wall calendar (picture only) + framed photo
        cv.drawRect(skia.Rect.MakeXYWH(620, 180, 150, 210), fill("#f6efe0")); cv.drawRect(skia.Rect.MakeXYWH(620, 180, 150, 210), stroke(LINE, 2))
        cv.drawRect(skia.Rect.MakeXYWH(632, 192, 126, 110), fill("#6f9ad0"))
        cv.drawCircle(695, 262, 30, fill("#f2c94c"))
        for k in range(4):
            cv.drawLine(635, 320 + k * 16, 755, 320 + k * 16, stroke("#c9b48c", 2))
        cv.drawRect(skia.Rect.MakeXYWH(900, 220, 120, 150), fill("#5a3a2a"))
        cv.drawRect(skia.Rect.MakeXYWH(912, 232, 96, 126), fill("#d9c49a"))
        cv.drawCircle(960, 280, 20, fill("#8a6a4a")); cv.drawPath(ellipse(960, 344, 34, 22), fill("#8a6a4a"))
        cv.drawRect(skia.Rect.MakeXYWH(900, 220, 120, 150), stroke(LINE, 2.4))
        cv.drawPath(smooth_path([(915, 225), (960, 205), (1005, 225)], close=False), stroke("#e8742a", 3))    # marigold garland
        # durrie (striped rug) in perspective
        rug = poly([(300, 840), (1600, 840), (1820, H + 20), (100, H + 20)])
        cv.drawPath(rug, fill("#c9563a"))
        cv.save(); cv.clipPath(rug, doAntiAlias=True)
        cols = ["#c9563a", "#2f5f9a", "#f2c94c", "#2f5f9a", "#c9563a", "#f5efe0"]
        y = 840
        k = 0
        while y < H:
            h = 14 + (y - 840) * 0.12
            cv.drawRect(skia.Rect.MakeLTRB(0, y, W, y + h), fill(cols[k % len(cols)]))
            y += h; k += 1
        cv.restore()
        cv.drawPath(rug, stroke(LINE, 2.4))
        # bolsters (gol takiya)
        for bx, by in ((360, 830), (1500, 830)):
            cv.drawPath(K.rrect(bx - 110, by - 50, 220, 60, 30), K.lin((0, by - 50), (0, by + 10), ["#f2d27a", "#c99a3a"]))
            for k in range(4):
                cv.drawLine(bx - 80 + k * 50, by - 48, bx - 80 + k * 50, by + 8, stroke("#a87a2a", 2))
            cv.drawPath(K.rrect(bx - 110, by - 50, 220, 60, 30), stroke(LINE, 2.4))
        # a small stack of picture books + steel water tumbler
        for k, c in enumerate(("#3a6fd8", "#d8333d", "#7a9a6a")):
            cv.drawPath(K.rrect(1180, 900 - k * 18, 120, 18, 3), fill(c)); cv.drawPath(K.rrect(1180, 900 - k * 18, 120, 18, 3), stroke(LINE, 1.8))
        cv.drawPath(poly([(1360, 880), (1400, 880), (1394, 930), (1366, 930)]), K.lin((1360, 0), (1400, 0), ["#dfe3ea", "#9aa1ad"]))
        # warm afternoon haze
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#ffcf8a", 0.06))
    return K.render_to_image(W, H, paint)


def draw_room(cv, t, fan=0.0):
    cv.drawImage(_room_static(), 0, 0)
    # light stripes from the shutters falling across wall-floor-rug (additive, slow dust drift)
    stripes = skia.Paint(); stripes.setBlendMode(skia.BlendMode.kPlus)
    for k in range(10):
        y0 = 190 + k * 37
        p = poly([(1290, y0), (1290, y0 + 10), (300 - k * 10, y0 + 640 + k * 26), (300 - k * 10, y0 + 610 + k * 26)])
        cv.drawPath(p, K.lin_a((1290, 0), (300, 0), [("#fff1c8", 0.22), ("#fff1c8", 0.05)]))
    rng = K.rng(95)
    for i in range(30):
        x = rng.uniform(500, 1280) + math.sin(t * 0.3 + i) * 20
        y = rng.uniform(300, 800) + math.cos(t * 0.25 + i) * 14
        cv.drawCircle(x, y, rng.uniform(1.2, 2.4), fill("#fff6d8", 0.4 + 0.3 * math.sin(t + i)))
    # ceiling fan
    fx, fy = 960, 70
    cv.drawLine(fx, -10, fx, fy, stroke("#6a6a76", 6))
    a0 = t * fan * 2 * math.pi
    for k in range(3):
        a = a0 + k * 2 * math.pi / 3
        cv.save(); cv.translate(fx, fy); cv.scale(1, 0.18); cv.rotate(math.degrees(a))
        cv.drawPath(K.rrect(10, -18, 260, 36, 16), fill("#8a8f9a")); cv.drawPath(K.rrect(10, -18, 260, 36, 16), stroke(LINE, 3))
        cv.restore()
    cv.drawPath(ellipse(fx, fy, 40, 16), fill("#5a5f6a")); cv.drawPath(ellipse(fx, fy, 40, 16), stroke(LINE, 2.4))
