"""Chandpur skyline panorama + shared architecture helpers for the other sets.

draw_town(cv, t, time='dusk'|'night'|'dawn'|'day', lights=1.0, powercut_u=None, heat=0.0, cam_x=0.0)
  World is WW=2600 px wide at the nearest layer; cam_x in [0, WW-1920] pans with parallax:
  sky (static), far (0.25), mid (0.55), near (1.0).
  lights      0..1 brightness of lit windows (warm glow).
  powercut_u  None = windows as `lights` says; 0..1 = wave of windows switching off left->right
              (each window has its own staggered switch-off moment; u=1 -> all dark).
  heat        0..1 heat-shimmer bands over the lower town.
CLOCK_TOWER   (x, y) screen position of the clock face centre at cam_x=0;
clock_tower_pos(cam_x) gives it for any pan.

Shared helpers used by rooftop/aerial/day: SKY, sky_gradient(), draw_moon(), haveli(), water_tank(),
power_pole(), wire(), kite(), laundry(), TIME_LIGHT.
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import W, H, fill, stroke, smooth_path, poly, ellipse, lerp, clamp

WW = 2600
PAR = {"far": 0.25, "mid": 0.55, "near": 1.0}

SKY = {
    "night": ["#060821", "#10163f", "#1f2862", "#34407c"],
    "night_dim": ["#04051a", "#0b1033", "#161d4e", "#252e66"],
    "dusk": ["#2e2f62", "#8a5a78", "#e08a5c", "#ffcf8a"],
    "evening": ["#2e2f62", "#8a5a78", "#e08a5c", "#ffcf8a"],
    "dawn": ["#34477f", "#9a86b6", "#f2a6a0", "#ffdca6"],
    "day": ["#cfd9d8", "#e8e2cc", "#f3e6c6", "#f8eed5"],
    "morning": ["#a9c6d6", "#dfe2d4", "#f6e7c8", "#fbefd6"],
}
HAZE = {"night": "#2a3470", "night_dim": "#1b2356", "dusk": "#e49a72", "evening": "#e49a72", "dawn": "#e6a7a8",
        "day": "#efe3c8", "morning": "#e9e4d2"}
TIME_LIGHT = {"night": "night", "night_dim": "night", "dusk": "dusk", "evening": "dusk", "dawn": "dawn",
              "day": "day", "morning": "day"}
WIN_DARK = "#2b1d22"
WIN_LIT = "#ffc46b"


# ------------------------------------------------------------------ sky
def sky_gradient(cv, time, w=W, h=H, horizon=0.62):
    cols = SKY[time]
    cv.drawRect(skia.Rect.MakeWH(w, h), K.lin((0, 0), (0, h * horizon + 80), cols, [0, 0.38, 0.75, 1]))


def draw_moon(cv, x, y, r=46, glow=1.0):
    cv.drawCircle(x, y, r * 6, K.rad_a((x, y), r * 6, [("moonglow", 0.28 * glow), ("moonglow", 0.08 * glow),
                                                      ("moonglow", 0)], [0, 0.35, 1]))
    cv.drawCircle(x, y, r * 1.7, K.rad_a((x, y), r * 1.7, [("moon", 0.5 * glow), ("moon", 0)]))
    cv.drawCircle(x, y, r, K.rad((x - r * 0.3, y - r * 0.3), r * 1.3, ["#fffbea", "moon", "#e3d8b4"]))
    for (dx, dy, rr) in [(-12, 8, 9), (14, -10, 6), (8, 16, 5), (-18, -14, 4)]:
        cv.drawCircle(x + dx * r / 46, y + dy * r / 46, rr * r / 46, fill("#d9cca4", 0.45))


def draw_sun(cv, x, y, r, col="#fff0c0", glow="#ffb36b"):
    cv.drawCircle(x, y, r * 5, K.rad_a((x, y), r * 5, [(glow, 0.45), (glow, 0)]))
    cv.drawCircle(x, y, r, K.rad((x, y), r, ["#fffbe8", col]))


def clouds(cv, rng, w, y0, y1, col, a=0.25, n=6):
    for _ in range(n):
        cx, cy = rng.uniform(0, w), rng.uniform(y0, y1)
        L = rng.uniform(180, 420)
        for k in range(5):
            cv.drawOval(skia.Rect.MakeXYWH(cx + k * L / 5 - L / 2, cy - 8 + rng.uniform(-6, 6), L / 2.2, 16 + rng.uniform(0, 10)),
                        fill(col, a * rng.uniform(0.5, 1)))


# ------------------------------------------------------------------ architecture helpers
PLASTER = ["#e7d3ad", "#e9c79a", "#d9b48a", "#efe0c2", "#e4c0a0", "#d8c2a6", "#c9a888", "#e8cfb8", "#dcc49c"]
ACCENT = ["#5f8fb7", "#8c5a3c", "#3d78b8", "#a3553a", "#7a9a6a", "#c46a4a"]


def arched_window(cv, x, y, w, h, frame="#6b4630", lw=1.6, grille=True, dark=WIN_DARK):
    p = skia.Path()
    p.moveTo(x, y + h); p.lineTo(x, y + w / 2)
    p.arcTo(skia.Rect.MakeXYWH(x, y, w, w), 180, 180, False)
    p.lineTo(x + w, y + h); p.close()
    cv.drawPath(p, fill(dark))
    if grille:
        for i in range(1, 3):
            cv.drawLine(x + w * i / 3, y + w / 3, x + w * i / 3, y + h, stroke(frame, lw * 0.7, 0.8))
        cv.drawLine(x, y + h * 0.6, x + w, y + h * 0.6, stroke(frame, lw * 0.7, 0.8))
    cv.drawPath(p, stroke(frame, lw))
    return skia.Rect.MakeXYWH(x, y, w, h)


def window_path(x, y, w, h):
    p = skia.Path()
    p.moveTo(x, y + h); p.lineTo(x, y + w / 2)
    p.arcTo(skia.Rect.MakeXYWH(x, y, w, w), 180, 180, False)
    p.lineTo(x + w, y + h); p.close()
    return p


def jharokha(cv, cx, by, w, h, col, line="#3a2418", lw=2.0):
    """Carved projecting balcony: base with brackets, pillared box, curved roof."""
    wood = K.shade(col, -0.25)
    # brackets
    for i in range(3):
        bx = cx - w / 2 + 8 + i * (w - 16) / 2
        cv.drawPath(poly([(bx - 5, by), (bx + 5, by), (bx, by + 16)]), fill(wood))
    base = skia.Rect.MakeLTRB(cx - w / 2 - 6, by - 8, cx + w / 2 + 6, by + 2)
    cv.drawRect(base, fill(K.shade(col, -0.1)))
    cv.drawRect(base, stroke(line, lw * 0.8))
    box = skia.Rect.MakeLTRB(cx - w / 2, by - h, cx + w / 2, by - 8)
    cv.drawRect(box, fill(WIN_DARK))
    # carved panel low
    cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2, by - h * 0.38, cx + w / 2, by - 8), fill(col))
    for i in range(5):
        x = cx - w / 2 + (i + 0.5) * w / 5
        cv.drawCircle(x, by - h * 0.22, 2.4, fill(wood))
    # pillars
    for i in range(4):
        x = cx - w / 2 + i * w / 3
        cv.drawLine(x, by - h, x, by - h * 0.38, stroke(col, 3.2))
    cv.drawRect(box, stroke(line, lw))
    # curved chhajja roof
    roof = smooth_path([(cx - w / 2 - 10, by - h), (cx - w / 2 + 4, by - h - 12), (cx, by - h - 18),
                        (cx + w / 2 - 4, by - h - 12), (cx + w / 2 + 10, by - h)], close=True, tension=0.4)
    cv.drawPath(roof, fill(K.shade(col, -0.05)))
    cv.drawPath(roof, stroke(line, lw))
    cv.drawCircle(cx, by - h - 20, 3, fill(K.shade(col, -0.2)))
    return skia.Rect.MakeLTRB(cx - w / 2 + 3, by - h + 2, cx + w / 2 - 3, by - h * 0.4)


def water_tank(cv, cx, by, r=22, h=34, col="#1d1d24", lw=1.8, line="#0b0b10"):
    cv.drawRect(skia.Rect.MakeLTRB(cx - r, by - h, cx + r, by), K.lin((cx - r, 0), (cx + r, 0), ["#2a2a33", "#3d3d48", col]))
    cv.drawOval(skia.Rect.MakeLTRB(cx - r, by - h - r * 0.35, cx + r, by - h + r * 0.35), fill("#33333d"))
    cv.drawOval(skia.Rect.MakeLTRB(cx - r * 0.35, by - h - r * 0.45, cx + r * 0.35, by - h - r * 0.05), fill("#24242c"))
    for k in (0.33, 0.66):
        cv.drawLine(cx - r, by - h * k, cx + r, by - h * k, stroke("#4a4a56", 1.2))
    p = skia.Path(); p.addRect(skia.Rect.MakeLTRB(cx - r, by - h, cx + r, by))
    cv.drawPath(p, stroke(line, lw))


def chhatri(cv, cx, by, w, col, line="#3a2418", lw=1.6):
    """Small domed rooftop pavilion."""
    for i in range(3):
        x = cx - w / 2 + i * w / 2
        cv.drawLine(x, by, x, by - w * 0.7, stroke(col, 3))
    cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2 - 4, by - w * 0.78, cx + w / 2 + 4, by - w * 0.68), fill(col))
    dome = smooth_path([(cx - w / 2, by - w * 0.78), (cx - w * 0.4, by - w * 1.15), (cx, by - w * 1.3),
                        (cx + w * 0.4, by - w * 1.15), (cx + w / 2, by - w * 0.78)], tension=0.5)
    cv.drawPath(dome, fill(K.shade(col, 0.05)))
    cv.drawPath(dome, stroke(line, lw))
    cv.drawLine(cx, by - w * 1.3, cx, by - w * 1.45, stroke(line, lw))


def haveli(cv, x, by, w, h, rng, col=None, detail=1.0, wins=None, lw=2.0, line="#3a2418", tank=None,
           roof="parapet"):
    """An old town house front. Appends lit-able window rects to `wins`."""
    col = col or rng.choice(PLASTER)
    body = skia.Rect.MakeLTRB(x, by - h, x + w, by)
    cv.drawRect(body, K.lin((0, by - h), (0, by), [K.shade(col, 0.06), col, K.shade(col, -0.12)]))
    # plaster patches + brick peeking
    if detail > 0.4:
        for _ in range(int(3 * detail)):
            px, py = rng.uniform(x + 6, x + w - 30), rng.uniform(by - h + 20, by - 20)
            cv.drawOval(skia.Rect.MakeXYWH(px, py, rng.uniform(16, 40), rng.uniform(8, 20)), fill(K.shade(col, -0.08), 0.5))
        for _ in range(int(2 * detail)):
            px, py = rng.uniform(x + 8, x + w - 40), rng.uniform(by - h + 30, by - 30)
            cv.save()
            cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px, py, 34, 20), 8, 8), doAntiAlias=True)
            for r_ in range(4):
                for c_ in range(4):
                    cv.drawRect(skia.Rect.MakeXYWH(px + c_ * 11 - (r_ % 2) * 5, py + r_ * 6, 9, 4), fill("brick", 0.8))
            cv.restore()
    floors = max(1, int(h / 85))
    fh = h / floors
    jfloor = rng.randrange(floors) if (floors > 1 and detail > 0.5 and w > 90) else -1
    for f in range(floors):
        fy = by - h + f * fh
        # ledge
        if f > 0:
            cv.drawRect(skia.Rect.MakeLTRB(x - 3, fy - 3, x + w + 3, fy + 3), fill(K.shade(col, -0.18)))
        nwin = max(1, int(w / 62))
        ww = min(24, w / nwin * 0.42)
        wh = min(fh * 0.55, ww * 1.8)
        if f == jfloor:
            r = jharokha(cv, x + w / 2, fy + fh * 0.88, min(w * 0.5, 80), fh * 0.72, col, line, lw)
            if wins is not None:
                wins.append(r)
            continue
        for i in range(nwin):
            wx = x + (i + 0.5) * w / nwin - ww / 2
            wy = fy + fh * 0.3
            if f == floors - 1 and i == nwin // 2 and detail > 0.6 and w > 70:
                # ground-floor door
                dr = skia.Rect.MakeXYWH(x + w / 2 - ww * 0.8, by - fh * 0.62, ww * 1.6, fh * 0.62)
                cv.drawRect(dr, fill(rng.choice(ACCENT)))
                cv.drawRect(dr, stroke(line, lw))
                cv.drawLine(dr.centerX(), dr.top(), dr.centerX(), dr.bottom(), stroke(line, lw * 0.7))
                continue
            r = arched_window(cv, wx, wy, ww, wh, frame=K.shade(col, -0.45), lw=lw * 0.8, grille=detail > 0.5)
            if wins is not None:
                wins.append(r)
            if detail > 0.6 and rng.random() < 0.3:
                # shutters
                cv.drawRect(skia.Rect.MakeXYWH(wx - ww * 0.42, wy + ww * 0.3, ww * 0.38, wh - ww * 0.3), fill(rng.choice(ACCENT)))
    # roofline
    if roof == "parapet":
        cv.drawRect(skia.Rect.MakeLTRB(x - 4, by - h - 10, x + w + 4, by - h), fill(K.shade(col, -0.06)))
        n = int(w / 18)
        for i in range(n):
            cx = x + (i + 0.5) * w / n
            cv.drawPath(ellipse(cx, by - h - 10, w / n * 0.32, 5), fill(K.shade(col, -0.06)))
    elif roof == "flat":
        cv.drawRect(skia.Rect.MakeLTRB(x - 3, by - h - 6, x + w + 3, by - h), fill(K.shade(col, -0.1)))
    cv.drawRect(body, stroke(line, lw))
    if tank:
        water_tank(cv, x + w * tank, by - h - 6, r=w * 0.08 + 8, h=w * 0.1 + 14, lw=lw * 0.8)


def laundry(cv, x0, y0, x1, y1, rng, t=0.0, sag=18, lw=1.4, line="#3a2418", n=5):
    path = skia.Path(); path.moveTo(x0, y0); path.quadTo((x0 + x1) / 2, (y0 + y1) / 2 + sag * 2, x1, y1)
    cv.drawPath(path, stroke(line, lw))
    cols = ["#d8333d", "#f2c94c", "#3a6fd8", "#f5f0e6", "#7a9a6a", "#e37f6a", "#8e6cc9"]
    for i in range(n):
        u = (i + 0.7) / (n + 0.6)
        x = lerp(x0, x1, u)
        y = lerp(y0, y1, u) + sag * 2 * 2 * u * (1 - u)
        cw, ch = rng.uniform(16, 30), rng.uniform(20, 38)
        sw = math.sin(t * 1.3 + i) * 2
        cl = smooth_path([(x - cw / 2, y), (x + cw / 2, y), (x + cw / 2 + sw, y + ch), (x - cw / 2 + sw, y + ch)], tension=0.15)
        cv.drawPath(cl, fill(rng.choice(cols)))
        cv.drawPath(cl, stroke(line, lw * 0.8, 0.7))


def wire(cv, x0, y0, x1, y1, sag=30, col="#15121a", w=1.6, a=1.0):
    p = skia.Path(); p.moveTo(x0, y0); p.quadTo((x0 + x1) / 2, (y0 + y1) / 2 + sag * 2, x1, y1)
    cv.drawPath(p, stroke(col, w, a))


def wire_point(x0, y0, x1, y1, sag, u):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + sag * 2
    return ((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1)


def power_pole(cv, x, by, h, col="#2a2530", lw=1.6):
    cv.drawRect(skia.Rect.MakeLTRB(x - 4, by - h, x + 4, by), fill(col))
    for k, cw in ((0, 46), (16, 34)):
        cv.drawRect(skia.Rect.MakeLTRB(x - cw / 2, by - h + 8 + k, x + cw / 2, by - h + 12 + k), fill(col))
        for dx in (-cw / 2 + 3, cw / 2 - 3):
            cv.drawCircle(x + dx, by - h + 7 + k, 2.4, fill("#cfd2d8"))
    return [(x - 20, by - h + 7), (x + 20, by - h + 7), (x - 14, by - h + 23), (x + 14, by - h + 23)]


def kite(cv, x, y, s=1.0, col="#ff6fa5", rot=12, line="#3a2418", t=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot + math.sin(t * 1.7) * 3); cv.scale(s, s)
    k = poly([(0, -26), (20, 0), (0, 30), (-20, 0)])
    cv.drawPath(k, fill(col)); cv.drawPath(k, stroke(line, 1.8))
    cv.drawPath(poly([(0, -26), (20, 0), (0, 0)]), fill(K.shade(col, 0.25)))
    cv.drawLine(0, -26, 0, 30, stroke(line, 1.2)); cv.drawLine(-20, 0, 20, 0, stroke(line, 1.2))
    tail = smooth_path([(0, 30), (8 + math.sin(t * 3) * 4, 46), (-4, 60), (6 + math.sin(t * 3 + 1) * 4, 74)], close=False)
    cv.drawPath(tail, stroke(line, 1.2))
    for i, yy in enumerate((44, 58, 72)):
        cv.drawPath(poly([(-5 + i, yy), (5 + i, yy - 4), (5 + i, yy + 4)]), fill("#ffd23f"))
    cv.restore()


def clock_tower(cv, cx, by, h=330, col="#d9b48a", line="#3a2418", lw=2.2, rng=None):
    w = 78
    body = skia.Rect.MakeLTRB(cx - w / 2, by - h, cx + w / 2, by)
    cv.drawRect(body, K.lin((cx - w / 2, 0), (cx + w / 2, 0), [K.shade(col, 0.08), col, K.shade(col, -0.18)]))
    for k in range(4):
        y = by - h + 70 + k * 60
        cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2 - 4, y, cx + w / 2 + 4, y + 6), fill(K.shade(col, -0.15)))
    arched_window(cv, cx - 10, by - h * 0.45, 20, 40, frame=K.shade(col, -0.45), lw=1.5)
    arched_window(cv, cx - 10, by - h * 0.25, 20, 40, frame=K.shade(col, -0.45), lw=1.5)
    cv.drawRect(body, stroke(line, lw))
    # clock housing + face
    fy = by - h + 34
    cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2 - 8, by - h - 8, cx + w / 2 + 8, by - h + 70), fill(K.shade(col, 0.05)))
    cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2 - 8, by - h - 8, cx + w / 2 + 8, by - h + 70), stroke(line, lw))
    cv.drawCircle(cx, fy, 28, fill("#f6efd9"))
    cv.drawCircle(cx, fy, 28, stroke(line, lw))
    for i in range(12):
        a = i * math.pi / 6
        cv.drawLine(cx + math.cos(a) * 22, fy + math.sin(a) * 22, cx + math.cos(a) * 26, fy + math.sin(a) * 26, stroke(line, 2))
    # hands at (almost) midnight
    cv.drawLine(cx, fy, cx + 1, fy - 18, stroke(line, 3.4))
    cv.drawLine(cx, fy, cx + 2, fy - 24, stroke(line, 2.2))
    cv.drawCircle(cx, fy, 3, fill(line))
    # roof: small dome + finial
    dome = smooth_path([(cx - w / 2 - 10, by - h - 8), (cx - w * 0.35, by - h - 52), (cx, by - h - 76),
                        (cx + w * 0.35, by - h - 52), (cx + w / 2 + 10, by - h - 8)], tension=0.5)
    cv.drawPath(dome, K.lin((cx - w, 0), (cx + w, 0), [K.shade(col, 0.1), K.shade(col, -0.1)]))
    cv.drawPath(dome, stroke(line, lw))
    cv.drawLine(cx, by - h - 76, cx, by - h - 100, stroke(line, lw))
    cv.drawCircle(cx, by - h - 102, 4, fill("brass"))
    return (cx, fy)


def shikhara(cv, cx, by, h=260, w=120, col="#e6c49a", line="#3a2418", lw=2.0):
    # temple base
    cv.drawRect(skia.Rect.MakeLTRB(cx - w * 0.8, by - h * 0.28, cx + w * 0.8, by), fill(K.shade(col, -0.05)))
    for i in range(5):
        x = cx - w * 0.8 + (i + 0.5) * w * 1.6 / 5
        cv.drawLine(x, by - h * 0.26, x, by, stroke(K.shade(col, -0.2), 4))
    cv.drawRect(skia.Rect.MakeLTRB(cx - w * 0.85, by - h * 0.3, cx + w * 0.85, by - h * 0.26), fill(K.shade(col, -0.15)))
    cv.drawRect(skia.Rect.MakeLTRB(cx - w * 0.8, by - h * 0.28, cx + w * 0.8, by), stroke(line, lw))
    # curvilinear tower
    top = by - h
    tw = smooth_path([(cx - w / 2, by - h * 0.28), (cx - w * 0.47, by - h * 0.62), (cx - w * 0.28, top + h * 0.14),
                      (cx, top + h * 0.06), (cx + w * 0.28, top + h * 0.14), (cx + w * 0.47, by - h * 0.62),
                      (cx + w / 2, by - h * 0.28)], tension=0.5)
    cv.drawPath(tw, K.lin((cx - w / 2, 0), (cx + w / 2, 0), [K.shade(col, 0.1), col, K.shade(col, -0.2)]))
    cv.save(); cv.clipPath(tw, doAntiAlias=True)
    for k in range(9):
        y = by - h * 0.28 - k * h * 0.08
        cv.drawLine(cx - w, y, cx + w, y, stroke(K.shade(col, -0.2), 1.6))
    cv.drawLine(cx, top, cx, by, stroke(K.shade(col, -0.15), 2))
    cv.restore()
    cv.drawPath(tw, stroke(line, lw))
    # amalaka + kalash + flag
    cv.drawOval(skia.Rect.MakeLTRB(cx - 18, top + h * 0.02, cx + 18, top + h * 0.08), fill(K.shade(col, -0.05)))
    cv.drawOval(skia.Rect.MakeLTRB(cx - 18, top + h * 0.02, cx + 18, top + h * 0.08), stroke(line, lw * 0.8))
    cv.drawPath(ellipse(cx, top - 4, 7, 9), fill("brass"))
    cv.drawLine(cx, top - 12, cx, top - 50, stroke(line, 1.6))
    cv.drawPath(poly([(cx, top - 50), (cx + 26, top - 42), (cx, top - 34)]), fill("#e8742a"))


def onion_dome(cv, cx, by, w, col="#efe6d6", line="#3a2418", lw=1.8):
    cv.drawRect(skia.Rect.MakeLTRB(cx - w * 0.45, by - w * 0.25, cx + w * 0.45, by), fill(K.shade(col, -0.08)))
    d = smooth_path([(cx - w * 0.45, by - w * 0.25), (cx - w * 0.55, by - w * 0.65), (cx - w * 0.2, by - w * 1.0),
                     (cx, by - w * 1.2), (cx + w * 0.2, by - w * 1.0), (cx + w * 0.55, by - w * 0.65),
                     (cx + w * 0.45, by - w * 0.25)], tension=0.5)
    cv.drawPath(d, K.lin((cx - w / 2, 0), (cx + w / 2, 0), [K.shade(col, 0.1), col, K.shade(col, -0.2)]))
    cv.drawPath(d, stroke(line, lw))
    cv.drawLine(cx, by - w * 1.2, cx, by - w * 1.4, stroke(line, lw))


# ------------------------------------------------------------------ town layers
def _layer_width(p):
    return int(W + (WW - W) * p) + 4


def _build_far(cv, time, wins):
    rng = K.rng(101)
    lw = _layer_width(PAR["far"])
    x = -20
    by = 650
    while x < lw:
        w = rng.uniform(60, 150)
        h = rng.uniform(60, 150)
        r = rng.random()
        haveli(cv, x, by, w, h, rng, col=rng.choice(PLASTER), detail=0.2, wins=wins, lw=0, roof="flat")
        if r < 0.12:
            onion_dome(cv, x + w / 2, by - h - 6, w * 0.4, lw=0)
        elif r < 0.2:
            cv.drawRect(skia.Rect.MakeLTRB(x + w / 2 - 5, by - h - 110, x + w / 2 + 5, by - h), fill("#d9c7a8"))
            onion_dome(cv, x + w / 2, by - h - 108, 22, lw=0)
        elif r < 0.45:
            water_tank(cv, x + rng.uniform(0.2, 0.8) * w, by - h, r=8, h=12, lw=0)
        x += w + rng.uniform(-10, 6)
    # low hills of trees
    for i in range(40):
        cx = rng.uniform(0, lw)
        cv.drawCircle(cx, by + 4, rng.uniform(20, 40), fill("#6f7a55"))
    cv.drawRect(skia.Rect.MakeLTRB(0, by, lw, H), fill("#b79d7c"))


CLOCK_LAYER_X = 1320   # clock tower x inside the mid layer image


def _build_mid(cv, time, wins):
    rng = K.rng(202)
    lw = _layer_width(PAR["mid"])
    x = -30
    by = 790
    placed_temple = False
    while x < lw:
        if abs(x - (CLOCK_LAYER_X - 60)) < 90:
            x = CLOCK_LAYER_X + 60
            continue
        if not placed_temple and x > 520:
            shikhara(cv, x + 90, by - 120, h=250, w=110)
            haveli(cv, x, by, 180, 120, rng, detail=0.6, wins=wins, lw=1.6)
            placed_temple = True
            x += 190
            continue
        w = rng.uniform(110, 210)
        h = rng.uniform(150, 290)
        haveli(cv, x, by, w, h, rng, detail=0.7, wins=wins, lw=1.6,
               tank=rng.uniform(0.2, 0.8) if rng.random() < 0.55 else None,
               roof=rng.choice(["parapet", "parapet", "flat"]))
        if rng.random() < 0.25:
            chhatri(cv, x + w * rng.uniform(0.3, 0.7), by - h - 10, 34, K.shade(rng.choice(PLASTER), -0.05), lw=1.4)
        if rng.random() < 0.3:
            laundry(cv, x + 8, by - h - 34, x + w - 10, by - h - 30, rng, sag=8, lw=1.2, n=4)
            cv.drawLine(x + 8, by - h - 34, x + 8, by - h - 8, stroke("#3a2418", 1.4))
            cv.drawLine(x + w - 10, by - h - 30, x + w - 10, by - h - 8, stroke("#3a2418", 1.4))
        x += w + rng.uniform(-6, 10)
    for i in range(9):
        tx = rng.uniform(0, lw)
        if abs(tx - CLOCK_LAYER_X) < 80:
            continue
        ty = by - rng.uniform(40, 120)
        for k in range(6):
            cv.drawCircle(tx + rng.uniform(-40, 40), ty + rng.uniform(-30, 20), rng.uniform(22, 38),
                          fill(rng.choice(["#4f6e3f", "#5d7d47", "#46643a"])))
        cv.drawRect(skia.Rect.MakeLTRB(tx - 5, ty + 10, tx + 5, by), fill("#4a3428"))
    clock_tower(cv, CLOCK_LAYER_X, by, h=380)


def _build_near(cv, time, wins, extras):
    rng = K.rng(303)
    lw = _layer_width(PAR["near"])
    x = -40
    by = 1080
    poles = []
    while x < lw:
        w = rng.uniform(220, 380)
        h = rng.uniform(170, 300)
        haveli(cv, x, by, w, h, rng, detail=1.0, wins=wins, lw=2.4,
               tank=rng.uniform(0.15, 0.85) if rng.random() < 0.6 else None, roof="parapet")
        if rng.random() < 0.35:
            laundry(cv, x + 20, by - h - 50, x + w - 30, by - h - 44, rng, sag=14, lw=1.6, n=5)
            cv.drawLine(x + 20, by - h - 50, x + 20, by - h - 10, stroke("#3a2418", 2))
            cv.drawLine(x + w - 30, by - h - 44, x + w - 30, by - h - 10, stroke("#3a2418", 2))
        if rng.random() < 0.4:
            # potted plants on the parapet
            for k in range(rng.randint(2, 4)):
                px = x + rng.uniform(20, w - 20)
                cv.drawPath(poly([(px - 9, by - h - 10), (px + 9, by - h - 10), (px + 6, by - h + 6), (px - 6, by - h + 6)]),
                            fill("#a65b3c"))
                for j in range(5):
                    a = -math.pi / 2 + (j - 2) * 0.45
                    cv.drawPath(ellipse(px + math.cos(a) * 10, by - h - 16 + math.sin(a) * 10, 5, 8), fill("#4f7d43"))
        poles.append((x + w * 0.5, by - h))
        x += w + rng.uniform(-8, 8)
    # power poles + sagging wires across
    tops = []
    for i in range(0, len(poles), 2):
        px, ty = poles[i]
        tops.append(power_pole(cv, px, ty + 10, 180))
    for a, b in zip(tops, tops[1:]):
        for k in range(4):
            wire(cv, *a[k], *b[k], sag=22 + k * 6, w=1.6)
    extras["wires"] = list(zip(tops, tops[1:]))
    # kite caught on the second span
    if len(tops) > 2:
        a, b = tops[1], tops[2]
        kx, ky = wire_point(*a[1], *b[1], 28, 0.42)
        extras["kite"] = (kx, ky)


@lru_cache(maxsize=16)
def _layers(time):
    light = TIME_LIGHT[time]
    haze = HAZE[time]
    out = {}
    for name, p in PAR.items():
        wins = []
        extras = {}
        lw_ = _layer_width(p)

        def build(cv, name=name, wins=wins, extras=extras):
            if name == "far":
                _build_far(cv, time, wins)
            elif name == "mid":
                _build_mid(cv, time, wins)
            else:
                _build_near(cv, time, wins, extras)
        rec = skia.PictureRecorder()
        rc = rec.beginRecording(skia.Rect.MakeWH(lw_, H))
        build(rc)
        pic = rec.finishRecordingAsPicture()

        def paint(cv, pic=pic, name=name):
            with K.lit(cv, light, 1.0):
                cv.drawPicture(pic)
            # atmospheric haze on drawn pixels only
            hz = {"far": 0.55, "mid": 0.25, "near": 0.0}[name]
            if time in ("night", "night_dim"):
                hz *= 0.8
            if hz:
                p_ = fill(haze, hz)
                p_.setBlendMode(skia.BlendMode.kSrcATop)
                cv.drawRect(skia.Rect.MakeWH(lw_, H), p_)
            # depth grading: nearer layers darker / more contrasty, per time of day
            grade = {
                "night": {"far": (0.10, 0.25), "mid": (0.22, 0.45), "near": (0.32, 0.62)},
                "night_dim": {"far": (0.2, 0.35), "mid": (0.32, 0.55), "near": (0.42, 0.7)},
                "dusk": {"far": (0.0, 0.0), "mid": (0.08, 0.2), "near": (0.18, 0.38)},
                "evening": {"far": (0.0, 0.0), "mid": (0.08, 0.2), "near": (0.18, 0.38)},
                "dawn": {"far": (0.0, 0.0), "mid": (0.06, 0.16), "near": (0.12, 0.3)},
            }.get(time, {}).get(name)
            if grade:
                gc = {"night": "#070a24", "night_dim": "#04061a", "dusk": "#4a2238", "evening": "#4a2238",
                      "dawn": "#4a3060"}[time]
                p_ = K.lin_a((0, 450), (0, 1080), [(gc, grade[0]), (gc, grade[1])])
                p_.setBlendMode(skia.BlendMode.kSrcATop)
                cv.drawRect(skia.Rect.MakeWH(lw_, H), p_)
            if name == "near" and time in ("night", "night_dim", "dawn"):
                # moon rim on rooftop edges: subtle top-light gradient
                p_ = K.lin_a((0, 760), (0, 1080), [("#9fb3ff", 0.10), ("#9fb3ff", 0.0)])
                p_.setBlendMode(skia.BlendMode.kSrcATop)
                cv.drawRect(skia.Rect.MakeWH(lw_, H), p_)
        img = K.render_to_image(lw_, H, paint)
        # lit-window overlay image
        def paint_lit(cv, wins=wins, name=name):
            for r in wins:
                pad = 14 if name == "near" else 8
                cv.drawRect(r.makeOutset(pad, pad), K.rad_a((r.centerX(), r.centerY()), max(r.width(), r.height()) + pad,
                                                             [(WIN_LIT, 0.45), (WIN_LIT, 0)]))
                cv.drawRect(r, K.lin((0, r.top()), (0, r.bottom()), ["#ffe2a0", WIN_LIT, "#e8913a"]))
        lit_img = K.render_to_image(lw_, H, paint_lit)
        r = K.rng(7 + int(p * 100))
        thresholds = []
        for w_ in wins:
            xw = w_.centerX() / lw_
            thresholds.append(clamp(0.05 + xw * 0.8 + r.uniform(-0.06, 0.1), 0.02, 0.98))
        on = [r.random() < (0.55 if name != "far" else 0.4) for _ in wins]
        out[name] = (img, lit_img, wins, thresholds, on, extras)
    return out


@lru_cache(maxsize=8)
def _sky(time):
    def paint(cv):
        sky_gradient(cv, time, W, H, horizon=0.66)
        rng = K.rng(55)
        if time in ("night", "night_dim"):
            draw_moon(cv, 1500, 190, 52, glow=1.0 if time == "night" else 0.7)
            clouds(cv, rng, W, 120, 420, "#4a5592", a=0.18, n=5)
        elif time in ("dusk", "evening"):
            draw_sun(cv, 380, 600, 60, col="#ffd9a0", glow="#ff9a5a")
            clouds(cv, rng, W, 150, 480, "#f6b48a", a=0.35, n=7)
        elif time == "dawn":
            draw_sun(cv, 1450, 690, 70, col="#fff1cf", glow="#ffb09a")
            clouds(cv, rng, W, 180, 500, "#ffd0c0", a=0.35, n=7)
            draw_moon(cv, 420, 180, 30, glow=0.35)
        else:
            clouds(cv, rng, W, 150, 420, "#ffffff", a=0.3, n=5)
            cv.drawCircle(1600, 120, 400, K.rad_a((1600, 120), 400, [("#fffbe8", 0.5), ("#fffbe8", 0)]))
    return K.render_to_image(W, H, paint)


def clock_tower_pos(cam_x=0.0):
    p = PAR["mid"]
    return (CLOCK_LAYER_X - cam_x * p, 790 - 380 + 34)


CLOCK_TOWER = clock_tower_pos(0.0)


def draw_town(cv, t, time="dusk", lights=1.0, powercut_u=None, heat=0.0, cam_x=0.0, y_offset=0.0, skip_near=False,
              sky=True):
    """Draw the panorama. y_offset shifts all town layers (not the sky) down (e.g. to sit behind a parapet)."""
    cam_x = clamp(cam_x, 0, WW - W)
    if sky:
        cv.drawImage(_sky(time), 0, 0)
        if time in ("night", "night_dim"):
            K.stars(cv, W, H, t, n=240, seed=7, bottom=620, alpha=1.0 if time == "night" else 0.7)
        elif time == "dawn":
            K.stars(cv, W, H, t, n=60, seed=7, bottom=300, alpha=0.35)
        elif time in ("dusk", "evening"):
            K.stars(cv, W, H, t, n=25, seed=9, bottom=250, alpha=0.4)
    layers = _layers(time)
    order = ["far", "mid"] + ([] if skip_near else ["near"])
    for name in order:
        img, lit_img, wins, thr, on, extras = layers[name]
        p = PAR[name]
        ox = -cam_x * p
        oy = y_offset * (0.4 + 0.6 * p)
        if heat and name == "near":
            oy += math.sin(t * 2.3) * 1.2 * heat
        cv.drawImage(img, ox, oy)
        if lights > 0.01:
            clip = skia.Path()
            any_on = False
            for r, th, o in zip(wins, thr, on):
                if not o:
                    continue
                if powercut_u is not None and powercut_u >= th:
                    continue
                clip.addRect(r.makeOutset(16, 16))
                any_on = True
            if any_on:
                cv.save()
                cv.translate(ox, oy)
                cv.clipPath(clip, doAntiAlias=False)
                pt = skia.Paint(); pt.setAlphaf(clamp(lights) * (0.75 if time == "day" else 1.0))
                cv.drawImage(lit_img, 0, 0, skia.SamplingOptions(), pt)
                cv.restore()
        if name == "near" and "kite" in extras:
            kx, ky = extras["kite"]
            with K.lit(cv, TIME_LIGHT[time]):
                kite(cv, kx + ox, ky + oy + 22, 0.9, t=t)
    if heat > 0:
        for i in range(7):
            y0 = 560 + i * 70 + math.sin(t * 0.7 + i) * 10
            path = skia.Path()
            path.moveTo(0, y0)
            for xx in range(0, W + 80, 80):
                path.lineTo(xx, y0 + math.sin(xx * 0.012 + t * 2.2 + i * 1.3) * 6)
            for xx in range(W, -80, -80):
                path.lineTo(xx, y0 + 14 + math.sin(xx * 0.012 + t * 2.2 + i * 1.3 + 0.6) * 6)
            path.close()
            cv.drawPath(path, fill("#fff3d6", 0.05 * heat))
