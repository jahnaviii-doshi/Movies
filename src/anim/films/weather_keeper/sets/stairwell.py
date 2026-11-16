"""Block C stairwell (government-block concrete: two-tone painted walls, steel railing, grilles).

draw_stairwell(cv, t, view='landing'|'top', weather='heat'|'evening'|'night'|'monsoon', gap_glow=1.0,
               door_open=0.0)
  'landing': mid-building landing seen from the side. A flight comes DOWN from the upper right onto the
      landing; a grille window throws hard light stripes; the bare wall at left is where Rehan bounces
      his ball (tok tok tok).
      LANDING_Y = 905 (floor line), LANDING_S = 1.5 (kids), BALL_WALL_X = 250 (wall face),
      STEPS_DOWN = [(x, y), ...] foot positions top->bottom of the flight Meghnath descends,
      MEGHNATH_DOOR = None here.
  'top': the top flight up to the ROOF DOOR: a steel door with a fat padlock + chain and a hand-painted
      sign (a big red cross, NO text). Beside the door a crack where it doesn't meet the wall (GAP) leaks
      a blade of light; a pigeon and a small boy can squeeze through. Meghnath's flat door is on the
      top landing at left.
      ROOF_DOOR = (x, y, w, h); GAP = (x, y, w, h); MEGHNATH_DOOR = (x, y, w, h);
      TOP_STEPS = [(x, y), ...] bottom->top of the last flight; TOP_FLOOR_Y = 640 (top landing floor),
      TOP_S = 1.25; BOTTOM_Y = 1040 (frame bottom landing), BOTTOM_S = 1.6.
  door_open 0..1 (top view): the roof door scraping open (Tara & Rehan tumble through later).
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C

LANDING_Y = 905
LANDING_S = 1.5
BALL_WALL_X = 250
STEPS_DOWN = [(1700 - i * 70, 560 + i * 34) for i in range(11)]

ROOF_DOOR = (1240, 210, 300, 430)
GAP = (1540, 220, 26, 420)
MEGHNATH_DOOR = (260, 250, 260, 390)
TOP_FLOOR_Y = 640
TOP_S = 1.25
TOP_STEPS = [(560 + i * 62, 1040 - i * 40) for i in range(11)]
BOTTOM_Y = 1040
BOTTOM_S = 1.6


def _walls(c, p, dado_col, y_split):
    c.drawRect(skia.Rect.MakeWH(W, H), fill(p["wall"]))
    c.drawRect(skia.Rect.MakeLTRB(0, y_split, W, H), fill(dado_col))
    c.drawRect(skia.Rect.MakeLTRB(0, y_split - 6, W, y_split), fill(K.shade(dado_col, -0.2)))
    r = K.rng(7)
    for i in range(14):   # scuffs + peeling paint
        x, y = r.uniform(0, W), r.uniform(0, H)
        c.drawPath(ellipse(x, y, r.uniform(10, 40), r.uniform(5, 16)), fill(p["wall_dark"], 0.18))


def _dado(p, weather):
    return {"heat": "#7fae9c", "evening": "#8a9a7c", "night": "#2f4a52", "monsoon": "#5e8a80",
            "dust": "#8a5a36", "monsoon_night": "#24384a", "dawn_wet": "#6fae96"}.get(weather, "#7fae9c")


def _landing_static(weather):
    p = C.pal(weather)
    dado = _dado(p, weather)

    def draw(c):
        _walls(c, p, dado, 560)
        # grille window (upper middle) + the light it throws
        gx, gy, gw, gh = 760, 140, 300, 260
        c.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), fill(p["sky_mid"] if not C.is_night(weather) else "#1a2140"))
        for k in range(1, 6):
            c.drawLine(gx + k * gw / 6, gy, gx + k * gw / 6, gy + gh, stroke(p["line"], 5))
        for k in range(1, 4):
            c.drawLine(gx, gy + k * gh / 4, gx + gw, gy + k * gh / 4, stroke(p["line"], 5))
        c.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), stroke(p["line"], 4))
        if weather in ("heat", "evening"):
            light = "#fff6dc" if weather == "heat" else "#ffcf98"
            for k in range(6):
                x0 = gx + k * gw / 6 + 6
                c.drawPath(poly([(x0, gy + gh), (x0 + gw / 6 - 12, gy + gh), (x0 + gw / 6 + 260, LANDING_Y),
                                 (x0 + 280, LANDING_Y)]), fill(light, 0.22))
        # the flight coming down from upper right (side view, sawtooth)
        path = skia.Path()
        path.moveTo(W + 20, STEPS_DOWN[0][1] - 34)
        for (x, y) in STEPS_DOWN:
            path.lineTo(x + 35, y - 34 + 0)
            path.lineTo(x + 35, y)
            path.lineTo(x - 35, y)
        path.lineTo(STEPS_DOWN[-1][0] - 35, LANDING_Y)
        path.lineTo(W + 20, LANDING_Y)
        path.close()
        c.drawPath(path, fill("#b9b2a6" if not C.is_night(weather) else "#4a4e66"))
        c.drawPath(path, stroke(p["line"], 3))
        # underside of stairs (dark wedge)
        c.drawPath(poly([(STEPS_DOWN[-1][0] - 35, LANDING_Y), (W + 20, STEPS_DOWN[0][1] + 120), (W + 20, LANDING_Y)]),
                   fill(p["wall_dark"], 0.35))
        # railing along the flight
        rail = [(x, y - 150) for (x, y) in STEPS_DOWN]
        c.drawPath(smooth_path(rail, close=False), stroke("#5a5e66", 8))
        for (x, y) in STEPS_DOWN[::2]:
            c.drawLine(x, y, x, y - 150, stroke("#5a5e66", 5))
        # landing floor
        c.drawRect(skia.Rect.MakeLTRB(0, LANDING_Y, W, H), fill("#c9c1b4" if not C.is_night(weather) else "#3e4258"))
        c.drawLine(0, LANDING_Y, W, LANDING_Y, stroke(p["line"], 3))
        for x in range(0, W, 160):
            c.drawLine(x, LANDING_Y, x - 60, H, stroke(p["line"], 1.4, 0.3))
        # wall corner at left (ball wall)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, BALL_WALL_X, H), fill(K.shade(p["wall"], -0.08)))
        c.drawRect(skia.Rect.MakeLTRB(0, 560, BALL_WALL_X, H), fill(K.shade(dado, -0.1)))
        c.drawLine(BALL_WALL_X, 0, BALL_WALL_X, LANDING_Y, stroke(p["line"], 3))
        # ball scuff marks on the wall
        for k in range(6):
            c.drawCircle(BALL_WALL_X - 30 + k * 4, 640 + (k % 3) * 18, 7, fill(p["wall_dark"], 0.35))
        # electric meter box + wires
        C.rect_line(c, 420, 300, 120, 160, "#d9d2c0", p["line"], 2.6)
        for k in range(3):
            C.wire(c, 480, 300, 700 + k * 40, -10, 30, p["line"], 2.2)
    return C.cached(("stair_land", weather), draw)


def _top_static(weather):
    p = C.pal(weather)
    dado = _dado(p, weather)

    def draw(c):
        _walls(c, p, dado, 470)
        # top landing floor slab
        c.drawRect(skia.Rect.MakeLTRB(0, TOP_FLOOR_Y, W, TOP_FLOOR_Y + 30), fill("#c9c1b4"))
        c.drawLine(0, TOP_FLOOR_Y, W, TOP_FLOOR_Y, stroke(p["line"], 3))
        # Meghnath's flat door (wooden, nameplate shape but blank, a shoe rack)
        x, y, w, h = MEGHNATH_DOOR
        C.rect_line(c, x - 18, y - 18, w + 36, h + 18, K.shade(p["wall"], -0.1), p["line"], 2.6)
        C.rect_line(c, x, y, w, h, "#7a4a2e", p["line"], 3)
        for k in range(2):
            C.rect_line(c, x + 24, y + 24 + k * (h / 2 - 10), w - 48, h / 2 - 44, "#8a5838", p["line"], 2)
        c.drawCircle(x + w - 30, y + h / 2, 8, fill("#d8b04a"))
        C.rect_line(c, x + w / 2 - 40, y - 60, 80, 26, "#e9e2cc", p["line"], 2)   # blank nameplate
        C.rect_line(c, x + w + 30, TOP_FLOOR_Y - 60, 110, 60, "#9a8a6a", p["line"], 2)   # shoe rack
        for k in range(3):
            c.drawPath(ellipse(x + w + 52 + k * 32, TOP_FLOOR_Y - 66, 13, 6), fill("#4a3a3a"))
        # stair flight rising from bottom-left to the top landing (side view)
        path = skia.Path()
        path.moveTo(TOP_STEPS[0][0] - 40, H + 20)
        for (sx, sy) in TOP_STEPS:
            path.lineTo(sx - 31, sy)
            path.lineTo(sx + 31, sy)
            path.lineTo(sx + 31, sy - 40)
        path.lineTo(TOP_STEPS[-1][0] + 31, TOP_FLOOR_Y)
        path.lineTo(TOP_STEPS[-1][0] + 31, H + 20)
        path.close()
        c.drawPath(path, fill("#b9b2a6"))
        c.drawPath(path, stroke(p["line"], 3))
        rail = [(sx, sy - 140) for (sx, sy) in TOP_STEPS]
        c.drawPath(smooth_path(rail, close=False), stroke("#5a5e66", 8))
        for (sx, sy) in TOP_STEPS[::2]:
            c.drawLine(sx, sy, sx, sy - 140, stroke("#5a5e66", 5))
        # bottom landing
        c.drawRect(skia.Rect.MakeLTRB(0, BOTTOM_Y, W, H), fill("#c9c1b4"))
    return C.cached(("stair_top", weather), draw)


def _roof_door(cv, t, p, weather, gap_glow, door_open):
    x, y, w, h = ROOF_DOOR
    # frame
    C.rect_line(cv, x - 20, y - 20, w + 40, h + 20, K.shade(p["wall"], -0.12), p["line"], 3)
    # light behind (visible when open / through the gap)
    out = "#fff4d6" if weather == "heat" else "#ffc890" if weather == "evening" else "#8aa0c8"
    if door_open > 0:
        cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(out))
    # the door leaf swings in (narrows toward its hinge at the left)
    leaf_w = w * (1 - 0.82 * K.ease_in_out(door_open))
    leaf = poly([(x, y), (x + leaf_w, y + 14 * door_open), (x + leaf_w, y + h - 14 * door_open), (x, y + h)])
    cv.drawPath(leaf, fill("#5f7486"))
    for k in range(3):
        yy = y + 40 + k * (h - 80) / 2
        cv.drawLine(x + 10, yy, x + leaf_w - 10, yy + 4 * door_open, stroke("#4a5e70", 6))
    cv.drawPath(leaf, stroke(p["line"], 3))
    if door_open < 0.15:
        # the sign: a big red cross, hand-painted (no text)
        sx, sy = x + w / 2 - 70, y + 70
        C.rect_line(cv, sx, sy, 140, 110, "#f2ecd8", p["line"], 2.6)
        cv.drawLine(sx + 30, sy + 22, sx + 110, sy + 88, stroke("#d8322e", 14))
        cv.drawLine(sx + 110, sy + 22, sx + 30, sy + 88, stroke("#d8322e", 14))
        # chain + fat padlock
        cx, cy = x + w - 40, y + h / 2
        for k in range(7):
            cv.drawPath(ellipse(cx - 60 + k * 14, cy + (k % 2) * 3, 9, 6), stroke("#8a8e96", 4))
        lock = rrect(cx - 34, cy + 6, 68, 62, 10)
        cv.drawPath(smooth_path([(cx - 22, cy + 8), (cx - 22, cy - 26), (cx + 22, cy - 26), (cx + 22, cy + 8)],
                                close=False, tension=0.4), stroke("#9aa0aa", 9))
        cv.drawPath(lock, fill("#d8b04a"))
        cv.drawPath(lock, stroke(p["line"], 3))
        cv.drawCircle(cx, cy + 30, 7, fill(p["line"]))
        cv.drawRect(skia.Rect.MakeXYWH(cx - 3, cy + 32, 6, 18), fill(p["line"]))
    # the gap beside the door: a crack leaking a blade of light
    gx, gy, gw, gh = GAP
    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), fill(out))
    if gap_glow > 0:
        blade = poly([(gx, gy), (gx + gw, gy), (gx + gw + 420, TOP_FLOOR_Y + 30), (gx - 60, TOP_FLOOR_Y + 30)])
        cv.drawPath(blade, fill(out, 0.18 * gap_glow))
        motes = K.rng(9)
        for i in range(16):
            mx = gx + motes.uniform(-20, 300)
            my = gy + (motes.uniform(0, gh) - t * 8 * motes.uniform(0.5, 1.5)) % gh
            cv.drawCircle(mx, my, 2, fill("#ffffff", 0.5 * gap_glow))
    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), stroke(p["line"], 2))


def draw_stairwell(cv, t, view="landing", weather="heat", gap_glow=1.0, door_open=0.0):
    p = C.pal(weather)
    if view == "landing":
        C.blit(cv, _landing_static(weather))
    else:
        C.blit(cv, _top_static(weather))
        _roof_door(cv, t, p, weather, gap_glow, door_open)
