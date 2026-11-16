"""Weather effects for The Weather Keeper (all drawn live, deterministic).

heat_shimmer(cv, t, rect, amt)        wavy translucent bands over a region (heat haze)
rain(cv, t, amount, wind=0, splash_y=None, rect=None, seed=1, color=...)
                                      streaks + splash crowns along splash_y (a y or callable x->y)
hail(cv, t, rect, amount)             bouncing ice balls inside rect (bedsheet-sized storm)
dust_storm_overlay(cv, t, amount)     brown-orange monochrome wash + flying debris
                                      (laundry, a cartwheeling plastic chair, leaves, grit)
lightning(cv, t, points, a=1.0, seed=0, width=6)  jagged bolt through points (list of (x,y))
lightning_flash(cv, a)                full-frame cool flash
wet_reflections(cv, rect, src_img, t, a)  mirrored, rippled reflection of a picture into rect
smog_blanket(cv, t, amount, top=..., bottom=..., swept=0..1)  thick grey sagging layer; swept
                                      clears it left->right (the kids sweeping)
steam(cv, t, x, y, amount, spin=0, loom=None)  pressure-cooker steam; spin>0 curls it toward
                                      the loom centre (x,y) as if being spun
drops_on_glass(cv, t, rect, amount)   raindrops on a window pane
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, ellipse, smooth_path, lerp, clamp


def heat_shimmer(cv, t, rect=(0, 0, W, H), amt=1.0, seed=5):
    if amt <= 0:
        return
    x0, y0, x1, y1 = rect
    r = K.rng(seed)
    n = int(10 * amt) + 2
    for i in range(n):
        y = y0 + (y1 - y0) * ((i + 0.5) / n) + math.sin(t * 0.6 + i) * 10
        ph = r.uniform(0, 6.28)
        path = skia.Path()
        path.moveTo(x0, y)
        steps = 24
        for k in range(1, steps + 1):
            x = lerp(x0, x1, k / steps)
            path.lineTo(x, y + math.sin(x * 0.02 + t * 3 + ph) * 4 * amt)
        cv.drawPath(path, stroke("#ffffff", 3 + 4 * amt, 0.05 + 0.05 * amt))


def rain(cv, t, amount=1.0, wind=0.0, splash_y=None, rect=None, seed=1, color="#cfe0ee", n=None, speed=1400,
         length=38, splash=True):
    if amount <= 0.01:
        return
    x0, y0, x1, y1 = rect or (0, 0, W, H)
    r = K.rng(seed)
    n = n or int(420 * amount)
    dx = wind * 0.35
    for i in range(n):
        sx = r.uniform(x0 - 200, x1 + 200)
        sy = r.uniform(0, 1)
        sp = speed * r.uniform(0.8, 1.2)
        L = length * r.uniform(0.6, 1.2)
        span = (y1 - y0) + L
        y = y0 - L + ((sy * span + t * sp) % span)
        x = sx + (y - y0) * dx
        if x < x0 - 20 or x > x1 + 20:
            continue
        a = r.uniform(0.25, 0.6) * min(1, amount * 1.3)
        cv.drawLine(x, y, x - L * dx, y - L, stroke(color, r.uniform(1.4, 2.4), a))
    if splash and splash_y is not None:
        m = int(80 * amount)
        for i in range(m):
            sx = r.uniform(x0, x1)
            ph = (t * r.uniform(2.2, 3.4) + r.uniform(0, 1)) % 1.0
            yy = splash_y(sx) if callable(splash_y) else splash_y
            if ph < 0.35:
                k = ph / 0.35
                rr = 3 + 10 * k
                cv.drawPath(ellipse(sx, yy, rr, rr * 0.3), stroke(color, 1.6, 0.7 * (1 - k)))
                for d in (-1, 1):
                    cv.drawCircle(sx + d * rr * 0.8, yy - 8 * math.sin(k * math.pi), 1.6, fill(color, 0.8 * (1 - k)))


def hail(cv, t, rect, amount=1.0, seed=11):
    if amount <= 0.01:
        return
    x0, y0, x1, y1 = rect
    r = K.rng(seed)
    n = int(70 * amount)
    for i in range(n):
        sx = r.uniform(x0, x1)
        period = r.uniform(0.5, 0.9)
        ph = ((t + r.uniform(0, 3)) % period) / period
        ground = y1 - r.uniform(0, (y1 - y0) * 0.25)
        if ph < 0.6:
            y = lerp(y0, ground, (ph / 0.6) ** 2)
            xx = sx
        else:
            k = (ph - 0.6) / 0.4
            y = ground - math.sin(k * math.pi) * 26
            xx = sx + k * r.choice([-1, 1]) * 18
        rr = r.uniform(3, 6)
        cv.drawCircle(xx, y, rr, fill("#f2fbff", 0.95))
        cv.drawCircle(xx, y, rr, stroke("#7fa6c0", 1.2))
    # little white specks settled on the ground
    for i in range(int(40 * amount)):
        gx = r.uniform(x0, x1)
        cv.drawCircle(gx, y1 - r.uniform(0, (y1 - y0) * 0.25), 2.4, fill("#ffffff", 0.85))


def dust_storm_overlay(cv, t, amount=1.0, seed=21, debris=True):
    """Brown-orange monochrome wash with drifting grit bands and flying junk."""
    if amount <= 0.01:
        return
    cv.save(); cv.resetMatrix()
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#b8692f", 0.35 * amount))
    r = K.rng(seed)
    # grit bands streaming right
    for i in range(14):
        y = r.uniform(0, H)
        sp = r.uniform(300, 700)
        x = ((t * sp + r.uniform(0, W * 2)) % (W * 2)) - W * 0.5
        w = r.uniform(400, 900)
        h = r.uniform(30, 120)
        cv.drawPath(ellipse(x, y + math.sin(t + i) * 20, w / 2, h / 2), fill("#e0a060", 0.10 * amount))
    for i in range(int(260 * amount)):
        y = r.uniform(0, H)
        sp = r.uniform(600, 1300)
        x = ((t * sp + r.uniform(0, W * 1.5)) % (W * 1.3)) - 100
        cv.drawLine(x, y, x - 14, y + 2, stroke("#f0c080", 1.4, 0.45 * amount))
    if debris:
        _debris(cv, t, amount, r)
    cv.restore()


def dust_grade(cv, amount=1.0):
    """Context manager: draw a scene through the brown-orange monochrome grade."""
    m = K.light_matrix(((1.05, 0.66, 0.38), (0.10, 0.04, 0.0), 0.0), amount)
    return K.layer(cv, color_filter=K.matrix_filter(m))


def _debris(cv, t, amount, r):
    cols = ["#e9d9b6", "#d77b6a", "#7aa0c8", "#efc65a"]
    for i in range(int(7 * amount) + 1):
        ph = (t * r.uniform(0.18, 0.3) + r.uniform(0, 1)) % 1.0
        x = lerp(-150, W + 150, ph)
        y = r.uniform(80, H * 0.75) + math.sin(t * 2 + i) * 60
        ang = t * r.uniform(200, 500)
        cv.save(); cv.translate(x, y); cv.rotate(ang)
        kind = i % 3
        col = cols[i % len(cols)]
        if kind == 0:   # flapping cloth
            w_ = r.uniform(40, 70)
            fl = math.sin(t * 12 + i) * 10
            cv.drawPath(poly([(-w_ / 2, 0), (w_ / 2, fl), (w_ / 2 - 6, 30 + fl), (-w_ / 2 + 4, 26)]), fill(col))
        elif kind == 1:  # leaves
            for k in range(3):
                cv.drawPath(ellipse(k * 14, k * 6, 9, 4), fill("#7a6a2a"))
        else:   # paper
            cv.drawRect(skia.Rect.MakeXYWH(-16, -12, 32, 24), fill("#efe6d0"))
        cv.restore()
    # the cartwheeling plastic chair
    ph = (t * 0.22) % 1.0
    x = lerp(-200, W + 200, ph)
    y = H * 0.78 - abs(math.sin(ph * math.pi * 6)) * 120
    cv.save(); cv.translate(x, y); cv.rotate(ph * 1440)
    chair = "#e8eef0"
    cv.drawRect(skia.Rect.MakeXYWH(-40, -10, 80, 12), fill(chair))
    cv.drawRect(skia.Rect.MakeXYWH(-40, -70, 12, 64), fill(chair))
    cv.drawRect(skia.Rect.MakeXYWH(-40, -70, 60, 10), fill(chair))
    for lx in (-36, 30):
        cv.drawLine(lx, 2, lx + (6 if lx > 0 else -6), 52, stroke(chair, 8))
    cv.restore()


def lightning(cv, t, points, a=1.0, seed=0, width=6, color="#f4f6ff"):
    if a <= 0.01 or len(points) < 2:
        return
    r = K.rng(seed + int(t * 20))
    path = skia.Path()
    path.moveTo(*points[0])
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for k in range(1, 6):
            f = k / 6
            path.lineTo(lerp(x0, x1, f) + r.uniform(-18, 18), lerp(y0, y1, f) + r.uniform(-8, 8))
        path.lineTo(x1, y1)
    gp = stroke(color, width * 4, 0.25 * a)
    gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    cv.drawPath(path, gp)
    cv.drawPath(path, stroke(color, width, a))
    cv.drawPath(path, stroke("#ffffff", width * 0.4, a))


def lightning_flash(cv, a=0.5, color="#dfe8ff"):
    if a <= 0:
        return
    cv.save(); cv.resetMatrix()
    p = fill(color, clamp(a)); p.setBlendMode(skia.BlendMode.kScreen)
    cv.drawRect(skia.Rect.MakeWH(W, H), p)
    cv.restore()


def wet_reflections(cv, rect, src_img, t, a=0.45, mirror_y=None):
    """Draw src_img (full-frame image) mirrored about mirror_y into rect with horizontal ripples."""
    x0, y0, x1, y1 = rect
    my = mirror_y if mirror_y is not None else y0
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    p = skia.Paint(); p.setAlphaf(a)
    strip = 8
    y = y0
    while y < y1:
        off = math.sin(y * 0.11 + t * 4) * 5
        src_y = my - (y - my)
        cv.drawImageRect(src_img, skia.Rect.MakeLTRB(x0, max(0, src_y - strip), x1, max(1, src_y)),
                         skia.Rect.MakeLTRB(x0 + off, y, x1 + off, y + strip),
                         skia.SamplingOptions(skia.FilterMode.kLinear), p)
        y += strip
    cv.restore()


def smog_blanket(cv, t, amount=1.0, top=380, bottom=640, swept=0.0, seed=33):
    if amount <= 0.01:
        return
    r = K.rng(seed)
    cut = lerp(-100, W + 100, swept)
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(cut, 0, W, H))
    # sagging lumpy bands of grey
    for layer, (col, a) in enumerate((("#8a8a8e", 0.55), ("#a3a2a4", 0.55), ("#6f6e74", 0.35))):
        path = skia.Path()
        yb = lerp(top, bottom, 0.3 + layer * 0.25)
        path.moveTo(-50, H)
        path.lineTo(-50, yb)
        for k in range(0, 21):
            x = k * W / 20
            yy = yb - 30 * math.sin(k * 1.3 + layer + t * 0.3) - r.uniform(0, 40) * (k % 2)
            path.lineTo(x, yy)
        path.lineTo(W + 50, H)
        path.close()
        cv.drawPath(path, fill(col, a * amount))
    cv.restore()
    if 0 < swept < 1:
        # swept edge: rolled-up grey cobweb
        for k in range(8):
            y = lerp(top, bottom + 120, k / 7)
            cv.drawCircle(cut + math.sin(t * 3 + k) * 6, y, 30 + 10 * math.sin(k), fill("#8a8a8e", 0.55 * amount))


def steam(cv, t, x, y, amount=1.0, spin=0.0, loom=None, seed=4, n=14):
    """Steam puffs rising from (x,y). With spin>0 and loom=(lx,ly,r) the puffs spiral into the loom."""
    if amount <= 0.01:
        return
    r = K.rng(seed)
    for i in range(n):
        life = ((t * r.uniform(0.35, 0.55) + i / n) % 1.0)
        rise = life * 260
        px = x + math.sin(t * 1.5 + i) * 12 * life + r.uniform(-6, 6)
        py = y - rise
        if spin > 0 and loom:
            lx, ly, lr = loom
            ang = t * 3 + i * 0.7 + life * 6
            rr = lr * (1 - 0.6 * life)
            px = lerp(px, lx + math.cos(ang) * rr, clamp(spin * life * 1.6))
            py = lerp(py, ly + math.sin(ang) * rr * 0.6, clamp(spin * life * 1.6))
        rad_ = 10 + 30 * life
        a = amount * (1 - life) * 0.55
        cv.drawCircle(px, py, rad_, fill("#ffffff", a))


def drops_on_glass(cv, t, rect, amount=1.0, seed=7):
    x0, y0, x1, y1 = rect
    r = K.rng(seed)
    for i in range(int(60 * amount)):
        x = r.uniform(x0, x1)
        sp = r.uniform(10, 80)
        y = y0 + ((r.uniform(0, 1) * (y1 - y0) + t * sp * (1 if r.random() < 0.3 else 0.05)) % (y1 - y0))
        rr = r.uniform(2, 6)
        cv.drawPath(ellipse(x, y, rr * 0.8, rr), fill("#dfeef8", 0.55))
        cv.drawCircle(x - rr * 0.25, y - rr * 0.3, rr * 0.25, fill("#ffffff", 0.8))
