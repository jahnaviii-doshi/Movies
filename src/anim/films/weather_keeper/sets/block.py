"""Block C, Sector 9: exterior + courtyard.

draw_block(cv, t, weather='heat', fans=1.0, wind=0.0, tear=0.0, cheer=0.0, rain=0.0, tanker_x=None,
           tanker_gush=0.0, coda=False, view='wide')
    view 'wide': the whole five-storey block, roof forest of black tanks + crooked antennas on top,
        courtyard at the bottom; neighbouring blocks at the frame edges.
    view 'balconies': closer on the upper three floors (for laundry tearing / rain cheering).
    view 'top': Meghnath's top-floor balcony medium for the coda; draw the character, THEN
        draw_top_rail(cv, t, weather, coda=True) for the railing + chilli pot in front.
    fans 0..1 ceiling fans spinning in the windows (power cut = drive to 0).
    wind 0..1 laundry flapping; tear 0..1 laundry rips off and flies away (dust storm).
    cheer 0..1 balcony silhouettes lean out, faces up, hands out (rain finale); NO full crowds.
    rain 0..1 rain over the block (use weather='monsoon'/'monsoon_night'/'dawn_wet').
    tanker_x: screen x of the water tanker's front (None = no tanker); tanker_gush 0..1 water from its tap.
    coda: Meghnath's top-floor balcony shows a pot of green chillies.

Anchors (view 'wide'): GROUND_Y = 990 (courtyard floor, kids s≈0.55), BALCONIES = list of dicts
    {x, y (rail top), floor 0..4, bay 0..3} for placing silhouettes/props; MEGHNATH_BALCONY = (x, y);
    view 'top': TOP_ANCHOR = (x_floor, y_floor, s) for Meghnath standing on his balcony (s≈1.6),
    TOP_POT = (x, y) the chilli pot.
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF

BX0, BX1 = 300, 1620          # facade left/right (wide)
ROOF_Y = 250
GROUND_Y = 990
FLOORS = 5
BAYS = 4
FLOOR_H = (GROUND_Y - ROOF_Y) / FLOORS
BAY_W = (BX1 - BX0) / BAYS

BALCONIES = []
for f in range(FLOORS):
    for b in range(BAYS):
        BALCONIES.append(dict(x=BX0 + (b + 0.5) * BAY_W, y=ROOF_Y + (f + 1) * FLOOR_H - 62, floor=FLOORS - 1 - f,
                              bay=b))
MEGHNATH_BALCONY = (BX0 + 3.5 * BAY_W, ROOF_Y + FLOOR_H - 62)
TOP_ANCHOR = (1180, 1010, 1.75)   # feet hidden behind the rail
TOP_POT = (760, 862)

_LAUNDRY_COLS = ["#e8a3a0", "#d9895d", "#6f9ac0", "#f2e2a8", "#9bc59a", "#c99ad0", "#f4f0e6"]


def _bay(c, p, x, y, w, h, seed, top_floor):
    """One flat's frontage: balcony slab + railing, window, AC unit, peeling paint."""
    r = K.rng(seed)
    # recess / back wall of balcony
    c.drawRect(skia.Rect.MakeXYWH(x + 18, y + 18, w - 36, h - 50), fill(p["wall_shade"]))
    # window + door in the recess
    c.drawRect(skia.Rect.MakeXYWH(x + 40, y + 34, w * 0.36, h * 0.5), fill(p["window"]))
    c.drawRect(skia.Rect.MakeXYWH(x + 40, y + 34, w * 0.36, h * 0.5), stroke(p["line"], 2.2))
    c.drawRect(skia.Rect.MakeXYWH(x + w * 0.58, y + 30, w * 0.2, h * 0.72), fill(K.shade(p["window"], -0.15)))
    c.drawRect(skia.Rect.MakeXYWH(x + w * 0.58, y + 30, w * 0.2, h * 0.72), stroke(p["line"], 2.2))
    # balcony slab + parapet rail
    c.drawRect(skia.Rect.MakeXYWH(x + 6, y + h - 32, w - 12, 14), fill(p["wall"]))
    c.drawRect(skia.Rect.MakeXYWH(x + 6, y + h - 82, w - 12, 50), fill(K.shade(p["wall"], -0.04)))
    for k in range(int((w - 12) / 22)):
        c.drawLine(x + 16 + k * 22, y + h - 78, x + 16 + k * 22, y + h - 34, stroke(p["wall_dark"], 2.4))
    c.drawRect(skia.Rect.MakeXYWH(x + 6, y + h - 86, w - 12, 8), fill(p["wall"]))
    c.drawRect(skia.Rect.MakeXYWH(x + 6, y + h - 86, w - 12, 72), stroke(p["line"], 2.4))
    # peeling paint
    for i in range(r.randint(1, 3)):
        px, py = x + r.uniform(10, w - 10), y + r.uniform(4, h - 20)
        c.drawPath(ellipse(px, py, r.uniform(8, 22), r.uniform(5, 12)), fill(p["wall_dark"], 0.35))
    # stain streak from the AC drip
    c.drawRect(skia.Rect.MakeXYWH(x + w - 46, y + h - 18, 6, 26), fill(p["wall_dark"], 0.25))


def _static(weather):
    p = C.pal(weather)

    def draw(c):
        C.sky(c, weather, W, H, H)
        if weather == "heat":
            c.drawCircle(1700, 150, 70, fill("#fffdf6"))
            c.drawCircle(1700, 150, 130, fill("#ffffff", 0.25))
        if C.is_night(weather):
            K.stars(c, W, 500, 0.0, n=120, seed=3, alpha=0.6)
        # neighbouring blocks at the edges (flat, receding)
        C.flat_building(c, -60, GROUND_Y, 330, 820, p["mid"], K.shade(p["mid"], -0.15), seed=2, balcony=True,
                        shade=K.shade(p["mid"], -0.07), tanks=2, tank_col=p["tank"], ant_col=p["line"])
        C.flat_building(c, 1650, GROUND_Y, 340, 760, p["mid"], K.shade(p["mid"], -0.15), seed=5, balcony=True,
                        shade=K.shade(p["mid"], -0.07), tanks=1, tank_col=p["tank"], ant_col=p["line"])
        # roof forest: tanks + antennas (behind the parapet)
        r = K.rng(11)
        for i in range(9):
            x = BX0 + 60 + i * (BX1 - BX0 - 120) / 8 + r.uniform(-20, 20)
            C.water_tank(c, x, ROOF_Y + 6, r.uniform(0.75, 1.05), p)
        for i in range(6):
            C.antenna(c, BX0 + 100 + i * 230 + r.uniform(-40, 40), ROOF_Y, r.uniform(110, 170), 1.0, p, seed=i)
        # stair hut on the roof
        C.rect_line(c, BX0 + 80, ROOF_Y - 90, 170, 92, p["wall"], p["line"], 2.6)
        c.drawRect(skia.Rect.MakeXYWH(BX0 + 70, ROOF_Y - 98, 190, 12), fill(p["metal"]))
        # facade
        c.drawRect(skia.Rect.MakeLTRB(BX0, ROOF_Y, BX1, GROUND_Y), fill(p["wall"]))
        c.drawRect(skia.Rect.MakeLTRB(BX1 - 120, ROOF_Y, BX1, GROUND_Y), fill(p["wall_shade"], 0.6))
        for f in range(FLOORS):
            for b in range(BAYS):
                _bay(c, p, BX0 + b * BAY_W, ROOF_Y + f * FLOOR_H, BAY_W, FLOOR_H, f * 10 + b, f == 0)
        # floor bands
        for f in range(FLOORS + 1):
            c.drawRect(skia.Rect.MakeXYWH(BX0 - 8, ROOF_Y + f * FLOOR_H - 6, BX1 - BX0 + 16, 10), fill(p["wall"]))
            c.drawLine(BX0 - 8, ROOF_Y + f * FLOOR_H + 4, BX1 + 8, ROOF_Y + f * FLOOR_H + 4, stroke(p["line"], 2))
        # parapet + drainpipe
        c.drawRect(skia.Rect.MakeXYWH(BX0 - 10, ROOF_Y - 24, BX1 - BX0 + 20, 26), fill(p["near_lit"]))
        c.drawRect(skia.Rect.MakeXYWH(BX0 - 10, ROOF_Y - 24, BX1 - BX0 + 20, 26), stroke(p["line"], 2.6))
        c.drawRect(skia.Rect.MakeXYWH(BX0 + 10, ROOF_Y, 14, GROUND_Y - ROOF_Y), fill(p["metal"]))
        c.drawRect(skia.Rect.MakeLTRB(BX0, ROOF_Y - 24, BX1, GROUND_Y), stroke(p["line"], 3))
        # courtyard
        c.drawRect(skia.Rect.MakeLTRB(0, GROUND_Y, W, H), fill(p["ground"]))
        c.drawRect(skia.Rect.MakeLTRB(0, GROUND_Y, W, GROUND_Y + 10), fill(p["ground_shade"]))
        # entrance
        c.drawRect(skia.Rect.MakeXYWH(900, GROUND_Y - 120, 120, 120), fill(p["wall_dark"]))
        c.drawRect(skia.Rect.MakeXYWH(900, GROUND_Y - 120, 120, 120), stroke(p["line"], 2.6))
        # hard heat shadow diagonal
        if weather == "heat":
            c.drawPath(poly([(BX1 - 120, ROOF_Y), (BX1, ROOF_Y), (BX1 + 260, GROUND_Y), (BX1 + 140, GROUND_Y)]),
                       fill(p["wall_dark"], 0.25))
    return C.cached(("block", weather), draw)


def _tanker(cv, x, p, t, gush):
    y = GROUND_Y + 4
    C.rect_line(cv, x - 520, y - 150, 400, 130, "#4a6fa8", p["line"], 3)      # tank
    cv.drawPath(ellipse(x - 520, y - 85, 22, 65), fill("#3a5a8c"))
    cv.drawRect(skia.Rect.MakeXYWH(x - 500, y - 150, 360, 14), fill("#6d90c4"))
    C.rect_line(cv, x - 110, y - 170, 120, 150, "#d8c27a", p["line"], 3)      # cab
    C.rect_line(cv, x - 80, y - 150, 72, 54, "#9ec0d8", p["line"], 2.4)
    for wx in (x - 440, x - 230, x - 40):
        cv.drawCircle(wx, y - 14, 30, fill("#222"))
        cv.drawCircle(wx, y - 14, 12, fill("#888"))
    cv.drawLine(x - 300, y - 20, x - 300, y + 6, stroke(p["metal"], 6))
    if gush > 0:
        cv.drawPath(smooth_path([(x - 300, y + 4), (x - 290, y + 30 * gush), (x - 310, y + 60 * gush)], close=False),
                    stroke("#9fd0ea", 10 * gush, 0.8))
        cv.drawPath(ellipse(x - 300, y + 70, 60 * gush, 10 * gush), fill("#9fd0ea", 0.6))


def _silhouettes(cv, t, cheer, p, seed=4):
    """Hands, faces-up and dangling feet on some balconies (never a crowd)."""
    r = K.rng(seed)
    pick = [b for b in BALCONIES if r.random() < 0.45]
    skin = ["#c98a5e", "#b77b55", "#a8724e", "#d8a07a"]
    cloth = ["#e8a3a0", "#6f9ac0", "#f2e2a8", "#9bc59a", "#c99ad0"]
    for i, b in enumerate(pick):
        k = clamp(cheer * 1.6 - i * 0.04)
        if k <= 0:
            continue
        x, y = b["x"] + r.uniform(-60, 60), b["y"]
        kind = i % 3
        sk = skin[i % 4]
        cl = cloth[i % 5]
        if kind == 0:   # head tilted up + shoulders behind the rail
            hy = y - 18 * k
            cv.drawPath(ellipse(x, y + 4, 26, 14), fill(cl))
            cv.drawCircle(x, hy - 10, 16, fill(sk))
            cv.drawCircle(x, hy - 10, 16, stroke(p["line"], 2))
            cv.drawPath(smooth_path([(x - 6, hy - 6), (x, hy - 2), (x + 6, hy - 6)], close=False), stroke(p["line"], 2))
            cv.drawCircle(x, hy - 22, 9, fill("#2a1e22"))
        elif kind == 1:  # two hands reaching out, palms up
            for d in (-1, 1):
                ax = x + d * 18
                ang = math.sin(t * 4 + i) * 6
                cv.drawLine(ax, y + 6, ax + d * 16, y - 34 * k + ang, stroke(sk, 9))
                cv.drawCircle(ax + d * 16, y - 36 * k + ang, 7, fill(sk))
        else:   # feet dangling through the rail (a kid sitting)
            for d in (-1, 1):
                fx = x + d * 12
                sw = math.sin(t * 3 + d + i) * 8 * k
                cv.drawLine(fx, y + 44, fx + sw, y + 70 + 10 * k, stroke(cl, 9))
                cv.drawPath(ellipse(fx + sw + 3, y + 80 + 10 * k, 8, 5), fill(sk))


def draw_block(cv, t, weather="heat", fans=1.0, wind=0.0, tear=0.0, cheer=0.0, rain=0.0, tanker_x=None,
               tanker_gush=0.0, coda=False, view="wide"):
    p = C.pal(weather)
    if view == "top":
        return _draw_top(cv, t, weather, coda, rain)   # then call draw_top_rail() after the characters
    cv.save()
    if view == "balconies":
        cv.translate(W / 2, H / 2); cv.scale(1.9, 1.9); cv.translate(-960, -470)
    C.blit(cv, _static(weather))
    # fans in every window (live)
    for b in BALCONIES:
        x0 = b["x"] - BAY_W / 2 + 40
        y0 = b["y"] - FLOOR_H + 62 + 34
        C.ceiling_fan_window(cv, x0, y0, BAY_W * 0.36, FLOOR_H * 0.5, t, fans, p, seed=int(x0))
        # AC unit on every other bay
        if (b["floor"] + b["bay"]) % 2 == 0:
            C.ac_unit(cv, b["x"] + BAY_W / 2 - 86, b["y"] - 60, 0.85, p, t, drip=weather in ("heat", "evening"))
    # laundry on the balcony rails
    for i, b in enumerate(BALCONIES):
        if i % 3 == 1 or (i % 5 == 0):
            x0, x1 = b["x"] - BAY_W / 2 + 20, b["x"] + BAY_W / 2 - 20
            C.laundry_line(cv, x0, b["y"] - 6, x1, b["y"] - 6, t, i, _LAUNDRY_COLS, wind=wind, sag=4, s=0.75,
                           tear=tear, line_col=p["line"])
    if coda:
        mx, my = MEGHNATH_BALCONY
        _chilli_pot(cv, mx - 40, my - 4, 0.6, t, p)
    if cheer > 0:
        _silhouettes(cv, t, cheer, p)
    if tanker_x is not None:
        _tanker(cv, tanker_x, p, t, tanker_gush)
    cv.restore()
    if rain > 0:
        WF.rain(cv, t, rain, wind=0.15, splash_y=GROUND_Y + 30 if view == "wide" else None)


def _chilli_pot(cv, x, y, s, t, p):
    pot = poly([(x - 36 * s, y - 60 * s), (x + 36 * s, y - 60 * s), (x + 26 * s, y), (x - 26 * s, y)])
    cv.drawPath(pot, fill("#b06a48")); cv.drawPath(pot, stroke(p["line"], 2.4))
    for k in range(7):
        a = -60 + k * 20 + math.sin(t * 1.5 + k) * 3
        L = 70 * s
        ex = x + math.sin(math.radians(a)) * L
        ey = y - 60 * s - math.cos(math.radians(a)) * L
        cv.drawLine(x, y - 60 * s, ex, ey, stroke("#3f9a55", 4 * s))
        cv.drawPath(ellipse(ex, ey, 10 * s, 6 * s), fill("#4fae5c"))
        if k % 2 == 0:
            cv.drawPath(ellipse(ex + 4 * s, ey + 12 * s, 4 * s, 12 * s), fill("#3f9a55"))


def _draw_top(cv, t, weather, coda, rain):
    """Medium on Meghnath's top-floor balcony: railing at the bottom, door + window behind."""
    p = C.pal(weather)

    def draw(c):
        C.sky(c, weather, W, H, H)
        c.drawRect(skia.Rect.MakeLTRB(160, 0, 1760, H), fill(p["wall"]))
        c.drawRect(skia.Rect.MakeLTRB(1500, 0, 1760, H), fill(p["wall_shade"], 0.6))
        C.rect_line(c, 300, 180, 420, 600, K.shade(p["window"], -0.1), p["line"], 3)   # door
        c.drawRect(skia.Rect.MakeXYWH(320, 200, 380, 560), fill(p["wall_dark"], 0.4))
        C.rect_line(c, 900, 220, 460, 380, p["window"], p["line"], 3)                    # window
        for k in range(1, 5):
            c.drawLine(900 + k * 92, 220, 900 + k * 92, 600, stroke(p["wall_dark"], 4))
        c.drawRect(skia.Rect.MakeLTRB(160, 940, 1760, H), fill(p["wall_shade"]))   # balcony floor
    C.blit(cv, C.cached(("block_top", weather), draw))


def draw_top_rail(cv, t, weather="dawn_wet", coda=True, rain=0.0):
    """Front layer for view='top': the balcony railing (draw AFTER Meghnath) + chilli pot + rain."""
    p = C.pal(weather)

    def draw(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 860, W, 900), fill(p["wall"]))
        c.drawRect(skia.Rect.MakeLTRB(0, 860, W, 900), stroke(p["line"], 3))
        for k in range(0, W, 60):
            c.drawLine(k + 30, 900, k + 30, H, stroke(p["wall_dark"], 6))
        c.drawRect(skia.Rect.MakeLTRB(0, 1000, W, H), fill(p["wall"]))
        c.drawLine(0, 1000, W, 1000, stroke(p["line"], 3))
    C.blit(cv, C.cached(("block_top_rail", weather), draw))
    if coda:
        _chilli_pot(cv, TOP_POT[0], TOP_POT[1], 1.4, t, p)
    if rain > 0:
        WF.rain(cv, t, rain)
