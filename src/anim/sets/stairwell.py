"""The haveli's narrow old staircase (inside Nani's house), seen from the side.

draw_stairwell(cv, t, light='moon'|'torch', torch=None, dust=True)
  Steps descend from the roof-door landing (top-left) to the street-door landing (bottom-right).
  light='moon': moonlight pours through a carved stone jali screen (upper right) and lays a lacy
  pattern across the steps; dust motes drift in the shaft.
  light='torch': the stairwell is near-black except a warm torch cone. torch=(x, y, ang_deg)
  gives the torch head position and beam direction (0 = pointing right, 90 = straight down).
  Draw characters AFTER calling this; for torch mode call draw_torch_light(cv, t, torch) after the
  characters too if you want the light to fall on them (it darkens everything outside the cone).

STEPS     list of (x, y) foot positions on each tread, top -> bottom (13 entries; [0] = top landing,
          [-1] = bottom landing).
CHAR_S    suggested character scale on the stairs (1.15).
ROOF_DOOR (x, y)  feet position in the roof doorway at the top.
STREET_DOOR (x, y) feet position at the street door, bottom.
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import W, H, fill, stroke, smooth_path, poly, ellipse, lerp, clamp
from . import town as T

LINE = "#2a1810"
TOP = (230, 360)          # top landing front-edge point
RISE, RUN, N = 46, 92, 11
STEPS = [(160, TOP[1])] + [(TOP[0] + RUN * (i + 0.5), TOP[1] + RISE * (i + 1)) for i in range(N)] + \
        [(TOP[0] + RUN * N + 140, TOP[1] + RISE * N)]
CHAR_S = 1.15
ROOF_DOOR = (150, TOP[1])
STREET_DOOR = (STEPS[-1][0] + 150, STEPS[-1][1])
JALI = (1330, 150, 260, 300)   # x, y, w, h of the jali screen on the back wall


def _stairs_path():
    p = skia.Path()
    p.moveTo(-20, TOP[1])
    p.lineTo(TOP[0], TOP[1])
    x, y = TOP
    for i in range(N):
        p.lineTo(x, y + RISE)
        x += RUN
        y += RISE
        p.lineTo(x, y)
    p.lineTo(W + 20, y)
    p.lineTo(W + 20, H + 20)
    p.lineTo(-20, H + 20)
    p.close()
    return p


def _jali_pattern(cv, x, y, w, h, col, a=1.0, scale=1.0):
    """Carved lattice: grid of quatrefoils (used for the screen and for its light pattern)."""
    cell = 34 * scale
    nx, ny = int(w / cell), int(h / cell)
    for i in range(nx):
        for j in range(ny):
            cx, cy = x + (i + 0.5) * cell, y + (j + 0.5) * cell
            r = cell * 0.2
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                cv.drawCircle(cx + dx, cy + dy, r * 0.95, fill(col, a))


@lru_cache(maxsize=4)
def _static(light):
    def paint(cv):
        # back wall
        cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#d8c2a0", "#c9ae88", "#b39472"]))
        rng = K.rng(61)
        for _ in range(26):
            cv.drawOval(skia.Rect.MakeXYWH(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 120), rng.uniform(10, 30)),
                        fill("#a88a66", 0.25))
        for _ in range(4):
            px, py = rng.uniform(300, 1700), rng.uniform(80, 700)
            cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px, py, 70, 34), 12, 12), doAntiAlias=True)
            for r_ in range(6):
                for c_ in range(7):
                    cv.drawRect(skia.Rect.MakeXYWH(px + c_ * 12 - (r_ % 2) * 6, py + r_ * 7, 10, 5), fill("brick", 0.7))
            cv.restore()
        # niche with an old diya
        niche = T.window_path(760, 300, 70, 100)
        cv.drawPath(niche, fill("#8a6a4a")); cv.drawPath(niche, stroke(LINE, 2.4))
        cv.drawPath(ellipse(795, 392, 18, 6), fill("#b4613f")); cv.drawPath(ellipse(795, 392, 18, 6), stroke(LINE, 1.6))
        # framed photo (shapes only)
        cv.drawRect(skia.Rect.MakeXYWH(1010, 260, 110, 140), fill("#5a3a2a"))
        cv.drawRect(skia.Rect.MakeXYWH(1022, 272, 86, 116), fill("#c9b48c"))
        cv.drawCircle(1065, 312, 18, fill("#8a6a4a")); cv.drawPath(ellipse(1065, 372, 30, 22), fill("#8a6a4a"))
        cv.drawRect(skia.Rect.MakeXYWH(1010, 260, 110, 140), stroke(LINE, 2.4))
        cv.drawPath(poly([(1065, 230), (1010, 262), (1120, 262)], close=False), stroke(LINE, 1.4))
        # jali screen
        jx, jy, jw, jh = JALI
        frame = T.window_path(jx - 18, jy - 18, jw + 36, jh + 36)
        cv.drawPath(frame, fill("#e6d6b8")); cv.drawPath(frame, stroke(LINE, 2.6))
        jp = T.window_path(jx, jy, jw, jh)
        cv.save(); cv.clipPath(jp, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(jx, jy, jw, jh), fill("#d9c7a4"))
        _jali_pattern(cv, jx, jy, jw, jh, "#1a2050" if light == "moon" else "#140f12")
        cv.restore()
        cv.drawPath(jp, stroke(LINE, 2.2))
        # roof door (top-left) and street door (bottom-right)
        rd = T.window_path(40, TOP[1] - 250, 150, 250)
        cv.drawPath(rd, fill("#1a1e44" if light == "moon" else "#0a0a12"))
        cv.drawPath(rd, stroke(LINE, 3))
        if light == "moon":
            K.stars(cv, 190, TOP[1], 0, n=12, seed=4, top=TOP[1] - 220, bottom=TOP[1] - 80)
        sx = STEPS[-1][0] + 80
        sd = T.window_path(sx, STEPS[-1][1] - 280, 170, 280)
        cv.drawPath(sd, fill("#6e4226")); cv.drawPath(sd, stroke(LINE, 3))
        for yy in range(int(STEPS[-1][1]) - 220, int(STEPS[-1][1]), 46):
            cv.drawLine(sx, yy, sx + 170, yy, stroke("#4e2c18", 2))
        cv.drawCircle(sx + 140, STEPS[-1][1] - 130, 6, fill("brass"))
        # stairs mass + treads
        st = _stairs_path()
        cv.drawPath(st, K.lin((0, TOP[1]), (0, H), ["#a88866", "#8a6a4c", "#6a4e38"]))
        x, y = TOP
        for i in range(N):
            cv.drawRect(skia.Rect.MakeLTRB(x - 2, y + RISE - 6, x + RUN + 6, y + RISE + 4), fill("#c9ad86"))  # tread lip
            cv.drawLine(x, y, x, y + RISE, stroke(LINE, 2.2))
            cv.drawLine(x - 2, y + RISE - 6, x + RUN + 6, y + RISE - 6, stroke(LINE, 1.8))
            x += RUN; y += RISE
        cv.drawRect(skia.Rect.MakeLTRB(-20, TOP[1] - 6, TOP[0] + 6, TOP[1] + 4), fill("#c9ad86"))
        cv.drawRect(skia.Rect.MakeLTRB(x - 2, y - 6, W + 20, y + 4), fill("#c9ad86"))
        cv.drawPath(st, stroke(LINE, 2.6))
        # stone blocks on the stair's side wall
        cv.save(); cv.clipPath(st, doAntiAlias=True)
        for j in range(12):
            for i in range(24):
                bx = i * 90 - (j % 2) * 45
                by = TOP[1] + 60 + j * 52
                cv.drawRect(skia.Rect.MakeXYWH(bx, by, 86, 48), stroke("#5a402c", 1.4, 0.5))
        cv.restore()
        # thin iron rail along the stair
        rail_pts = [(TOP[0] - 40, TOP[1] - 150)] + [(TOP[0] + RUN * (i + 0.5), TOP[1] + RISE * (i + 1) - 150) for i in range(0, N, 2)]
        cv.drawPath(smooth_path(rail_pts, close=False), stroke("#2a2a30", 5))
        for i in range(0, N, 2):
            bx, by = TOP[0] + RUN * (i + 0.5), TOP[1] + RISE * (i + 1)
            cv.drawLine(bx, by - 150, bx, by, stroke("#2a2a30", 3))

        if light == "moon":
            # cool night grade
            g = fill("#0c1030", 0.55)
            g.setBlendMode(skia.BlendMode.kMultiply)
            cv.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 0), (0, H), [("#141a4c", 0.6), ("#080a26", 0.74)]))
            # moon shaft from the jali, falling down-left across wall and steps
            shaft = poly([(jx, jy), (jx + jw, jy + 40), (jx + jw - 200, H + 60), (jx - 700, H + 60)])
            p = K.lin_a((jx, jy), (jx - 400, H), [("#b8c6ff", 0.32), ("#b8c6ff", 0.08)])
            p.setBlendMode(skia.BlendMode.kPlus)
            cv.drawPath(shaft, p)
            # lacy light pattern projected onto the steps (skewed lattice)
            cv.save()
            cv.clipPath(shaft, doAntiAlias=True)
            cv.clipPath(st, doAntiAlias=True)
            m = skia.Matrix()
            m.setAll(1.25, -0.9, 0, 0, 0.9, 0, 0, 0, 1)
            cv.translate(jx - 520, TOP[1] + 250)
            cv.concat(m)
            pat = skia.Paint(); pat.setBlendMode(skia.BlendMode.kPlus)
            cv.saveLayer(None, pat)
            _jali_pattern(cv, 0, 0, 900, 600, "#c9d4ff", 0.12, scale=0.9)
            cv.restore()
            cv.restore()
            # glow at the screen itself
            cv.drawRect(skia.Rect.MakeXYWH(jx - 60, jy - 60, jw + 120, jh + 120),
                        K.rad_a((jx + jw / 2, jy + jh / 2), jw, [("#c9d4ff", 0.25), ("#c9d4ff", 0)]))
        else:
            cv.drawRect(skia.Rect.MakeWH(W, H), fill("#06050a", 0.25))
    return K.render_to_image(W, H, paint)


def _cone(x, y, ang, length=1100, spread=26):
    a0, a1 = math.radians(ang - spread), math.radians(ang + spread)
    p = skia.Path()
    p.moveTo(x, y)
    for k in range(13):
        a = lerp(a0, a1, k / 12)
        p.lineTo(x + math.cos(a) * length, y + math.sin(a) * length)
    p.close()
    return p


def draw_torch_light(cv, t, torch):
    """Darkness everywhere except the torch cone (call after drawing characters)."""
    x, y, ang = torch
    jit = math.sin(t * 9) * 0.6
    cv.save(); cv.resetMatrix()
    cv.saveLayer(None, skia.Paint())
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#04030a", 0.8))
    # soft-edged cut: nested cones, each removing a bit more darkness
    for spread, a in ((38, 0.17), (31, 0.2), (24, 0.24), (17, 0.28), (11, 0.3)):
        cut = K.rad_a((x, y), 1150, [("#000000", a), ("#000000", a * 0.8), ("#000000", 0.0)], [0, 0.55, 1])
        cut.setBlendMode(skia.BlendMode.kDstOut)
        cv.drawPath(_cone(x, y, ang + jit, 1150, spread), cut)
    hal = K.rad_a((x, y), 380, [("#000000", 0.75), ("#000000", 0.35), ("#000000", 0)], [0, 0.5, 1])
    hal.setBlendMode(skia.BlendMode.kDstOut)
    cv.drawCircle(x, y, 380, hal)
    cv.restore()
    for spread, a in ((26, 0.16),):
        warm = K.rad_a((x, y), 1000, [("#ffcf85", a), ("#ffb35a", a * 0.4), ("#ffb35a", 0)], [0, 0.4, 1])
        warm.setBlendMode(skia.BlendMode.kPlus)
        cv.drawPath(_cone(x, y, ang + jit, 1000, spread), warm)
    cv.drawCircle(x, y, 18, K.rad_a((x, y), 18, [("#fff6d8", 0.95), ("#ffd27a", 0)]))
    cv.restore()


def draw_stairwell(cv, t, light="moon", torch=None, dust=True):
    cv.drawImage(_static("moon" if light == "moon" else "torch"), 0, 0)
    if light == "moon" and dust:
        jx, jy, jw, jh = JALI
        rng = K.rng(71)
        for i in range(40):
            u = rng.random()
            sx = lerp(jx + jw * 0.5, jx - 300, u) + rng.uniform(-120, 120)
            sy = lerp(jy + jh * 0.5, H - 100, u) + math.sin(t * 0.5 + i) * 20 - (t * 6 + i * 13) % 60
            a = 0.25 + 0.35 * math.sin(t * rng.uniform(0.5, 1.5) + i)
            cv.drawCircle(sx, sy, rng.uniform(1.2, 2.6), fill("#e8eeff", clamp(a)))
