"""Delhi skyline wide, and the chemist's-sign thermometer.

draw_skyline(cv, t, weather='heat', cam_x=0, dust=0, monsoon=0, rain=0, heat=1, pigeons=True,
             lightning_on=True)
    Panorama 2400 px wide (cam_x 0..480 pans; three parallax layers). Generic government blocks,
    domes, a flyover, municipal water towers, power pylons, kites and pigeon flocks. NO real landmarks.
    heat: the white-coin sun welded to a white sky + shimmer (heat weather).
    dust 0..1: the aandhi WALL rolls in from the left across the frame; at 1 the whole frame is
        brown-orange monochrome with flying debris.
    monsoon 0..1: a slate-blue cloud mountain sweeps from the left over the skyline; lightning
        stitches its leading edge; rain 0..1 adds rain.
    Anchors: HORIZON_Y = 760 (skyline base line), SUN_POS = (1380, 230).

draw_chemist_sign(cv, t, heat=0..1, pop_t=None)
    Close-up: a chemist's shop sign (green cross, no text) with a big wall thermometer whose red
    line climbs with heat (no numbers). If pop_t is given (seconds), the bulb top pops off at that
    time: cap flies, a spark, a little 'ping' burst.
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF

HORIZON_Y = 760
SUN_POS = (1380, 230)
WORLD_W = 2400


def _far(c, p, seed=1):
    r = K.rng(seed)
    col = p["far"]
    x = -40
    while x < WORLD_W:
        w = r.uniform(90, 200)
        h = r.uniform(120, 260)
        C.flat_building(c, x, HORIZON_Y - 40, w, h, col, K.shade(col, -0.05) if p is not None else col,
                        seed=int(x), tanks=r.randint(0, 2), tank_col=K.shade(col, -0.08), s=0.8)
        x += w + r.uniform(-10, 30)
    for dx, rr in ((420, 50), (1180, 70), (1900, 46)):
        C.dome(c, dx, HORIZON_Y - 220, rr, col)
        c.drawRect(skia.Rect.MakeXYWH(dx - rr * 1.1, HORIZON_Y - 220, rr * 2.2, 200), fill(col))
    for wx in (760, 2150):
        C.water_tower(c, wx, HORIZON_Y - 40, 1.1, K.shade(col, -0.06))


def _mid(c, p, seed=2):
    r = K.rng(seed)
    col = p["mid"]
    win = K.shade(col, -0.18)
    # flyover: a long concrete curve on pillars
    path = skia.Path()
    path.moveTo(-50, HORIZON_Y - 120)
    path.cubicTo(500, HORIZON_Y - 160, 900, HORIZON_Y - 90, 1500, HORIZON_Y - 140)
    path.lineTo(1500, HORIZON_Y - 118)
    path.cubicTo(900, HORIZON_Y - 68, 500, HORIZON_Y - 138, -50, HORIZON_Y - 98)
    path.close()
    c.drawPath(path, fill(K.shade(col, 0.06)))
    for px in range(60, 1500, 170):
        c.drawRect(skia.Rect.MakeXYWH(px, HORIZON_Y - 120, 18, 120), fill(K.shade(col, 0.02)))
    x = -20
    while x < WORLD_W:
        w = r.uniform(140, 260)
        h = r.uniform(140, 300)
        C.flat_building(c, x, HORIZON_Y + 10, w, h, col, win, seed=int(x) + 7, balcony=True,
                        shade=K.shade(col, -0.08), tanks=r.randint(1, 3), tank_col=p["tank"],
                        ant_col=K.shade(col, -0.3), s=1.0)
        x += w + r.uniform(20, 70)
    for px in (1650, 2280):
        C.pylon(c, px, HORIZON_Y + 10, 1.0, K.shade(col, -0.25))
    C.wire(c, 1650, HORIZON_Y - 250, 2280, HORIZON_Y - 250, 60, K.shade(col, -0.3), 2)


def _near(c, p, seed=3, wet=False):
    r = K.rng(seed)
    base = H + 10
    x = -30
    while x < WORLD_W:
        w = r.uniform(260, 420)
        h = r.uniform(150, 250)
        top = base - h
        c.drawRect(skia.Rect.MakeXYWH(x, top, w + 6, h + 20), fill(p["near"]))
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.7, top, w * 0.3 + 6, h + 20), fill(K.shade(p["near"], -0.08)))
        # window grid with shaded reveals + a balcony rail
        for row in range(2):
            for k in range(int(w / 70)):
                wx, wy = x + 26 + k * 70, top + 60 + row * 90
                if wy + 50 > H:
                    continue
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 34, 46), fill(p["window"]))
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 34, 8), fill(p["wall_dark"], 0.5))
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 34, 46), stroke(p["line"], 1.8))
        c.drawRect(skia.Rect.MakeXYWH(x, top, w + 6, 16), fill(p["near_lit"]))       # parapet cap
        c.drawLine(x, top + 16, x + w + 6, top + 16, stroke(p["line"], 2.5))
        c.drawLine(x, top, x + w + 6, top, stroke(p["line"], 2.5))
        c.drawLine(x + w + 6, top, x + w + 6, H, stroke(p["line"], 2.5))
        for k in range(r.randint(1, 3)):
            C.water_tank(c, x + r.uniform(0.15, 0.85) * w, top + 2, r.uniform(0.55, 0.75), p)
        for k in range(r.randint(1, 2)):
            C.antenna(c, x + r.uniform(0.1, 0.9) * w, top, r.uniform(70, 130), 0.9, p, seed=int(x) + k)
        if r.random() < 0.6:
            C.laundry_line(c, x + 20, top - 40, x + w - 30, top - 36, 0, int(x),
                           [p["accent"], p["accent2"], p["wall"], "#6f9ac0"], s=0.7, sag=10, line_col=p["line"])
        x += w + 6


def _layers(weather):
    p = C.pal(weather)
    wet = C.is_wet(weather)
    far = C.cached(("sky_far", weather), lambda c: _far(c, p), WORLD_W, H)
    mid = C.cached(("sky_mid", weather), lambda c: _mid(c, p), WORLD_W, H)
    near = C.cached(("sky_near", weather), lambda c: _near(c, p, wet=wet), WORLD_W, H)
    return far, mid, near


def _sun(cv, t, heat):
    x, y = SUN_POS
    for k, (rr, a) in enumerate(((260, 0.18), (170, 0.25), (110, 0.35))):
        cv.drawCircle(x, y, rr + math.sin(t * 2 + k) * 4 * heat, fill("#ffffff", a))
    cv.drawCircle(x, y, 78, fill("#fffdf6"))
    # welded rim: wobbling white-hot ring
    path = skia.Path()
    for i in range(41):
        a = i / 40 * 2 * math.pi
        rr = 84 + math.sin(a * 7 + t * 5) * 3 * heat
        (path.moveTo if i == 0 else path.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    cv.drawPath(path, stroke("#fff8e0", 4, 0.8))


def _cloud_mass(cv, t, front_x, p, top=-60, bottom=700, seed=9, col=None, edge_col=None):
    """A billowing mass occupying x < front_x (scalloped leading edge)."""
    r = K.rng(seed)
    col = col or p["sky_top"]
    path = skia.Path()
    path.moveTo(-200, top)
    path.lineTo(front_x - 80, top)
    n = 9
    for k in range(n + 1):
        y = lerp(top, bottom, k / n)
        bulge = 90 + 50 * math.sin(k * 1.7 + t * 0.8) + r.uniform(0, 40)
        path.quadTo(front_x + bulge, y - (bottom - top) / n / 2, front_x + bulge * 0.4, y)
    path.lineTo(-200, bottom)
    path.close()
    cv.drawPath(path, fill(col))
    # puffy top scallops
    for k in range(int(max(0, front_x + 200) / 160) + 1):
        cx = k * 160 - 60
        if cx > front_x:
            break
        cv.drawCircle(cx, bottom - 10 + math.sin(k + t) * 8, 90, fill(col))
    if edge_col:
        cv.drawPath(path, stroke(edge_col, 6, 0.5))
    return path


def _scene(cv, t, weather, cam_x, heat, pigeons, monsoon, lightning_on):
    p = C.pal(weather)
    C.sky(cv, weather, W, H, H)
    if weather == "heat":
        _sun(cv, t, heat)
    elif weather in ("evening",):
        cv.drawCircle(SUN_POS[0], 640, 120, fill("#ffd8a0", 0.9))
    elif C.is_night(weather):
        K.stars(cv, W, HORIZON_Y, t, n=150, seed=8, alpha=0.7)
        cv.drawCircle(1500, 200, 46, fill("#f4f0dc"))
    elif weather == "dust":
        cv.drawCircle(SUN_POS[0], SUN_POS[1], 70, fill("#e8a860", 0.6))
    if monsoon > 0:
        front = lerp(-300, W + 700, K.ease_in_out(monsoon))
        C.cloud_bank(cv, t, front - 240, 250, ("#1c2638", "#6f86a8", "#0e1420"), seed=12, puff=100)
        C.cloud_bank(cv, t, front, 430, ("#2a3a54", "#9bb4d4", "#121a2a"), seed=11, puff=130)
        if lightning_on and 0.05 < monsoon < 0.98:
            k = int(t * 3)
            if (k % 3) == 0:
                fy = 160 + (k * 97) % 260
                WF.lightning(cv, t, [(front + 40, fy), (front + 10, fy + 140), (front + 70, fy + 260)], a=0.9,
                             seed=k)
    far, mid, near = _layers(weather)
    for img, par in ((far, 0.3), (mid, 0.6), (near, 1.0)):
        cv.save()
        cv.translate(-cam_x * par, 0)
        C.blit(cv, img)
        cv.restore()
        if img is far:
            cv.drawRect(skia.Rect.MakeXYWH(0, HORIZON_Y - 320, W, 320),
                        K.lin_a((0, HORIZON_Y - 320), (0, HORIZON_Y), [(p["haze"], 0), (p["haze"], 0.45)]))
    if weather == "heat" and heat > 0:
        WF.heat_shimmer(cv, t, (0, 380, W, HORIZON_Y + 60), heat)
    if pigeons and weather != "dust":
        C.pigeon_flock(cv, t, 300 - cam_x * 0.5, 330, 9, 90, 1.1, K.shade(p["mid"], -0.45), seed=4, speed=55)
        C.kite(cv, 1640 - cam_x * 0.8, 300, 1.0, p["accent"], t=t, line_to=(1700 - cam_x, 900))
        C.kite(cv, 520 - cam_x * 0.7, 210, 0.8, "#6f9ac0", t=t + 1, line_to=(560 - cam_x, 900))


def draw_skyline(cv, t, weather="heat", cam_x=0.0, dust=0.0, monsoon=0.0, rain=0.0, heat=1.0, pigeons=True,
                 lightning_on=True):
    cam_x = clamp(cam_x, 0, WORLD_W - W)
    if dust <= 0:
        _scene(cv, t, weather, cam_x, heat, pigeons, monsoon, lightning_on)
    else:
        # the aandhi: behind the rolling wall the city is brown-orange monochrome and hazy
        front = lerp(-400, W + 500, K.ease_in_out(clamp(dust / 0.75)))
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(front, 0, W, H))
        _scene(cv, t, weather, cam_x, heat, pigeons, monsoon, lightning_on)
        cv.restore()
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(-10, 0, max(-10, front), H))
        _scene(cv, t, "dust", cam_x, 0, False, 0, False)
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#b8692f", 0.3))
        cv.restore()
        # the towering wall itself, rolling, a band ~300 px wide at the front
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(front - 360, -10, W + 400, H + 10))
        C.cloud_bank(cv, t * 3, front + 120, H + 200, ("#a85d2c", "#d89a5a", "#6e3818"), top_y=-200, seed=13,
                     puff=160, drift=2.0)
        cv.restore()
        # the wall's trailing edge thins into the brown haze
        cv.drawRect(skia.Rect.MakeLTRB(front - 900, 0, front - 340, H),
                    K.lin_a((front - 900, 0), (front - 340, 0), [("#a85d2c", 0.0), ("#a85d2c", 1.0)]))
        # churning billows inside the wall + debris whipped off its face
        r = K.rng(77)
        for k in range(9):
            bx = front - 260 + r.uniform(-60, 120) + math.sin(t * 2.5 + k) * 25
            by = (k + 0.5) * H / 9 + math.sin(t * 1.7 + k * 2) * 30
            rr = r.uniform(70, 120)
            cv.drawCircle(bx + 8, by + 10, rr, fill("#7a3e1c", 0.7))
            cv.drawCircle(bx, by, rr, fill("#b86a34", 0.95))
            cv.drawCircle(bx - rr * 0.3, by - rr * 0.3, rr * 0.4, fill("#e0a060", 0.25))
        for k in range(30):
            ph = (t * r.uniform(0.6, 1.2) + r.uniform(0, 1)) % 1.0
            dx = front + 100 + ph * 400
            dy = r.uniform(0, H) - ph * 80
            cv.drawLine(dx, dy, dx - 24, dy + 4, stroke("#d08a4c", 2.2, 0.8 * (1 - ph)))
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(-10, 0, max(-10, front - 160), H))
        cv.restore()
        if dust > 0.75:
            WF.dust_storm_overlay(cv, t, clamp((dust - 0.75) / 0.25))
    if rain > 0:
        WF.rain(cv, t, rain, wind=0.25, rect=(0, 0, W, H))
def draw_chemist_sign(cv, t, heat=1.0, pop_t=None, weather="heat"):
    p = C.pal(weather)
    # plastered wall
    cv.drawRect(skia.Rect.MakeWH(W, H), fill(p["wall"]))
    C.bands(cv, 0, 0, W, H, [p["wall"], K.shade(p["wall"], -0.03), K.shade(p["wall"], -0.06)])
    r = K.rng(5)
    for i in range(18):   # peeling paint patches
        x, y = r.uniform(0, W), r.uniform(0, H)
        cv.drawPath(ellipse(x, y, r.uniform(20, 70), r.uniform(10, 30)), fill(p["wall_shade"], 0.35))
    # hard diagonal shadow
    cv.drawPath(poly([(0, 0), (700, 0), (200, H), (0, H)]), fill(p["wall_dark"], 0.18))
    # sign board with a green cross
    sx, sy, sw, sh = 260, 210, 640, 460
    C.rect_line(cv, sx, sy, sw, sh, "#f4f6f0", p["line"], 5)
    C.rect_line(cv, sx + 20, sy + 20, sw - 40, sh - 40, "#2f9a5a", None)
    cx, cy = sx + sw / 2, sy + sh / 2
    for (w_, h_) in ((70, 260), (260, 70)):
        cv.drawRect(skia.Rect.MakeXYWH(cx - w_ / 2, cy - h_ / 2, w_, h_), fill("#f4f6f0"))
    cv.drawLine(sx + 80, sy, sx + 40, sy - 200, stroke(p["metal"], 8))
    cv.drawLine(sx + sw - 80, sy, sx + sw - 40, sy - 200, stroke(p["metal"], 8))
    # thermometer
    tx, ty, tw, th = 1260, 120, 150, 820
    C.rect_line(cv, tx, ty, tw, th, "#f4f1e8", p["line"], 5)
    for k in range(14):   # tick marks, no numbers
        yy = ty + 90 + k * 46
        cv.drawLine(tx + 18, yy, tx + (60 if k % 2 == 0 else 42), yy, stroke(p["line"], 3))
    tube = skia.Rect.MakeXYWH(tx + 66, ty + 40, 22, th - 170)
    cv.drawRRect(skia.RRect.MakeRectXY(tube, 11, 11), fill("#ffffff"))
    cv.drawRRect(skia.RRect.MakeRectXY(tube, 11, 11), stroke(p["line"], 3))
    bulb_y = ty + th - 90
    level = clamp(heat)
    popped = pop_t is not None and t >= pop_t
    top_y = lerp(bulb_y - 20, ty + 46, level)
    if popped:
        top_y = ty + 30
    cv.drawRect(skia.Rect.MakeLTRB(tx + 71, top_y, tx + 83, bulb_y), fill("#e2342e"))
    cv.drawCircle(tx + 77, bulb_y, 38, fill("#e2342e"))
    cv.drawCircle(tx + 77, bulb_y, 38, stroke(p["line"], 4))
    cv.drawCircle(tx + 66, bulb_y - 10, 9, fill("#ff8a80"))
    if pop_t is not None:
        k = t - pop_t
        if k < 0:
            # trembling cap
            j = math.sin(t * 60) * 2 * clamp((t - pop_t + 1.0))
            cv.drawRect(skia.Rect.MakeXYWH(tx + 64 + j, ty + 26, 26, 16), fill(p["metal"]))
        else:
            cx_, cy_ = tx + 77 + k * 240, ty + 26 - k * 700 + 900 * k * k
            cv.save(); cv.translate(cx_, cy_); cv.rotate(k * 900)
            cv.drawRect(skia.Rect.MakeXYWH(-13, -8, 26, 16), fill(p["metal"]))
            cv.drawRect(skia.Rect.MakeXYWH(-13, -8, 26, 16), stroke(p["line"], 2.5))
            cv.restore()
            if k < 0.5:
                u = k / 0.5
                for i in range(10):
                    a = i / 10 * 2 * math.pi
                    r0, r1 = 20 + 80 * u, 40 + 140 * u
                    cv.drawLine(tx + 77 + math.cos(a) * r0, ty + 34 + math.sin(a) * r0,
                                tx + 77 + math.cos(a) * r1, ty + 34 + math.sin(a) * r1,
                                stroke("#e2342e", 6 * (1 - u)))
            # red spurt
            for i in range(6):
                u = clamp(k * 1.6 - i * 0.05)
                if 0 < u < 1:
                    cv.drawCircle(tx + 77 + (i - 3) * 20 * u, ty + 34 - 200 * u + 300 * u * u, 7 * (1 - u),
                                  fill("#e2342e"))
    else:
        cv.drawRect(skia.Rect.MakeXYWH(tx + 64, ty + 26, 26, 16), fill(p["metal"]))
    if heat > 0.3:
        WF.heat_shimmer(cv, t, (0, 0, W, H), heat * 0.8)
