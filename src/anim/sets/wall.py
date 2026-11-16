"""The blank blue wall at the dead end, and the shop unfolding out of it. THE hero effect.

draw_wall(cv, t, time='night'|'dawn', glow=0.0, unfold=0.0, flicker=0.0, fold=0.0, handprint=0.0, cam=None)
    glow     0..1  gold cracks appear one by one and join into the outline of a doorway
    unfold   0..1  pop-up book: four wall leaves hinge outward (overshoot + settle), a striped
                   awning drops and snaps taut, the door shutters swing open, five lanterns blink
                   alight one by one, shelves slide out and their jars light up, warm light floods
                   the lane. Drive it with ~6-8 s of screen time for full effect.
    flicker  0..1  the sad, broken version: outline stutters like a dying bulb, half an awning,
                   one lantern, a ghost of a door. (Use instead of unfold.)
    fold     0..1  dawn: the open shop calmly folds back into the wall (use with unfold=1 or 0).
    handprint 0..1 a small golden handprint glows on the wall (peak ~0.5) and fades.
    cam      None or (cx, cy, zoom)

Anchors
    FLOOR_Y = 905, CHAR_S = 1.55  (people standing in front of the wall; Meher ≈ 465 px tall)
    DOG_S = 1.1
    DOOR_RECT = (835, 335, 1085, 905)  where characters step in (x centre 960)
    OPENING = (600, 230, 1320, 905)     the region of wall that unfolds
    STAND_X = dict(left=640, centre=960, right=1280)  good marks in front of the wall
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import skia

from .. import core as K
from ..core import C, fill, stroke, lerp, clamp, smooth_path, poly, ellipse, seg, ease_out_back, ease_in_out, ease_out
from .gali import bloom, peeling_wall, apply_cam, overlay, W, H

FLOOR_Y = 905
CHAR_S = 1.55
DOG_S = 1.1
WALL_L, WALL_R, WALL_T = 300, 1620, 150
OPENING = (600, 230, 1320, 905)
DOOR_RECT = (835, 335, 1085, 905)
STAND_X = dict(left=640, centre=960, right=1280)
VPX, VPY, D = 960.0, 560.0, 1100.0
SWEETS = ["saffron", "rose", "pistachio", "silver"]


def proj(x, y, dz):
    f = D / (D - dz)
    return (VPX + (x - VPX) * f, VPY + (y - VPY) * f)


def quad_matrix(w, h, dst):
    m = skia.Matrix()
    m.setPolyToPoly([skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)],
                    [skia.Point(*p) for p in dst])
    return m


# ------------------------------------------------------------------ sweets & jars (shared with shop.py)
def jar(cv, x, y, w, h, color="saffron", kind="laddoo", lit=1.0, t=0.0, seed=0, empty=False):
    """Glass jar standing on y (base), centred at x. lit 0..1 inner glow."""
    rng = K.rng(seed)
    gl = K.hexrgb(K.PAL.get(color, color))
    body = K.rrect(x - w / 2, y - h, w, h, w * 0.22)
    if lit > 0 and not empty:
        cv.drawCircle(x, y - h * 0.45, w * 1.3, K.rad_a((x, y - h * 0.45), w * 1.3, [(gl, 0.32 * lit), (gl, 0)]))
    cv.drawPath(body, fill("#dfe9f5", 0.22))
    if not empty:
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        fill_top = y - h * 0.78
        if kind == "laddoo":
            r = w * 0.17
            for row in range(5):
                for k in range(3):
                    cx = x - w * 0.3 + k * w * 0.3 + (row % 2) * w * 0.12
                    cy = y - r - row * r * 1.7
                    if cy - r > fill_top - r:
                        cv.drawCircle(cx, cy, r, K.rad((cx - r * 0.3, cy - r * 0.3), r * 1.2, ["#ffe08a", color, K.shade(color, -0.3)]))
        elif kind == "barfi":
            s = w * 0.26
            for row in range(5):
                for k in range(3):
                    cx = x - w * 0.3 + k * w * 0.3
                    cy = y - s * 0.7 - row * s * 0.95
                    if cy > fill_top:
                        r = poly([(cx, cy - s * 0.45), (cx + s * 0.5, cy), (cx, cy + s * 0.45), (cx - s * 0.5, cy)])
                        cv.drawPath(r, fill(K.mix(color, "#ffffff", 0.35)))
                        cv.drawPath(r, stroke("#ffffff", 1.2, 0.8))
        elif kind == "jalebi":
            for k in range(4):
                cx, cy = x + rng.uniform(-w * 0.2, w * 0.2), y - h * 0.18 - k * h * 0.17
                pts = [(cx + math.cos(a) * (2 + a * w * 0.022), cy + math.sin(a) * (2 + a * w * 0.022) * 0.6)
                       for a in np.linspace(0, 12, 40)]
                cv.drawPath(poly(pts, close=False), stroke(K.mix(color, "#ffb02e", 0.3), max(2, w * 0.07)))
        else:  # candy / gulab
            for k in range(14):
                cx, cy = x + rng.uniform(-w * 0.35, w * 0.35), y - rng.uniform(4, h * 0.75)
                cv.drawCircle(cx, cy, w * 0.11, fill(K.shade(color, rng.uniform(-0.2, 0.15))))
        if lit > 0:
            cv.drawRect(skia.Rect.MakeLTRB(x - w, y - h, x + w, y), K.rad_a((x, y - h * 0.4), h * 0.7, [(gl, 0.55 * lit), (gl, 0)]))
        cv.restore()
    # glass highlight, lid
    cv.drawPath(K.rrect(x - w * 0.36, y - h * 0.88, w * 0.12, h * 0.6, w * 0.06), fill("#ffffff", 0.45))
    cv.drawPath(body, stroke("#3a2a24", max(1.2, w * 0.035)))
    lid = K.rrect(x - w * 0.42, y - h - h * 0.12, w * 0.84, h * 0.14, h * 0.04)
    cv.drawPath(lid, K.lin((x - w / 2, 0), (x + w / 2, 0), ["brass_dark", "brass_light", "brass"]))
    cv.drawPath(lid, stroke("#3a2a24", max(1.0, w * 0.03)))
    cv.drawCircle(x, y - h - h * 0.15, w * 0.08, fill("brass"))


def jar_glow(cv, x, y, w, h, color, lit):
    gl = K.hexrgb(K.PAL.get(color, color))
    cv.drawCircle(x, y - h * 0.45, w * 0.55, fill(gl, 0.6 * lit))


def lantern(cv, x, y, s=1.0, lit=1.0, t=0.0, seed=0):
    """Brass hanging lantern; (x,y) = hook point."""
    sw = math.sin(t * 1.3 + seed) * 3
    cv.save(); cv.translate(x, y); cv.rotate(sw); cv.scale(s, s)
    cv.drawLine(0, 0, 0, 22, stroke("#3a2a24", 2))
    flick = 1 + 0.08 * math.sin(t * 13 + seed * 3) + 0.05 * math.sin(t * 7.3 + seed)
    a = lit * flick
    if lit > 0:
        cv.drawCircle(0, 52, 70, K.rad_a((0, 52), 70, [("#ffcf6e", 0.45 * a), ("#ffb02e", 0.0)]))
    top = poly([(-14, 22), (14, 22), (20, 34), (-20, 34)])
    cv.drawPath(top, fill("brass")); cv.drawPath(top, stroke("line", 2))
    glass = K.rrect(-16, 34, 32, 38, 7)
    cv.drawPath(glass, fill(K.mix("#3a2a24", "#ffe7a8", clamp(a)), 1.0))
    if lit > 0:
        cv.drawCircle(0, 54, 9 * clamp(a), fill("#fff6d8", clamp(a)))
    for k in (-8, 0, 8):
        cv.drawLine(k, 34, k, 72, stroke("brass_dark", 1.6))
    cv.drawPath(glass, stroke("line", 2))
    bot = poly([(-20, 72), (20, 72), (12, 82), (-12, 82)])
    cv.drawPath(bot, fill("brass")); cv.drawPath(bot, stroke("line", 2))
    cv.drawCircle(0, 86, 4, fill("brass"))
    cv.restore()


def sparkle(cv, x, y, r, a, col="#fff6d8"):
    if a <= 0.01:
        return
    p = smooth_path([(x, y - r), (x + r * 0.2, y - r * 0.2), (x + r, y), (x + r * 0.2, y + r * 0.2), (x, y + r),
                     (x - r * 0.2, y + r * 0.2), (x - r, y), (x - r * 0.2, y - r * 0.2)], tension=0.2)
    cv.drawPath(p, fill(col, clamp(a)))
    cv.drawCircle(x, y, r * 0.6, K.rad_a((x, y), r * 0.6, [(col, 0.6 * clamp(a)), (col, 0)]))


# ------------------------------------------------------------------ static background
def _sky(c, time):
    if time == "night":
        c.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, 500), ["night_sky_top", "night_sky_mid", "night_sky_low"]))
        K.stars(c, W, 260, 1.0, n=120, seed=21)
        c.drawCircle(1500, 70, 200, K.rad_a((1500, 70), 200, [("moonglow", 0.3), ("moonglow", 0)]))
        c.drawCircle(1500, 70, 38, fill("moon"))
        c.drawCircle(1490, 62, 7, fill("#e6dcb8")); c.drawCircle(1512, 80, 5, fill("#e6dcb8"))
    else:
        c.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, 500), ["#7d8fc4", "#e3a3a8", "#ffd2a0"]))
        c.drawCircle(960, 260, 600, K.rad_a((960, 260), 600, [("#fff1c8", 0.4), ("#fff1c8", 0)]))


def _skyline(c, time):
    col = "#262a55" if time == "night" else "#a8879f"
    rng = K.rng(12)
    x = 200
    while x < 1720:
        w = rng.uniform(70, 150); h = rng.uniform(40, 120)
        if rng.random() < 0.25:
            x += 40; continue
        c.drawRect(skia.Rect.MakeLTRB(x, WALL_T - h, x + w, WALL_T + 5), fill(col))
        if rng.random() < 0.3:
            c.drawPath(smooth_path([(x + 10, WALL_T - h), (x + w / 2, WALL_T - h - 50), (x + w - 10, WALL_T - h)], tension=0.5), fill(col))
        elif rng.random() < 0.4:
            c.drawPath(K.rrect(x + w * 0.4, WALL_T - h - 30, 26, 30, 6), fill(K.shade(col, -0.2)))
        x += w


def _side_facade(c, side, time):
    """Edges of the side houses, in perspective, framing the wall."""
    if side < 0:
        dst = [(-260, -600), (WALL_L, WALL_T - 140), (WALL_L, FLOOR_Y), (-260, 1500)]
        col = "#e6b4a3"
    else:
        dst = [(WALL_R, WALL_T - 140), (2180, -600), (2180, 1500), (WALL_R, FLOOR_Y)]
        col = "#dcae6a"
    ew, eh = 600, 1000   # elevation: x 0..600 (0 = far edge at the wall for the right side)
    m = quad_matrix(ew, eh, dst)
    c.save(); c.concat(m)
    c.drawRect(skia.Rect.MakeWH(ew, eh), K.lin((0, 0), (0, eh), [K.shade(col, 0.05), col, K.shade(col, -0.15)]))
    rng = K.rng(3 if side < 0 else 4)
    for _ in range(30):
        x, y = rng.uniform(0, ew), rng.uniform(0, eh)
        c.drawPath(ellipse(x, y, rng.uniform(8, 30), rng.uniform(5, 16)), fill(K.shade(col, rng.uniform(-0.15, 0.06)), 0.4))
    c.drawRect(skia.Rect.MakeLTRB(0, eh - 60, ew, eh), fill(K.shade(col, -0.25)))
    # a door and a window in perspective
    dx = 330 if side < 0 else 160
    door = smooth_path([(dx, eh - 6), (dx, eh - 300), (dx + 60, eh - 360), (dx + 120, eh - 300), (dx + 120, eh - 6)], tension=0.4)
    c.drawPath(door, fill("#5a3a2a")); c.drawPath(door, stroke("line", 3))
    c.drawLine(dx + 60, eh - 350, dx + 60, eh - 6, stroke("line", 2))
    c.drawCircle(dx + 40, eh - 170, 7, fill("brass")); c.drawCircle(dx + 80, eh - 170, 7, fill("brass"))
    wx = 120 if side < 0 else 380
    win = smooth_path([(wx, 520), (wx, 440), (wx + 45, 400), (wx + 90, 440), (wx + 90, 520)], tension=0.4)
    c.drawPath(win, fill("#1c1622")); c.drawPath(win, stroke("line", 3))
    for k in (-1, 1):
        sh = K.rrect(wx + (90 if k > 0 else -40), 410, 40, 112, 4)
        c.drawPath(sh, fill("#3f7d6a")); c.drawPath(sh, stroke("line", 2.4))
    # drainpipe at the corner
    px = 8 if side > 0 else ew - 20
    c.drawRect(skia.Rect.MakeLTRB(px, 0, px + 14, eh - 4), fill("#6b6a6e"))
    c.drawRect(skia.Rect.MakeWH(ew, eh), stroke("line", 3))
    c.restore()


def _floor(c, time):
    col = "#b9a58a"
    c.drawRect(skia.Rect.MakeLTRB(0, FLOOR_Y, W, H), K.lin((0, FLOOR_Y), (0, H), [K.shade(col, -0.1), col]))
    # flagstone joints converging to the vanishing point
    for k in range(-14, 15):
        x0 = 960 + k * 75
        x1 = VPX + (x0 - VPX) * 2.4
        c.drawLine(x0, FLOOR_Y, x1, H + 300, stroke(K.shade(col, -0.32), 1.6, 0.7))
    for y in (FLOOR_Y + 22, FLOOR_Y + 52, FLOOR_Y + 92, FLOOR_Y + 146):
        c.drawLine(0, y, W, y, stroke(K.shade(col, -0.32), 1.6, 0.7))
    # doorstep slab
    st = K.rrect(800, FLOOR_Y - 6, 320, 26, 6)
    c.drawPath(st, fill("#c9b79a")); c.drawPath(st, stroke("line", 2.4))


def _wall_layer(c, time):
    # the wall in screen coords: map an elevation (cm) to rect WALL_L..WALL_R x WALL_T..FLOOR_Y
    a0, a1, top = 0.0, 440.0, -250.0
    sx = (WALL_R - WALL_L) / (a1 - a0)
    sy = (FLOOR_Y - WALL_T) / -top
    c.save(); c.translate(WALL_L, FLOOR_Y); c.scale(sx, sy)
    peeling_wall(c, a0, a1, top, seed=91, line_w=0.9, flakes=0.9)
    c.restore()
    # wires over the wall
    rng = K.rng(9)
    for i in range(6):
        y0, y1 = rng.uniform(40, 200), rng.uniform(40, 200)
        sag = rng.uniform(30, 90)
        pts = [(x, lerp(y0, y1, x / W) + sag * 4 * (x / W) * (1 - x / W)) for x in range(-20, W + 21, 40)]
        c.drawPath(poly(pts, close=False), stroke("#141018", 2.4, 0.95))


LIGHT = {"night": ("night", 1.0), "dawn": ("dawn", 1.0)}


def _grade_overlay(c, time):
    if time == "night":
        c.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 600), (0, H), [("#04030e", 0.0), ("#04030e", 0.45)]))
        p = skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(1300, 0), 1300, [C("#c9d8ff", 0.22), C("#c9d8ff", 0.0)]), AntiAlias=True)
        p.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), p)
    else:
        p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)],
                       [C("#ffd8a0", 0.35), C("#ffd8a0", 0.0)]), AntiAlias=True)
        p.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), p)


@lru_cache(maxsize=8)
def _bg(time, scale=1.0):
    surf = skia.Surface(int(W * scale), int(H * scale)); c = surf.getCanvas(); c.scale(scale, scale)
    _sky(c, time)
    light, amt = LIGHT[time]
    with K.lit(c, light, amt):
        _skyline(c, time)
        _wall_layer(c, time)
        _side_facade(c, -1, time)
        _side_facade(c, 1, time)
        _floor(c, time)
    _grade_overlay(c, time)
    return surf.makeImageSnapshot()


@lru_cache(maxsize=4)
def _wall_only(time):
    """Wall image (graded) used for the front faces of the leaves."""
    surf = skia.Surface(W, H); c = surf.getCanvas()
    light, amt = LIGHT[time]
    with K.lit(c, light, amt):
        _wall_layer(c, time)
    _grade_overlay(c, time)
    return surf.makeImageSnapshot()


@lru_cache(maxsize=4)
def _leaf_back(w, h, seed):
    """Inner face of a wall leaf: carved, painted wood with flowers."""
    surf = skia.Surface(int(w), int(h)); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(w, h), K.lin((0, 0), (w, h), ["#7a2f22", "#5a2016"]))
    c.drawRect(skia.Rect.MakeLTRB(10, 10, w - 10, h - 10), stroke("#e3a72f", 5))
    c.drawRect(skia.Rect.MakeLTRB(24, 24, w - 24, h - 24), stroke("#c97a12", 2.5))
    rng = K.rng(seed)
    # flower/vine motif
    cx = w / 2
    for k in range(int(h // 70)):
        y = 50 + k * 70
        c.drawPath(smooth_path([(cx, y - 35), (cx + 12 * (1 if k % 2 else -1), y), (cx, y + 35)], close=False), stroke("#9bdc6b", 3))
        col = ["#ffb02e", "#ff6fa5", "#eef2ff"][k % 3]
        for a in range(6):
            ang = a * math.pi / 3
            c.drawCircle(cx + math.cos(ang) * 10, y + math.sin(ang) * 10, 7, fill(col))
        c.drawCircle(cx, y, 6, fill("#ffd36b"))
        for sd in (-1, 1):
            c.drawPath(ellipse(cx + sd * 30, y + 20, 12, 6), fill("#6fb04a"))
    # border dots
    for y in range(30, int(h) - 20, 22):
        for x in (18, w - 18):
            c.drawCircle(x, y, 2.6, fill("#ffd36b"))
    return surf.makeImageSnapshot()


@lru_cache(maxsize=2)
def _recess():
    """The opened shopfront (behind the leaves), without shutters/shelves/jars/awning/lanterns."""
    surf = skia.Surface(W, H); c = surf.getCanvas()
    l, t, r, b = OPENING
    # deep warm interior
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, b), K.lin((0, t), (0, b), ["#5a2a14", "#8a4a1c", "#3a1a0c"]))
    # back wall of the shop seen through: warm plaster with niches
    c.drawRect(skia.Rect.MakeLTRB(l + 20, t + 40, r - 20, b), fill("#7a3f1a"))
    # side shelf bays (back panels)
    for (x0, x1) in ((l + 14, DOOR_RECT[0] - 18), (DOOR_RECT[2] + 18, r - 14)):
        c.drawRect(skia.Rect.MakeLTRB(x0, t + 120, x1, b - 40), K.lin((x0, 0), (x1, 0), ["#4a2210", "#6a3418", "#4a2210"]))
        c.drawRect(skia.Rect.MakeLTRB(x0, t + 120, x1, b - 40), stroke("#2a1208", 3))
    # door: interior glow seen through the doorway
    dl, dt, dr, db = DOOR_RECT
    door = smooth_path([(dl, db), (dl, dt + 60), (dl + 30, dt + 10), ((dl + dr) / 2, dt - 12), (dr - 30, dt + 10), (dr, dt + 60), (dr, db)], tension=0.4)
    c.drawPath(door, K.lin((0, dt), (0, db), ["#ffd27a", "#e8902a", "#8a3f12"], [0, 0.45, 1]))
    c.save(); c.clipPath(door, doAntiAlias=True)
    # interior: far shelves with glowing jars, a hanging lantern, the end of the counter
    c.drawRect(skia.Rect.MakeLTRB(dl, dt, dr, db), K.rad_a(((dl + dr) / 2, dt + 140), 260, [("#fff2c8", 0.7), ("#ffd27a", 0.0)]))
    for k in range(4):
        y = dt + 150 + k * 95
        c.drawRect(skia.Rect.MakeLTRB(dl, y, dr, y + 9), fill("#7a3a12", 0.85))
        for j in range(5):
            jx = dl + 28 + j * 48
            col = ["#ff8a3a", "#ff6fa5", "#9bdc6b", "#fff2d0", "#ffb02e"][(j + k) % 5]
            c.drawCircle(jx, y - 20, 26, K.rad_a((jx, y - 20), 26, [(col, 0.45), (col, 0)]))
            c.drawPath(K.rrect(jx - 12, y - 40, 24, 40, 7), fill(col, 0.85))
            c.drawPath(K.rrect(jx - 12, y - 40, 24, 40, 7), stroke("#5a2a10", 1.6))
    cnt = K.rrect(dl - 10, db - 170, (dr - dl) * 0.7, 40, 6)
    c.drawPath(cnt, fill("#6a3014")); c.drawRect(skia.Rect.MakeLTRB(dl - 10, db - 130, dl + (dr - dl) * 0.7 - 10, db), fill("#4a200c"))
    c.drawLine((dl + dr) / 2 + 40, dt - 10, (dl + dr) / 2 + 40, dt + 60, stroke("#3a1a0c", 2))
    c.drawPath(K.rrect((dl + dr) / 2 + 28, dt + 60, 24, 30, 6), fill("#fff1c2"))
    c.drawRect(skia.Rect.MakeLTRB(dl, db - 60, dr, db), fill("#a8541a", 0.5))
    c.restore()
    # carved door frame
    fr = smooth_path([(dl - 26, db), (dl - 26, dt + 50), (dl + 20, dt - 14), ((dl + dr) / 2, dt - 40), (dr - 20, dt - 14),
                      (dr + 26, dt + 50), (dr + 26, db), (dr, db), (dr, dt + 60), (dr - 30, dt + 10), ((dl + dr) / 2, dt - 12),
                      (dl + 30, dt + 10), (dl, dt + 60), (dl, db)], tension=0.3)
    c.drawPath(fr, K.lin((dl, 0), (dr, 0), ["#8a4a1c", "#c97a32", "#8a4a1c"]))
    c.drawPath(fr, stroke("line", 3))
    for k in range(9):
        y = dt + 60 + k * 58
        for x in (dl - 13, dr + 13):
            c.drawCircle(x, y, 5, fill("#ffd36b"))
    # pillars at the opening edges
    for x in (l, r - 40):
        c.drawPath(K.rrect(x, t, 40, b - t, 6), K.lin((x, 0), (x + 40, 0), ["#6a3418", "#b0682a", "#6a3418"]))
        c.drawPath(K.rrect(x, t, 40, b - t, 6), stroke("line", 3))
        for y in range(int(t) + 40, int(b) - 30, 90):
            c.drawPath(ellipse(x + 20, y, 12, 20), stroke("#ffd36b", 2.4))
    # lintel with carved scallops + marigold garland
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, t + 46), K.lin((0, t), (0, t + 46), ["#b0682a", "#7a3f1a"]))
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, t + 46), stroke("line", 3))
    for k in range(int((r - l) // 40)):
        c.drawPath(smooth_path([(l + k * 40, t + 46), (l + k * 40 + 20, t + 66), (l + k * 40 + 40, t + 46)], close=False), stroke("#ffd36b", 2.4))
    for k in range(3):
        x0 = l + 60 + k * (r - l - 120) / 3; x1 = x0 + (r - l - 120) / 3
        for j in range(16):
            s = j / 15
            x = lerp(x0, x1, s); y = t + 60 + 50 * 4 * s * (1 - s)
            c.drawCircle(x, y, 9, fill("#ff9a1a" if j % 2 else "#ffc21a"))
            c.drawCircle(x, y, 9, stroke("#a8541a", 1.2))
    # threshold glow pool
    c.drawRect(skia.Rect.MakeLTRB(dl, db - 30, dr, db), fill("#ffd36b", 0.5))
    return surf.makeImageSnapshot()


# ------------------------------------------------------------------ elements
LEAVES = [  # (hinge_x, inner_x, y0, y1, dir, start)
    (OPENING[0], 960, OPENING[1], 560, +1, 0.04),
    (OPENING[2], 960, OPENING[1], 560, -1, 0.09),
    (OPENING[0], 960, 560, OPENING[3], +1, 0.14),
    (OPENING[2], 960, 560, OPENING[3], -1, 0.19),
]
OPEN_ANG = 128.0


def _leaf_quad(hx, ix, y0, y1, ang):
    w = abs(ix - hx)
    d = 1 if ix > hx else -1
    a = math.radians(ang)
    xi = hx + d * w * math.cos(a)
    dz = w * math.sin(a)
    p_h0, p_h1 = (hx, y0), (hx, y1)
    p_i0, p_i1 = proj(xi, y0, dz), proj(xi, y1, dz)
    return p_h0, p_i0, p_i1, p_h1, w


def _draw_leaf(c, leaf, ang, time):
    hx, ix, y0, y1, d, _ = leaf
    p_h0, p_i0, p_i1, p_h1, w = _leaf_quad(hx, ix, y0, y1, ang)
    h = y1 - y0
    front = ang < 90
    if d > 0:
        dst = [p_h0, p_i0, p_i1, p_h1]   # leaf local x: 0 at hinge -> w at inner edge
    else:
        dst = [p_i0, p_h0, p_h1, p_i1]   # local 0 at inner edge (screen-left) -> w at hinge
    c.save()
    c.concat(quad_matrix(w, h, dst))
    if front:
        src = skia.Rect.MakeLTRB(min(hx, ix), y0, max(hx, ix), y1)
        c.drawImageRect(_wall_only(time), src, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear), None)
        shade = clamp(ang / 90) * 0.45
        c.drawRect(skia.Rect.MakeWH(w, h), fill("#000010", shade))
    else:
        img = _leaf_back(int(w), int(h), int(abs(hx) + y0))
        # back face is mirrored horizontally relative to front
        c.save(); c.translate(w, 0); c.scale(-1, 1)
        c.drawImage(img, 0, 0)
        c.restore()
        lightk = clamp((ang - 90) / 60)
        c.drawRect(skia.Rect.MakeWH(w, h), fill("#ffb02e", 0.12 * lightk))
        if time == "night":
            c.drawRect(skia.Rect.MakeWH(w, h), fill("#0a0b2a", 0.25))
    c.drawRect(skia.Rect.MakeWH(w, h), stroke("line", 4))
    c.restore()
    # edge thickness strip on the inner edge
    c.drawLine(*p_i0, *p_i1, stroke("#c97a32" if not front else "#2a5486", 6))


def _crack_paths():
    """Cracks (polylines, in reveal order). The first ones draw an arched doorway; then the
    seams of the four wall leaves; small branches make it organic."""
    l, t, r, b = OPENING
    dl, dt, dr, db = DOOR_RECT
    rng = K.rng(5)

    def jag(pts_in, amp=5, sub=4):
        out = []
        for i in range(len(pts_in) - 1):
            a, bb = pts_in[i], pts_in[i + 1]
            for k in range(sub):
                s_ = k / sub
                x, y = lerp(a[0], bb[0], s_), lerp(a[1], bb[1], s_)
                if i + k > 0:
                    x += rng.uniform(-amp, amp); y += rng.uniform(-amp, amp)
                out.append((x, y))
        out.append(pts_in[-1])
        return out

    def arch(side):
        pts = [(960, db)] if False else []
        x0 = dl if side < 0 else dr
        pts = [(x0, db), (x0, dt + 70)]
        for k in range(1, 9):
            a = math.pi / 2 * k / 8
            pts.append((960 + side * (dr - dl) / 2 * math.cos(a), dt + 70 - 82 * math.sin(a)))
        return pts

    main = [
        jag([(960, db), (958, db - 90), (962, db - 170)], 4, 3),   # seed crack from the doorstep
        jag(arch(-1), 5, 3),                                        # the doorway outline
        jag(arch(1), 5, 3),
        jag([(960, dt - 12), (960, 560), (960, t)][1::-1] + [(960, t)], 5, 4) if False else jag([(960, dt - 12), (960, t)], 5, 5),
        jag([(dl, 560), (l, 560)], 6, 8), jag([(dr, 560), (r, 560)], 6, 8),
        jag([(960, t), (l, t)], 6, 10), jag([(960, t), (r, t)], 6, 10),
        jag([(l, t), (l, b)], 6, 14), jag([(r, t), (r, b)], 6, 14),
    ]
    branches = []
    for src in main[1:]:
        for _ in range(2):
            i = rng.randrange(2, len(src) - 2)
            x, y = src[i]
            ang = rng.uniform(0, 2 * math.pi)
            pts = [(x, y)]
            for k in range(4):
                ang += rng.uniform(-0.6, 0.6)
                x += math.cos(ang) * rng.uniform(10, 22); y += math.sin(ang) * rng.uniform(10, 22)
                pts.append((x, y))
            branches.append(pts)
    return main + branches


CRACKS = _crack_paths()
N_MAIN = 10


def _draw_cracks(c, amount, alpha=1.0, stutter=None, width=3.0):
    n = N_MAIN
    shown = amount * (n + 0.5)
    for i, pts in enumerate(CRACKS):
        f = clamp(shown - i * 0.85) if i < N_MAIN else clamp(shown - (i - N_MAIN) * 0.4 - 2.0)
        if f <= 0:
            continue
        a = alpha * (stutter[i] if stutter else 1.0)
        if a <= 0.01:
            continue
        m = max(2, int(len(pts) * f))
        sub = pts[:m]
        if m < len(pts):
            fr = len(pts) * f - (m - 1)
            last = pts[m - 1]; nxt = pts[min(m, len(pts) - 1)]
            sub = sub + [(lerp(last[0], nxt[0], clamp(fr)), lerp(last[1], nxt[1], clamp(fr)))]
        wd = width if i < N_MAIN else width * 0.6
        c.drawPath(poly(sub, close=False), stroke("#ffe08a", wd, a))
        c.drawPath(poly(sub, close=False), stroke("#ffffff", wd * 0.35, a))


def _awning(c, k, t, partial=1.0, ragged=False, alpha=1.0):
    """k 0..1 drop (elastic). Awning hangs from the lintel and juts toward the camera."""
    if k <= 0.001:
        return
    l, top, r, _ = OPENING
    x0, x1 = l - 40, r + 40
    if partial < 1:
        x1 = lerp(x0, x1, partial)
    drop = 130 * k
    dz = 120 * clamp(k)
    n = 14
    stripes = ["#ff6fa5", "#fff1dd"]
    pts_back = [(lerp(x0, x1, i / n), top) for i in range(n + 1)]
    pts_front = [proj(lerp(x0, x1, i / n), top + drop, dz) for i in range(n + 1)]
    for i in range(n):
        q = poly([pts_back[i], pts_back[i + 1], pts_front[i + 1], pts_front[i]])
        c.drawPath(q, fill(stripes[i % 2], alpha))
    # shading under-curve
    c.drawPath(poly(pts_back + pts_front[::-1]), K.lin_a((0, top), (0, top + drop + 20), [("#000000", 0.0), ("#5a1e22", 0.22 * alpha)]))
    # scalloped valance
    sc_h = 26 * clamp(k * 1.5)
    for i in range(n):
        a, bpt = pts_front[i], pts_front[i + 1]
        mx = (a[0] + bpt[0]) / 2
        yy = (a[1] + bpt[1]) / 2
        jag = 8 * math.sin(i * 7.1) if ragged else 0
        sc = smooth_path([a, (mx, yy + sc_h + jag), bpt], close=False)
        pth = skia.Path(sc); pth.close()
        c.drawPath(pth, fill(stripes[i % 2], alpha))
        c.drawPath(sc, stroke("line", 2.4, alpha))
    c.drawPath(poly(pts_front, close=False), stroke("line", 3, alpha))
    c.drawPath(poly(pts_back, close=False), stroke("line", 3, alpha))
    # rolled bar at the top
    c.drawPath(K.rrect(x0 - 6, top - 12, x1 - x0 + 12, 22, 10), fill("#c94a6a", alpha))
    c.drawPath(K.rrect(x0 - 6, top - 12, x1 - x0 + 12, 22, 10), stroke("line", 3, alpha))
    return pts_front


def _shutters(c, k, time):
    """Door shutters swing inward (away) and vanish behind the frame."""
    dl, dt, dr, db = DOOR_RECT
    if k >= 0.999:
        return
    mid = (dl + dr) / 2
    a = math.radians(100 * k)
    for hx, d in ((dl, 1), (dr, -1)):
        w = mid - dl
        xi = hx + d * w * math.cos(a)
        dz = -w * math.sin(a)
        p_i0, p_i1 = proj(xi, dt + 10, dz), proj(xi, db, dz)
        dst = [(hx, dt + 10), p_i0, p_i1, (hx, db)] if d > 0 else [p_i0, (hx, dt + 10), (hx, db), p_i1]
        c.save(); c.concat(quad_matrix(w, db - dt - 10, dst))
        hh = db - dt - 10
        c.drawRect(skia.Rect.MakeWH(w, hh), K.lin((0, 0), (0, hh), ["#8a3a22", "#5a2016"]))
        for j in range(4):
            c.drawPath(K.rrect(14, 20 + j * hh / 4, w - 28, hh / 4 - 30, 6), stroke("#e3a72f", 3))
            c.drawCircle(w / 2, 20 + j * hh / 4 + (hh / 4 - 30) / 2, 9, fill("#ff6fa5"))
        c.drawCircle(w - 18 if d > 0 else 18, hh * 0.5, 8, fill("brass"))
        c.drawRect(skia.Rect.MakeWH(w, hh), fill("#000000", 0.35 * k))
        c.drawRect(skia.Rect.MakeWH(w, hh), stroke("line", 3))
        c.restore()


SHELF_YS = [450, 575, 700, 825]


def _shelf_slots():
    dl, dt, dr, db = DOOR_RECT
    l, t, r, b = OPENING
    slots = []
    rng = K.rng(17)
    kinds = [("saffron", "laddoo"), ("rose", "barfi"), ("pistachio", "barfi"), ("silver", "barfi"), ("rose", "candy"),
             ("saffron", "jalebi"), ("pistachio", "candy")]
    for side, (x0, x1) in ((-1, (l + 56, dl - 34)), (1, (dr + 34, r - 56))):
        for row, y in enumerate(SHELF_YS):
            n = 3
            for j in range(n):
                x = x0 + (j + 0.5) * (x1 - x0) / n
                col, kind = kinds[(row * 3 + j + (side > 0) * 2) % len(kinds)]
                slots.append(dict(x=x, y=y, side=side, row=row, col=col, kind=kind, w=40, h=54 + (j % 2) * 10,
                                  order=rng.random()))
    return slots


SLOTS = _shelf_slots()


@lru_cache(maxsize=1)
def _shelves_full():
    sf = skia.Surface(W, H); cc = sf.getCanvas(); cc.clear(skia.ColorTRANSPARENT)
    _shelves(cc, 1.0, 1.0, 0.0, live=True)
    return sf.makeImageSnapshot()


def _shelves(c, k, jars_k, t, live=False):
    l, t0, r, b = OPENING
    dl, dt, dr, db = DOOR_RECT
    if k <= 0:
        return
    if k >= 1 and jars_k >= 1 and not live:
        c.drawImage(_shelves_full(), 0, 0)
        return
    e = ease_out(k)
    for side, (x0, x1) in ((-1, (l + 40, dl - 26)), (1, (dr + 26, r - 40))):
        slide = (1 - e) * (x1 - x0 + 60) * (-1 if side < 0 else 1)
        c.save(); c.translate(slide, 0)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(l + 40 if side < 0 else dr + 20, t0, dl - 20 if side < 0 else r - 40, b))
        for y in SHELF_YS:
            c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + 14), K.lin((0, y), (0, y + 14), ["#c97a32", "#7a3f1a"]))
            c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + 14), stroke("line", 2.4))
            for x in (x0 + 12, x1 - 12):
                c.drawPath(poly([(x - 8, y + 14), (x + 8, y + 14), (x, y + 34)]), fill("#7a3f1a"))
        for s in SLOTS:
            if s["side"] != side:
                continue
            jk = clamp((jars_k - s["order"] * 0.6) / 0.4)
            if jk <= 0:
                continue
            pop = ease_out_back(clamp(jk * 2.5), 2.2)
            c.save(); c.translate(s["x"], s["y"]); c.scale(pop, pop)
            jar(c, 0, 0, s["w"], s["h"], s["col"], s["kind"], lit=jk, t=t, seed=int(s["x"] + s["y"]))
            c.restore()
        c.restore()
        c.restore()


LANTERN_X = [640, 800, 960, 1120, 1280]


def _lantern_hooks(pts_front):
    out = []
    for x in LANTERN_X:
        best = min(pts_front, key=lambda p: abs(p[0] - x))
        out.append((x, best[1] + 18))
    return out


def _spill(c, k, t):
    """Warm light flooding out of the shop onto the lane (and toward camera)."""
    if k <= 0:
        return
    dl, dt, dr, db = DOOR_RECT
    l, t0, r, b = OPENING
    fl = 1 + 0.04 * math.sin(t * 9) + 0.03 * math.sin(t * 5.3)
    c.drawPath(poly([(l + 20, FLOOR_Y), (r - 20, FLOOR_Y), (r + 520, H), (l - 520, H)]),
               K.lin_a((0, FLOOR_Y), (0, H), [("#ffc256", 0.42 * k * fl), ("#ffb02e", 0.0)]))
    c.drawPath(poly([(DOOR_RECT[0], FLOOR_Y), (DOOR_RECT[2], FLOOR_Y), (DOOR_RECT[2] + 260, H), (DOOR_RECT[0] - 260, H)]),
               K.lin_a((0, FLOOR_Y), (0, H), [("#ffe7a8", 0.45 * k * fl), ("#ffe7a8", 0.0)]))
    overlay(c, "wall_spill", lambda cc: cc.drawRect(skia.Rect.MakeWH(W, H), K.rad_a((960, 600), 950, [("#ffb02e", 0.16), ("#ff9a3a", 0.0)])),
            alpha=k * fl)


def _particles(c, t, burst_k, ambient_k, seed=3):
    rng = K.rng(seed)
    l, t0, r, b = OPENING
    # burst from the cracks
    if 0 < burst_k < 1:
        for i in range(90):
            ang = rng.uniform(-math.pi, 0.2)
            sp = rng.uniform(150, 650)
            ox, oy = rng.choice([(960, rng.uniform(t0, b)), (rng.uniform(l, r), 560), (rng.uniform(l, r), t0)])
            d = burst_k * sp
            x, y = ox + math.cos(ang) * d, oy + math.sin(ang) * d + 120 * burst_k ** 2
            a = (1 - burst_k) * rng.uniform(0.5, 1)
            col = rng.choice(["#ffe08a", "#ff9fc4", "#c8f0a0", "#ffffff"])
            sparkle(c, x, y, rng.uniform(4, 11) * (1 - burst_k * 0.5), a, col)
    if ambient_k > 0:
        for i in range(60):
            x0, y0 = rng.uniform(l - 200, r + 200), rng.uniform(t0 - 100, FLOOR_Y)
            sp = rng.uniform(8, 30)
            y = y0 - (t * sp) % 700
            if y < t0 - 220:
                y += 700
            x = x0 + 20 * math.sin(t * 0.8 + i)
            tw = 0.5 + 0.5 * math.sin(t * rng.uniform(2, 5) + i)
            col = rng.choice(["#ffe08a", "#ff9fc4", "#c8f0a0", "#ffffff"])
            if i % 3 == 0:
                sparkle(c, x, y, rng.uniform(3, 7), ambient_k * tw, col)
            else:
                c.drawCircle(x, y, rng.uniform(1.2, 2.6), fill(col, ambient_k * tw * 0.8))


def _handprint(c, k):
    if k <= 0:
        return
    a = math.sin(clamp(k) * math.pi)
    x, y = 990, 650
    def draw(cc):
        cc.drawPath(ellipse(x, y + 10, 26, 30), fill("#ffd36b", a))
        for i, (dx, ln) in enumerate(((-22, 34), (-9, 44), (5, 46), (18, 40))):
            cc.drawPath(K.limb(x + dx, y - 10, x + dx * 1.15, y - 10 - ln, 13, 11), fill("#ffd36b", a))
        cc.drawPath(K.limb(x + 24, y + 14, x + 46, y - 6, 13, 11), fill("#ffd36b", a))
    draw(c)
    bloom(c, draw, radius=30, strength=a)


# ------------------------------------------------------------------ main
def _state(unfold, fold):
    """Per-element progress 0..1. fold reverses calmly (shelves first ... cracks last)."""
    u = clamp(unfold)
    st = dict(
        leaves=[ease_out_back(seg(u, L[5], L[5] + 0.24), 1.4) for L in LEAVES],
        awning=K.ease_out_elastic(seg(u, 0.26, 0.5)) if u < 0.999 else 1.0,
        shutters=ease_in_out(seg(u, 0.36, 0.54)),
        lanterns=[ease_out_back(seg(u, 0.46 + i * 0.055, 0.52 + i * 0.055), 2.5) for i in range(5)],
        shelves=seg(u, 0.55, 0.74),
        jars=seg(u, 0.62, 0.95),
        spill=ease_in_out(seg(u, 0.3, 0.92)),
        burst=seg(u, 0.05, 0.45),
        ambient=seg(u, 0.4, 0.8),
        cracks=1.0 - seg(u, 0.25, 0.55) * 0.85,
    )
    if fold > 0:
        f = clamp(fold)
        k = lambda a, b: 1 - ease_in_out(seg(f, a, b))  # noqa: E731
        st["jars"] = min(st["jars"], k(0.0, 0.25))
        st["shelves"] = min(st["shelves"], k(0.12, 0.35))
        st["lanterns"] = [min(v, k(0.18 + i * 0.03, 0.4 + i * 0.03)) for i, v in enumerate(st["lanterns"])]
        st["shutters"] = min(st["shutters"], k(0.35, 0.55))
        st["awning"] = min(st["awning"], k(0.45, 0.65))
        st["leaves"] = [min(v, k(0.55 + i * 0.04, 0.85 + i * 0.03)) for i, v in enumerate(st["leaves"])]
        st["spill"] = min(st["spill"], k(0.2, 0.85))
        st["ambient"] = min(st["ambient"], k(0.0, 0.7))
        st["cracks"] = (1 - seg(f, 0.85, 1.0)) * max(st["cracks"], 0.6 * seg(f, 0.5, 0.85))
        st["burst"] = 0.0
        st["fold"] = True
    return st


def draw_wall(cv, t, time="night", glow=0.0, unfold=0.0, flicker=0.0, fold=0.0, handprint=0.0, cam=None):
    apply_cam(cv, cam)
    zoom = cam[2] if cam else 1.0
    bg = _bg(time, 1.0 if zoom <= 1.1 else 2.0)
    cv.drawImageRect(bg, skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.FilterMode.kLinear))
    opened = unfold > 0.001 and not (fold >= 0.999)
    if flicker > 0 and not opened:
        _draw_flicker(cv, t, flicker, time)
    elif opened:
        _draw_open(cv, t, unfold, fold, time)
    elif glow > 0:
        def g(c):
            _draw_cracks(c, glow, width=5)
        _draw_cracks(cv, glow)
        bloom(cv, g, radius=26, strength=1.0)
        overlay(cv, "wall_glowpool", lambda cc: cc.drawCircle(960, 560, 520, K.rad_a((960, 560), 520, [("saffron", 0.18), ("saffron", 0)])), alpha=glow)
        _particles(cv, t, 0, 0.35 * glow)
    _handprint(cv, handprint)
    cv.restore()


def _draw_open(cv, t, unfold, fold, time):
    st = _state(unfold, fold)
    l, t0, r, b = OPENING
    open_any = max(st["leaves"]) > 0.0
    if open_any:
        cv.drawImage(_recess(), 0, 0)
        if time == "dawn" or st.get("fold"):
            cv.drawRect(skia.Rect.MakeLTRB(l, t0, r, b), fill("#2a1430", 0.25 * (1 - st["spill"])))
    _shutters(cv, st["shutters"], time)
    _shelves(cv, st["shelves"], st["jars"], t)
    # leaves (lower ones first so upper overlap reads cleanly)
    for i in (2, 3, 0, 1):
        _draw_leaf(cv, LEAVES[i], OPEN_ANG * st["leaves"][i], time)
    if st["cracks"] > 0.02 and max(st["leaves"]) < 0.98:
        _draw_cracks(cv, 1.0, alpha=st["cracks"])
    pts_front = _awning(cv, st["awning"], t)
    hooks = _lantern_hooks(pts_front) if pts_front else [(x, t0 + 140) for x in LANTERN_X]
    for i, (hx, hy) in enumerate(hooks):
        lk = st["lanterns"][i]
        if st["awning"] > 0.3 and lk > 0 or (st.get("fold") and st["awning"] > 0.3):
            lantern(cv, hx, hy, s=1.0, lit=clamp(lk), t=t, seed=i)
    _spill(cv, st["spill"], t)

    def glows(c):
        if st["cracks"] > 0.02 and max(st["leaves"]) < 0.98:
            _draw_cracks(c, 1.0, alpha=st["cracks"], width=6)
        dl, dt, dr, db = DOOR_RECT
        if open_any:
            c.drawRect(skia.Rect.MakeLTRB(dl + 20, dt + 40, dr - 20, db), fill("#ffb02e", 0.3 * st["spill"]))
        for i, (hx, hy) in enumerate(hooks):
            lk = clamp(st["lanterns"][i])
            if lk > 0 and st["awning"] > 0.3:
                c.drawCircle(hx, hy + 54, 26, fill("#ffcf6e", lk))
        if st["shelves"] > 0.5:
            for s in SLOTS:
                jk = clamp((st["jars"] - s["order"] * 0.6) / 0.4)
                if jk > 0:
                    jar_glow(c, s["x"], s["y"], s["w"], s["h"], s["col"], jk)
    bloom(cv, glows, radius=30, strength=0.8)
    _particles(cv, t, st["burst"], st["ambient"])


def _draw_flicker(cv, t, k, time):
    """The dying-bulb version: ghostly, stuttering, broken."""
    def stut(i, rate=1.0):
        n = K.noise1(t * 7 * rate + i * 3.1, 17)
        n2 = K.noise1(t * 23 * rate + i, 5)
        on = 1.0 if n > -0.35 else 0.25
        return clamp(on * (0.6 + 0.4 * n2)) * k
    master = 0.35 + 0.65 * stut(99, 0.6) / max(k, 1e-3) * k
    master *= k
    st = [stut(i) for i in range(len(CRACKS))]
    l, t0, r, b = OPENING
    # a ghost of the recess, barely there
    p = skia.Paint(); p.setAlphaf(0.4 * master)
    p.setColorFilter(K.matrix_filter(K.light_matrix("dim", 1.0)))
    cv.saveLayer(None, p)
    cv.drawImage(_recess(), 0, 0)
    cv.restore()
    _draw_cracks(cv, 0.85, alpha=0.9, stutter=st, width=2.4)
    _awning(cv, 0.75, t, partial=0.48, ragged=True, alpha=0.55 * master)
    hx, hy = 700, t0 + 120
    lantern(cv, hx, hy, s=0.95, lit=0.45 * master, t=t, seed=7)
    def g(c):
        _draw_cracks(c, 0.85, alpha=0.8, stutter=st, width=5)
        c.drawCircle(hx, hy + 52, 18, fill("#ffcf6e", 0.5 * master))
    bloom(cv, g, radius=22, strength=0.8)
    _particles(cv, t, 0, 0.15 * k, seed=9)
