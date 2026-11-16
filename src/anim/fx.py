"""Magic and atmosphere: sparkles, motes, glowing bubbles, memory bubbles, light rays,
chime rings, heroic shadows, fades, title cards."""
from __future__ import annotations

import math

import skia

from . import core as K
from .core import W, H, fill, stroke, ellipse, smooth_path, clamp, lerp


def star4(cv, x, y, r, color="#ffffff", a=1.0, rot=0.0):
    if a <= 0.01 or r <= 0.1:
        return
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    p = skia.Path()
    k = r * 0.22
    p.moveTo(0, -r); p.quadTo(k, -k, r, 0); p.quadTo(k, k, 0, r); p.quadTo(-k, k, -r, 0); p.quadTo(-k, -k, 0, -r)
    cv.drawCircle(0, 0, r * 1.6, K.rad_a((0, 0), r * 1.6, [(color, 0.35 * a), (color, 0)]))
    cv.drawPath(p, fill(color, a))
    cv.restore()


def sparkles(cv, t, cx, cy, spread=120, n=24, color="gold", size=7, seed=1, a=1.0, rise=0.0):
    r = K.rng(seed)
    for i in range(n):
        ph = r.uniform(0, 6.28)
        sp = r.uniform(1.5, 4)
        life = (math.sin(t * sp + ph) + 1) / 2
        x = cx + r.uniform(-spread, spread)
        y = cy + r.uniform(-spread * 0.6, spread * 0.6) - (rise * ((t * r.uniform(20, 60) + r.uniform(0, 200)) % 200))
        star4(cv, x, y, size * r.uniform(0.5, 1.3) * life, color, a * life, rot=t * 0.5 + ph)


def motes(cv, t, rect=(0, 0, W, H), n=60, color="#ffe7a8", a=0.6, seed=3, size=2.2):
    r = K.rng(seed)
    x0, y0, x1, y1 = rect
    for i in range(n):
        sx, sy = r.uniform(x0, x1), r.uniform(y0, y1)
        vx, vy = r.uniform(-8, 8), r.uniform(-14, -3)
        x = x0 + (sx - x0 + vx * t + 20 * math.sin(t * 0.7 + i)) % max(1, x1 - x0)
        y = y0 + (sy - y0 + vy * t) % max(1, y1 - y0)
        tw = 0.5 + 0.5 * math.sin(t * r.uniform(1, 3) + i)
        s = size * r.uniform(0.6, 1.4)
        cv.drawCircle(x, y, s * 2.5, K.rad_a((x, y), s * 2.5, [(color, a * tw * 0.4), (color, 0)]))
        cv.drawCircle(x, y, s * 0.7, fill(color, a * tw))


def glow_dot(cv, x, y, r, color="gold", a=1.0):
    cv.drawCircle(x, y, r, K.rad_a((x, y), r, [(color, a), (color, a * 0.35), (color, 0)], [0, 0.35, 1]))


def light_pool(cv, x, y, rx, ry, color="gold", a=0.5):
    cv.save(); cv.translate(x, y); cv.scale(1, ry / rx)
    cv.drawCircle(0, 0, rx, K.rad_a((0, 0), rx, [(color, a), (color, a * 0.4), (color, 0)], [0, 0.4, 1]))
    cv.restore()


def light_rays(cv, ox, oy, ang_deg, spread_deg=40, length=900, color="gold", a=0.25, n=7, t=0.0, seed=2):
    r = K.rng(seed)
    for i in range(n):
        ang = math.radians(ang_deg + (i / max(1, n - 1) - 0.5) * spread_deg + math.sin(t * 0.5 + i) * 1.5)
        w = math.radians(r.uniform(2, 5))
        p = K.poly([(ox, oy), (ox + math.cos(ang - w) * length, oy + math.sin(ang - w) * length),
                    (ox + math.cos(ang + w) * length, oy + math.sin(ang + w) * length)])
        cv.drawPath(p, K.lin_a((ox, oy), (ox + math.cos(ang) * length, oy + math.sin(ang) * length),
                               [(color, a * r.uniform(0.5, 1)), (color, 0)]))


def bubble(cv, x, y, r, color="gold", a=1.0, t=0.0, wobble=1.0):
    """A glowing glassy bubble (empty)."""
    if a <= 0.01 or r < 1:
        return
    wx = 1 + 0.04 * wobble * math.sin(t * 5)
    wy = 1 - 0.04 * wobble * math.sin(t * 5)
    cv.save(); cv.translate(x, y); cv.scale(wx, wy)
    cv.drawCircle(0, 0, r * 2.2, K.rad_a((0, 0), r * 2.2, [(color, 0.35 * a), (color, 0)]))
    cv.drawCircle(0, 0, r, K.rad_a((-r * 0.3, -r * 0.35), r * 1.3,
                                   [("#ffffff", 0.55 * a), (color, 0.28 * a), (color, 0.12 * a), (color, 0.45 * a)],
                                   [0, 0.3, 0.75, 1]))
    cv.drawCircle(0, 0, r, stroke("#ffffff", max(1.5, r * 0.04), 0.75 * a))
    cv.drawPath(smooth_path([(-r * 0.62, -r * 0.2), (-r * 0.5, -r * 0.55), (-r * 0.2, -r * 0.7)], close=False),
                stroke("#ffffff", max(2, r * 0.07), 0.8 * a))
    cv.restore()


def memory_bubble(cv, x, y, r, t, draw_inside, light="memory", a=1.0, color="gold", inner_scale=None):
    """Glowing bubble with a little scene inside (draw_inside(cv) draws a full 1920x1080 frame,
    which is fitted into the bubble)."""
    if a <= 0.01 or r < 2:
        return
    wob = 1 + 0.03 * math.sin(t * 4)
    cv.save(); cv.translate(x, y); cv.scale(wob, 2 - wob)
    cv.drawCircle(0, 0, r * 2.0, K.rad_a((0, 0), r * 2.0, [(color, 0.4 * a), (color, 0)]))
    clip = skia.Path(); clip.addCircle(0, 0, r)
    cv.save()
    cv.clipPath(clip, doAntiAlias=True)
    sc = inner_scale or (2.25 * r / H)
    with K.lit(cv, light, alpha=a):
        cv.save()
        cv.scale(sc, sc)
        cv.translate(-W / 2, -H / 2)
        draw_inside(cv)
        cv.restore()
        # inner vignette
        cv.drawCircle(0, 0, r, K.rad_a((0, 0), r, [("#000000", 0), ("#000000", 0), ("#3a2410", 0.55)], [0, 0.7, 1]))
    cv.restore()
    cv.drawCircle(0, 0, r, stroke("#fff5d6", max(2, r * 0.03), 0.9 * a))
    cv.drawPath(smooth_path([(-r * 0.66, -r * 0.18), (-r * 0.52, -r * 0.56), (-r * 0.18, -r * 0.74)], close=False),
                stroke("#ffffff", max(2, r * 0.05), 0.7 * a))
    cv.restore()
    sparkles(cv, t, x, y, spread=r * 1.1, n=10, color=color, size=max(3, r * 0.06), seed=int(r) % 17 + 5, a=a)


def chime_rings(cv, x, y, t0, t, color="gold", n=3, max_r=120, a=1.0):
    """Cartoon vibration rings radiating from (x,y) starting at time t0."""
    for i in range(n):
        u = (t - t0 - i * 0.12) / 0.7
        if 0 <= u <= 1:
            rr = lerp(10, max_r, K.ease_out(u))
            cv.drawCircle(x, y, rr, stroke(color, lerp(5, 1, u), a * (1 - u)))


def vibe_lines(cv, x, y, r, t, color="line", a=1.0, n=3):
    """Little 'shake' lines either side of an object."""
    for side in (-1, 1):
        for i in range(n):
            yy = y - r * 0.4 + i * r * 0.4
            dx = side * (r + 10 + 4 * math.sin(t * 40 + i))
            cv.drawLine(x + dx, yy, x + dx + side * 16, yy - 6, stroke(color, 3, a))


def hero_shadow(cv, draw_fn, base_x, base_y, grow=0.0, a=0.75, skew=0.0, color="#0a0618"):
    """Draw a character's silhouette as a shadow on a wall behind them. draw_fn(cv) draws the character
    with feet at (base_x, base_y). grow 0..1 scales the shadow up to ~2.6x and squares its shoulders."""
    s = 1.0 + 1.6 * K.ease_out_back(grow, 1.2)
    m = [0, 0, 0, 0, K.hexrgb(color)[0], 0, 0, 0, 0, K.hexrgb(color)[1], 0, 0, 0, 0, K.hexrgb(color)[2], 0, 0, 0, a, 0]
    with K.layer(cv, color_filter=K.matrix_filter(m), image_filter=K.blur_filter(2 + 3 * grow)):
        cv.save()
        cv.translate(base_x, base_y)
        cv.scale(s * (1 + 0.15 * grow), s)
        cv.skew(skew, 0)
        cv.translate(-base_x, -base_y)
        draw_fn(cv)
        cv.restore()


def fade(cv, color="#000000", a=1.0):
    if a <= 0:
        return
    cv.save(); cv.resetMatrix()
    cv.drawRect(skia.Rect.MakeWH(W, H), fill(color, clamp(a)))
    cv.restore()


def flash(cv, color="#fff6d8", a=1.0):
    if a <= 0:
        return
    cv.save(); cv.resetMatrix()
    p = fill(color, clamp(a)); p.setBlendMode(skia.BlendMode.kScreen)
    cv.drawRect(skia.Rect.MakeWH(W, H), p)
    cv.restore()


def card(cv, t, text, sub=None, a=1.0, bg="#0b0d2a", size=88, color="#ffe9b8", italic=True):
    """Storybook title card on a starry indigo field."""
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#14183f", bg, "#06071a"]))
    K.stars(cv, W, H, t, n=180, seed=21, alpha=0.8)
    cv.drawCircle(W / 2, H / 2, 520, K.rad_a((W / 2, H / 2), 520, [("gold", 0.12 * a), ("gold", 0)]))
    K.text_center(cv, text, W / 2, H / 2 + size * 0.3, size=size, color=color, a=a, italic=italic, bold=True)
    if sub:
        K.text_center(cv, sub, W / 2, H / 2 + size * 0.3 + 80, size=36, color="#cdb98f", a=a * 0.9, italic=True)


def sugar_crystals(cv, t, x, y, spread=40, n=14, a=1.0, seed=9):
    r = K.rng(seed)
    for i in range(n):
        px, py = x + r.uniform(-spread, spread), y + r.uniform(-spread, spread)
        s = r.uniform(3, 8)
        rot = r.uniform(0, 3.14)
        cv.save(); cv.translate(px, py); cv.rotate(math.degrees(rot))
        cv.drawPath(K.poly([(0, -s), (s * 0.7, 0), (0, s), (-s * 0.7, 0)]), fill("#eaf7ff", 0.85 * a))
        cv.drawPath(K.poly([(0, -s), (s * 0.7, 0), (0, s), (-s * 0.7, 0)]), stroke("#9fc7e8", 1.2, a))
        cv.restore()
        tw = clamp(math.sin(t * 3 + i * 1.3))
        if tw > 0.7:
            star4(cv, px, py, 6, "#ffffff", a * tw)


def shake_offset(t, amt=6.0, seed=1):
    return (amt * K.noise1(t * 30, seed), amt * K.noise1(t * 30, seed + 5))
