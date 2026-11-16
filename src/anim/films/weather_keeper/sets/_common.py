"""Shared flat-graphic pieces for The Weather Keeper sets.

Style: flat colour shapes with 2-3 tone banding, strong geometric silhouettes, dark warm
outlines on near objects only (they pick up the film's line wobble via core.stroke).

PALETTES[weather] keys: sky_top, sky_mid, sky_low, far, mid, near, near_lit, wall, wall_shade,
wall_dark, tank, tank_hi, metal, green, ground, ground_shade, accent, accent2, line, haze, window.
weathers: heat | evening | night | dust | monsoon | monsoon_night | dawn_wet
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp

LINE = "#2a1e22"

PALETTES = {
    "heat": dict(sky_top="#f6f3ea", sky_mid="#f8efdc", sky_low="#f1dcc0", far="#ead6bb", mid="#e2c39c",
                 near="#e9c79a", near_lit="#f4dfbd", wall="#efe0c4", wall_shade="#c9a77f", wall_dark="#9a7458",
                 tank="#2a2830", tank_hi="#4a4752", metal="#8c8a90", green="#9aa46a", ground="#e3c49a",
                 ground_shade="#bf9a72", accent="#e8a3a0", accent2="#d9895d", line=LINE, haze="#fbf3e2",
                 window="#7a6658"),
    "evening": dict(sky_top="#f0b08c", sky_mid="#f2c49a", sky_low="#f6dab0", far="#d9a088", mid="#c88b7a",
                    near="#d8a07e", near_lit="#f0c497", wall="#e7c3a0", wall_shade="#b07e6c", wall_dark="#7c5058",
                    tank="#2c2230", tank_hi="#5a4652", metal="#9a7f80", green="#8a8a58", ground="#d6a682",
                    ground_shade="#a8735e", accent="#e88a86", accent2="#e3a04e", line=LINE, haze="#f6caa0",
                    window="#6a4a52"),
    "night": dict(sky_top="#141a33", sky_mid="#1e2747", sky_low="#2c365a", far="#2a3150", mid="#323b5e",
                  near="#3b4569", near_lit="#556089", wall="#4a5478", wall_shade="#333b5c", wall_dark="#242a45",
                  tank="#111421", tank_hi="#2a3048", metal="#5d6585", green="#3c5050", ground="#3a4262",
                  ground_shade="#262c48", accent="#8a7aa8", accent2="#c9a26a", line="#0f1120", haze="#3a4470",
                  window="#ffd98a"),
    "dust": dict(sky_top="#b8692f", sky_mid="#c97d3d", sky_low="#d49152", far="#b06a3a", mid="#9e5a32",
                 near="#a8623a", near_lit="#c98250", wall="#c07a48", wall_shade="#8c4f2c", wall_dark="#6a3820",
                 tank="#3a2014", tank_hi="#5e3420", metal="#8a5636", green="#7a5530", ground="#b06e40",
                 ground_shade="#7e4626", accent="#d4874a", accent2="#e0a060", line="#2e160c", haze="#d99a5c",
                 window="#5a2e1a"),
    "monsoon": dict(sky_top="#2f3e55", sky_mid="#40546d", sky_low="#5a7086", far="#4c6378", mid="#566f80",
                    near="#6a8090", near_lit="#8aa2ae", wall="#93a7ad", wall_shade="#5f7682", wall_dark="#3a4c5a",
                    tank="#141a22", tank_hi="#3a4a5a", metal="#7d9098", green="#3f9a55", ground="#4f6470",
                    ground_shade="#33444f", accent="#e86a6a", accent2="#f0c04a", line="#141a22", haze="#5a7086",
                    window="#2c3a48"),
    "monsoon_night": dict(sky_top="#121a28", sky_mid="#1b2638", sky_low="#26354a", far="#223047", mid="#2a3a50",
                          near="#334760", near_lit="#4d6680", wall="#4a5f74", wall_shade="#2e3e52",
                          wall_dark="#1d2838", tank="#0a0d14", tank_hi="#24324a", metal="#4c6070",
                          green="#2a6a46", ground="#2c3c50", ground_shade="#1c2838", accent="#c86a7a",
                          accent2="#e0b04a", line="#0a0d14", haze="#2c3c55", window="#ffd98a"),
    "dawn_wet": dict(sky_top="#8aa6c2", sky_mid="#bccbd6", sky_low="#efd9bf", far="#9fb0ba", mid="#8fa3a8",
                     near="#a9b8b0", near_lit="#d6dccc", wall="#e3dcc6", wall_shade="#9eaaa4", wall_dark="#66787a",
                     tank="#1c222a", tank_hi="#46525e", metal="#8c9ca4", green="#4fae5c", ground="#7f939a",
                     ground_shade="#5a6c74", accent="#ee7a72", accent2="#f2c45a", line="#1c2228", haze="#d8e0e2",
                     window="#4a5a66"),
}

WEATHERS = tuple(PALETTES)


def pal(weather: str) -> dict:
    return PALETTES.get(weather, PALETTES["heat"])


def is_wet(weather):
    return weather in ("monsoon", "monsoon_night", "dawn_wet")


def is_night(weather):
    return weather in ("night", "monsoon_night")


# ------------------------------------------------------------------ caching
_IMG_CACHE: dict = {}


def cached(key, draw_fn, w=W, h=H, scale=1.0) -> skia.Image:
    """Render a static layer once (at `scale` resolution) and keep it."""
    img = _IMG_CACHE.get((key, scale))
    if img is None:
        def f(c):
            c.scale(scale, scale)
            draw_fn(c)
        img = K.render_to_image(int(w * scale), int(h * scale), f)
        _IMG_CACHE[(key, scale)] = img
    return img


def blit(cv, img, x=0, y=0, w=None, h=None):
    w = w or img.width()
    h = h or img.height()
    cv.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))


# ------------------------------------------------------------------ flat primitives
def rect(c, x, y, w, h, col, a=1.0):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(col, a))


def rect_line(c, x, y, w, h, col, line=LINE, lw=3.0, a=1.0):
    r = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRect(r, fill(col, a))
    if line:
        c.drawRect(r, stroke(line, lw, a))


def shape(c, path, col, line=LINE, lw=3.0, a=1.0):
    c.drawPath(path, fill(col, a))
    if line:
        c.drawPath(path, stroke(line, lw, a))


def bands(c, x, y, w, h, cols, vertical=True):
    """Flat 2-3 tone banding (stepped gradient)."""
    n = len(cols)
    for i, col in enumerate(cols):
        if vertical:
            c.drawRect(skia.Rect.MakeXYWH(x, y + h * i / n, w, h / n + 1), fill(col))
        else:
            c.drawRect(skia.Rect.MakeXYWH(x + w * i / n, y, w / n + 1, h), fill(col))


def sky(c, weather, w=W, h=H, horizon=None):
    p = pal(weather)
    horizon = horizon if horizon is not None else h
    # soft stepped sky: 3 big bands, blended edges via thin gradient strips
    c.drawRect(skia.Rect.MakeWH(w, horizon), K.lin((0, 0), (0, horizon), [p["sky_top"], p["sky_mid"], p["sky_low"]]))
    # flat banding overlay for the graphic look
    for i, k in enumerate((0.33, 0.62)):
        c.drawRect(skia.Rect.MakeXYWH(0, horizon * k, w, 3), fill("#ffffff", 0.05 if not is_night(weather) else 0.03))


def water_tank(c, x, y, s, p, line=True, ribs=True):
    """Black plastic rooftop tank (bottom-centre at x,y)."""
    w, h = 90 * s, 100 * s
    body = skia.Path()
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h, w, h), 10 * s, 10 * s))
    c.drawPath(body, fill(p["tank"]))
    # flat highlight band
    c.drawRect(skia.Rect.MakeXYWH(x - w * 0.32, y - h + 8 * s, w * 0.14, h - 16 * s), fill(p["tank_hi"]))
    if ribs:
        for k in range(1, 4):
            yy = y - h + h * k / 4
            c.drawLine(x - w / 2 + 2, yy, x + w / 2 - 2, yy, stroke(p["tank_hi"], 2.2 * s))
    # lid
    lid = ellipse(x, y - h, w * 0.28, 7 * s)
    c.drawPath(lid, fill(p["tank_hi"]))
    if line:
        c.drawPath(body, stroke(p["line"], 2.6 * s))
        c.drawPath(lid, stroke(p["line"], 2 * s))


def antenna(c, x, y, h, s, p, seed=0, lw=None):
    """Crooked TV antenna: mast + crossbars."""
    r = K.rng(seed)
    lw = lw or 3 * s
    tilt = r.uniform(-6, 6)
    tx = x + math.sin(math.radians(tilt)) * h
    c.drawLine(x, y, tx, y - h, stroke(p["metal"] if not is_night("") else p["metal"], lw))
    c.drawLine(x, y, tx, y - h, stroke(p["line"], lw * 0.5))
    for k in range(r.randint(3, 5)):
        f = 0.55 + k * 0.11
        cx, cy = lerp(x, tx, f), lerp(y, y - h, f)
        L = (40 - k * 6) * s * r.uniform(0.8, 1.2)
        ang = math.radians(r.uniform(-12, 12))
        c.drawLine(cx - math.cos(ang) * L, cy - math.sin(ang) * L, cx + math.cos(ang) * L, cy + math.sin(ang) * L,
                   stroke(p["line"], lw * 0.7))


def dome(c, x, y, r, col, line=None, finial=True):
    p = skia.Path()
    p.moveTo(x - r, y)
    p.cubicTo(x - r, y - r * 1.1, x - r * 0.15, y - r * 1.35, x, y - r * 1.5)
    p.cubicTo(x + r * 0.15, y - r * 1.35, x + r, y - r * 1.1, x + r, y)
    p.close()
    c.drawPath(p, fill(col))
    if line:
        c.drawPath(p, stroke(line, 2))
    if finial:
        c.drawLine(x, y - r * 1.5, x, y - r * 1.85, stroke(col, max(2, r * 0.08)))
        c.drawCircle(x, y - r * 1.62, max(2, r * 0.08), fill(col))


def water_tower(c, x, y, s, col):
    """Municipal overhead water tower silhouette (bottom centre x,y)."""
    for dx in (-40, -14, 14, 40):
        c.drawLine(x + dx * s, y, x + dx * s * 0.7, y - 160 * s, stroke(col, 6 * s))
    c.drawLine(x - 40 * s, y - 60 * s, x + 40 * s, y - 60 * s, stroke(col, 4 * s))
    c.drawLine(x - 34 * s, y - 115 * s, x + 34 * s, y - 115 * s, stroke(col, 4 * s))
    tank = poly([(x - 70 * s, y - 160 * s), (x + 70 * s, y - 160 * s), (x + 56 * s, y - 230 * s),
                 (x - 56 * s, y - 230 * s)])
    c.drawPath(tank, fill(col))
    c.drawPath(ellipse(x, y - 232 * s, 56 * s, 12 * s), fill(col))


def pylon(c, x, y, s, col):
    pts = [(x - 40 * s, y), (x - 8 * s, y - 260 * s), (x + 8 * s, y - 260 * s), (x + 40 * s, y)]
    c.drawLine(*pts[0], *pts[1], stroke(col, 4 * s))
    c.drawLine(*pts[3], *pts[2], stroke(col, 4 * s))
    for k in range(6):
        f0, f1 = k / 6, (k + 1) / 6
        a = (lerp(pts[0][0], pts[1][0], f0), lerp(pts[0][1], pts[1][1], f0))
        b = (lerp(pts[3][0], pts[2][0], f1), lerp(pts[3][1], pts[2][1], f1))
        c.drawLine(*a, *b, stroke(col, 2 * s))
    for yy, L in ((-200, 70), (-150, 90)):
        c.drawLine(x - L * s, y + yy * s, x + L * s, y + yy * s, stroke(col, 4 * s))


def pigeon(c, x, y, s, t, col="#6f7480", flap=True, seed=0, facing=1):
    """Tiny flying pigeon silhouette (flapping V)."""
    ph = t * 9 + seed * 1.7
    k = math.sin(ph) if flap else 0.3
    c.save(); c.translate(x, y); c.scale(s * facing, s)
    body = ellipse(0, 0, 10, 4.5)
    c.drawPath(body, fill(col))
    wy = -10 * k
    c.drawPath(poly([(-3, -1), (-14, wy), (-1, 1)]), fill(col))
    c.drawPath(poly([(3, -1), (14, wy * 0.9), (1, 1)]), fill(col))
    c.drawCircle(9, -2, 3.2, fill(col))
    c.restore()


def pigeon_flock(c, t, cx, cy, n, spread, s, col, seed=3, speed=40):
    r = K.rng(seed)
    for i in range(n):
        ox, oy = r.uniform(-spread, spread), r.uniform(-spread * 0.4, spread * 0.4)
        x = cx + ox + t * speed * r.uniform(0.8, 1.2) + math.sin(t * 0.7 + i) * 8
        y = cy + oy + math.sin(t * 1.3 + i * 2) * 6
        pigeon(c, x, y, s * r.uniform(0.8, 1.1), t, col, seed=i)


def kite(c, x, y, s, col, col2="#ffffff", t=0.0, tail=True, line_to=None):
    c.save(); c.translate(x, y); c.rotate(math.sin(t * 1.3) * 6); c.scale(s, s)
    d = poly([(0, -24), (18, 0), (0, 26), (-18, 0)])
    c.drawPath(d, fill(col))
    c.drawPath(poly([(0, -24), (18, 0), (0, 0)]), fill(col2, 0.6))
    if tail:
        c.drawPath(smooth_path([(0, 26), (6 + math.sin(t * 3) * 4, 40), (-4, 54), (3, 66)], close=False),
                   stroke(col, 2))
    c.restore()
    if line_to:
        c.drawLine(x, y, *line_to, stroke("#3a3438", 1.2, 0.7))


def laundry_line(c, x0, y0, x1, y1, t, seed, cols, wind=0.0, sag=18, s=1.0, tear=0.0, line_col=LINE):
    """A sagging line of hanging clothes. tear 0..1: pieces rip off and fly away (right-up)."""
    r = K.rng(seed)
    mid = ((x0 + x1) / 2, (y0 + y1) / 2 + sag)
    path = smooth_path([(x0, y0), mid, (x1, y1)], close=False, tension=0.6)
    c.drawPath(path, stroke(line_col, 1.4))
    n = max(2, int(abs(x1 - x0) / (46 * s)))
    for i in range(n):
        f = (i + 0.5) / n
        bx = lerp(x0, x1, f)
        by = lerp(y0, y1, f) + sag * 4 * f * (1 - f)
        w_, h_ = r.uniform(26, 40) * s, r.uniform(30, 52) * s
        col = r.choice(cols)
        kind = r.random()
        rel = r.uniform(0, 1)
        if tear > rel:
            # flown off: drift up and right, tumbling
            k = (tear - rel) / max(0.05, 1 - rel)
            bx += k * 900 + math.sin(t * 2 + i) * 30
            by -= k * 500
            ang = k * 720 * r.choice([-1, 1])
        else:
            ang = math.sin(t * (2 + wind * 6) + i) * (3 + wind * 25)
        c.save(); c.translate(bx, by); c.rotate(ang)
        sk = wind * 0.35 * math.sin(t * 7 + i)
        if kind < 0.45:   # shirt / kurta
            p = poly([(-w_ / 2, 0), (w_ / 2, 0), (w_ / 2 + 6 * s, 10 * s), (w_ * 0.38, 14 * s),
                      (w_ * 0.38 + sk * 20, h_), (-w_ * 0.38 + sk * 20, h_), (-w_ * 0.38, 14 * s),
                      (-w_ / 2 - 6 * s, 10 * s)])
        elif kind < 0.75:  # towel / dupatta
            p = poly([(-w_ / 2, 0), (w_ / 2, 0), (w_ / 2 + sk * 30, h_ * 1.2), (-w_ / 2 + sk * 30, h_ * 1.2)])
        else:   # pants
            p = poly([(-w_ / 3, 0), (w_ / 3, 0), (w_ / 3 + sk * 20, h_), (4 * s, h_), (0, h_ * 0.35),
                      (-4 * s, h_), (-w_ / 3 + sk * 20, h_)])
        c.drawPath(p, fill(col))
        c.drawPath(p, stroke(line_col, 1.6))
        c.drawCircle(-w_ * 0.3, 0, 2.2 * s, fill("#c8c0b0"))
        c.restore()


def ac_unit(c, x, y, s, p, t=0.0, drip=True):
    w, h = 70 * s, 48 * s
    rect_line(c, x, y, w, h, p["wall"], p["line"], 2.2 * s)
    for k in range(5):
        c.drawLine(x + 6 * s, y + 8 * s + k * 7 * s, x + w * 0.55, y + 8 * s + k * 7 * s, stroke(p["wall_shade"], 2 * s))
    c.drawCircle(x + w * 0.78, y + h / 2, 13 * s, fill(p["wall_shade"]))
    c.drawCircle(x + w * 0.78, y + h / 2, 13 * s, stroke(p["line"], 1.6 * s))
    if drip:
        # drip from the bottom, falling and resetting
        ph = (t * 0.9 + x * 0.013) % 1.0
        dy = ph * ph * 60 * s
        c.drawPath(ellipse(x + w * 0.2, y + h + 4 * s + dy, 2.2 * s, 3.4 * s), fill("#a8cfe0", 1 - ph))
        c.drawLine(x + w * 0.2, y + h, x + w * 0.2, y + h + 3 * s, stroke("#a8cfe0", 2 * s))


def ceiling_fan_window(c, x, y, w, h, t, spin, p, seed=0):
    """A window seen from outside with a ceiling fan inside; spin 0..1 speed."""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(p["window"]))
    if is_night(""):
        pass
    # fan
    cx, cy = x + w / 2, y + h * 0.3
    ang = (t * 14 * spin + seed) * 57.3
    c.save(); c.translate(cx, cy); c.rotate(ang)
    for k in range(3):
        c.rotate(120)
        c.drawPath(ellipse(w * 0.2, 0, w * 0.2, h * 0.04 + 1), fill(K.shade(p["window"], 0.25)))
    c.restore()
    c.drawCircle(cx, cy, max(2, w * 0.04), fill(K.shade(p["window"], 0.35)))
    # bars
    for k in range(1, 4):
        c.drawLine(x + w * k / 4, y, x + w * k / 4, y + h, stroke(p["wall_dark"], 2))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), stroke(p["line"], 2.2))


def flat_building(c, x, y, w, h, col, win, seed=0, floors=None, balcony=False, shade=None, line=None,
                  tanks=0, tank_col=None, ant_col=None, s=1.0):
    """Flat apartment block silhouette with a window grid (bottom-left x,y)."""
    r = K.rng(seed)
    c.drawRect(skia.Rect.MakeXYWH(x, y - h, w, h), fill(col))
    if shade:
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.72, y - h, w * 0.28, h), fill(shade))
    floors = floors or max(2, int(h / (46 * s)))
    cols_ = max(2, int(w / (36 * s)))
    fh = h / floors
    for f in range(floors):
        for k in range(cols_):
            if r.random() < 0.85:
                wx = x + (k + 0.3) * w / cols_
                wy = y - h + f * fh + fh * 0.28
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, w / cols_ * 0.42, fh * 0.42), fill(win))
        if balcony and f > 0:
            c.drawRect(skia.Rect.MakeXYWH(x - 4 * s, y - h + f * fh - 3 * s, w + 8 * s, 4 * s), fill(shade or win))
    if line:
        c.drawRect(skia.Rect.MakeXYWH(x, y - h, w, h), stroke(line, 2))
    for i in range(tanks):
        tx = x + w * (0.2 + 0.6 * (i + 0.5) / max(1, tanks))
        tw, th = 26 * s, 26 * s
        c.drawRect(skia.Rect.MakeXYWH(tx - tw / 2, y - h - th, tw, th), fill(tank_col or win))
    if ant_col:
        for i in range(r.randint(1, 3)):
            ax = x + r.uniform(0.1, 0.9) * w
            ah = r.uniform(30, 60) * s
            c.drawLine(ax, y - h, ax + r.uniform(-4, 4), y - h - ah, stroke(ant_col, 2 * s))
            c.drawLine(ax - 12 * s, y - h - ah * 0.8, ax + 12 * s, y - h - ah * 0.8, stroke(ant_col, 2 * s))


def wire(c, x0, y0, x1, y1, sag, col=LINE, w=2.0, a=1.0):
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo((x0 + x1) / 2, max(y0, y1) + sag, x1, y1)
    c.drawPath(path, stroke(col, w, a))


def flowerpot(c, x, y, s, p, dry=True, seed=0):
    pot = poly([(x - 18 * s, y - 32 * s), (x + 18 * s, y - 32 * s), (x + 13 * s, y), (x - 13 * s, y)])
    c.drawPath(pot, fill("#b06a48" if not is_night("") else "#b06a48"))
    c.drawPath(pot, stroke(p["line"], 2.2 * s))
    c.drawRect(skia.Rect.MakeXYWH(x - 20 * s, y - 38 * s, 40 * s, 7 * s), fill("#c27c56"))
    c.drawRect(skia.Rect.MakeXYWH(x - 20 * s, y - 38 * s, 40 * s, 7 * s), stroke(p["line"], 2 * s))
    r = K.rng(seed)
    col = "#a08a5a" if dry else p["green"]
    for k in range(4):
        a = r.uniform(-50, 50)
        L = r.uniform(18, 34) * s
        ex = x + math.sin(math.radians(a)) * L
        ey = y - 38 * s - math.cos(math.radians(a)) * L * (0.6 if dry else 1.0) + (8 * s if dry else 0)
        c.drawLine(x, y - 38 * s, ex, ey, stroke(col, 2.4 * s))


def puddle(c, x, y, rx, ry, p, t, sky_col=None):
    """Wet puddle with a sky reflection + ripples."""
    sky_col = sky_col or p["sky_mid"]
    c.drawPath(ellipse(x, y, rx, ry), fill(sky_col, 0.85))
    c.drawPath(ellipse(x, y, rx, ry), stroke(K.shade(p["ground"], -0.25), 2))
    r = K.rng(int(x * 3 + y))
    for k in range(2):
        ph = (t * 0.8 + r.uniform(0, 1)) % 1.0
        rx2 = rx * 0.15 + ph * rx * 0.5
        c.drawPath(ellipse(x + r.uniform(-rx * 0.4, rx * 0.4), y, rx2, rx2 * ry / rx), stroke("#ffffff", 1.4, 0.6 * (1 - ph)))


def apply_cam(cv, cam):
    """cam=(cx, cy, zoom) -> returns a context manager (or a no-op)."""
    if cam:
        return K.camera(cv, cam[0], cam[1], cam[2] if len(cam) > 2 else 1.0)
    from contextlib import nullcontext
    return nullcontext(cv)


def cloud_path(t, front_x, bottom_y, top_y=-150, seed=9, puff=110, drift=0.6, front_puffs=True):
    """Union silhouette of a billowing cloud bank filling x < front_x above bottom_y."""
    r = K.rng(seed)
    path = skia.Path()
    path.addRect(skia.Rect.MakeLTRB(-400, top_y, front_x - puff * 0.3, bottom_y - puff * 0.5))
    n = int((front_x + 400) / (puff * 0.8)) + 2
    for k in range(n):
        x = -400 + k * puff * 0.8 + r.uniform(-20, 20)
        if x > front_x:
            break
        rr = puff * r.uniform(0.65, 1.0)
        q = skia.Path(); q.addCircle(x, bottom_y - rr * 0.75 + math.sin(t * drift + k) * 6, rr)
        path = skia.Op(path, q, skia.PathOp.kUnion_PathOp) or path
    if front_puffs:
        m = int((bottom_y - top_y) / (puff * 0.8)) + 1
        for k in range(m):
            y = bottom_y - puff * 0.6 - k * puff * 0.8
            rr = puff * r.uniform(0.75, 1.1)
            x = front_x - rr * 0.6 + math.sin(t * drift * 1.3 + k * 1.7) * 16 + r.uniform(-30, 10)
            q = skia.Path(); q.addCircle(x, y, rr)
            path = skia.Op(path, q, skia.PathOp.kUnion_PathOp) or path
    return path


def cloud_bank(c, t, front_x, bottom_y, tones, top_y=-150, seed=9, puff=110, front_puffs=True, drift=0.6,
               alpha=1.0):
    """Flat-graphic billowing cloud bank: dark offset shadow, flat base, rim-light crescents."""
    base, light, dark = tones
    if front_x < -puff * 2:
        return
    path = cloud_path(t, front_x, bottom_y, top_y, seed, puff, drift, front_puffs)
    c.save(); c.translate(10, 18); c.drawPath(path, fill(dark, alpha)); c.restore()
    c.drawPath(path, fill(base, alpha))
    # rim light: the same silhouette offset down-right, subtracted -> crescent on top-left edges
    inner = skia.Path(path); inner.offset(-16, 20)   # rim lights the top and leading (right) edges
    rim = skia.Op(path, inner, skia.PathOp.kDifference_PathOp)
    if rim is not None:
        c.drawPath(rim, fill(light, 0.9 * alpha))
