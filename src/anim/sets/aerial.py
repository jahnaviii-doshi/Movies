"""Flying over moonlit Chandpur.

draw_aerial(cv, t, scroll=0.0, time='night'|'dawn', altitude=1.0, moon=True)
  High oblique view across endless rooftops. `scroll` (px, grows as we fly right) scrolls three
  parallax bands (far 0.3, mid 0.6, near 1.0). Tiles are generated procedurally from a seeded RNG
  per tile index, so any scroll value works and loops seamlessly. The clock tower passes every
  ~9 mid tiles (indices 3, 12, 21 ...), a temple shikhara every 13 (index 7, 20 ...).
  Rooftops carry water tanks, pigeon coops, potted plants, laundry, kites on wires and families
  asleep on charpais. altitude > 1 shrinks the town toward the horizon (higher up).
  HORIZON_Y = 330. Characters fly at roughly y 300-700, scale ~0.9-1.3.
draw_moon_sky(cv, t, time='night', r=300)
  Big moon filling the frame centre (MOON_CENTER, radius r) with drifting cloud wisps and stars —
  for Meher's slow somersault in front of the moon.
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import W, H, fill, stroke, smooth_path, poly, ellipse, lerp, clamp
from . import town as T

HORIZON_Y = 330
MT = 340   # tile headroom for towers
MOON_CENTER = (960, 520)
BANDS = [  # name, parallax, base y, scale, tile width (at scale 1)
    ("far", 0.3, 400, 0.38, 460),
    ("mid", 0.6, 560, 0.62, 460),
    ("near", 1.0, 820, 1.0, 460),
]
PAL_T = {
    "night": dict(top="#8790c4", face="#2c3262", face2="#22274f", rim="#c9d2ff", tank="#15161f", line="#0c0c18",
                  haze="#2e3a78", ground="#141838"),
    "dawn": dict(top="#e2b2ae", face="#7a5f86", face2="#654d74", rim="#ffe2c8", tank="#2a2430", line="#2a1a24",
                 haze="#d79aa6", ground="#5a4670"),
}


def _block(cv, x, y, w, d, h, rng, c, detail=1.0, t=0.0):
    """Rooftop block: top face (x..x+w, y..y+d) + front wall down h. Returns list of prop spots."""
    top = skia.Rect.MakeLTRB(x, y, x + w, y + d)
    face = skia.Rect.MakeLTRB(x, y + d, x + w, y + d + h)
    cv.drawRect(face, K.lin((0, y + d), (0, y + d + 260), [c["face"], c["face2"], c["ground"]], [0, 0.45, 1]))
    # windows + a carved balcony on the top floor only; lower floors fall into the lane's shadow
    nw = max(1, int(w / 52))
    for i in range(nw):
        wx = x + (i + 0.5) * w / nw - 7
        for f, a in ((0, 1.0), (1, 0.45)):
            wy = y + d + 22 + f * 72
            lit = rng.random() < 0.05
            cv.drawPath(T.window_path(wx, wy, 14, 26), fill("#ffc46b" if lit else "#151633", a))
    if w > 160 and rng.random() < 0.5:
        bx = x + w * rng.uniform(0.3, 0.7)
        cv.drawRect(skia.Rect.MakeLTRB(bx - 22, y + d + 16, bx + 22, y + d + 50), fill("#5a3a2e"))
        cv.drawPath(smooth_path([(bx - 28, y + d + 16), (bx, y + d + 4), (bx + 28, y + d + 16)], close=True), fill("#7a5a4a"))
        cv.drawRect(skia.Rect.MakeLTRB(bx - 22, y + d + 16, bx + 22, y + d + 50), stroke(c["line"], 1.2))
    # parapet arch cut-outs
    if rng.random() < 0.4:
        for i in range(int(w / 20)):
            cv.drawPath(ellipse(x + 10 + i * 20, y - 1, 5, 3), fill(K.shade(c["top"], -0.2)))
    cv.drawRect(top, K.lin((0, y), (0, y + d), [K.shade(c["top"], 0.06), c["top"]]))
    # parapet rim
    cv.drawRect(skia.Rect.MakeLTRB(x - 3, y - 4, x + w + 3, y + 3), fill(c["rim"], 0.9))
    cv.drawRect(skia.Rect.MakeLTRB(x - 3, y + d - 3, x + w + 3, y + d + 5), fill(K.shade(c["top"], -0.15)))
    cv.drawRect(top, stroke(c["line"], 1.4, 0.6))
    cv.drawLine(x, y + d, x, y + d + h, stroke(c["line"], 1.4, 0.5))
    cv.drawLine(x + w, y + d, x + w, y + d + h, stroke(c["line"], 1.4, 0.5))
    return [(x + w * u, y + d * v) for u, v in ((0.2, 0.5), (0.5, 0.45), (0.8, 0.55))]


def _sleepers(cv, x, y, s, c, rng):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(poly([(-60, 0), (60, 0), (52, -22), (-68, -22)]), fill("#c9b07a", 0.85))
    cv.drawPath(poly([(-60, 0), (60, 0), (52, -22), (-68, -22)]), stroke(c["line"], 1.6))
    for k in range(rng.randint(1, 2)):
        oy = -6 - k * 9
        cv.drawPath(smooth_path([(-50, oy), (-30, oy - 9), (40, oy - 8), (50, oy - 2), (-46, oy + 2)], tension=0.4),
                    fill("#ece6f4"))
        cv.drawCircle(-50, oy - 4, 6, fill("#3a2a2a"))
    cv.restore()


def _coop(cv, x, y, s, c):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeLTRB(-26, -40, 26, 0), fill("#6a4a3a"))
    for i in range(6):
        cv.drawLine(-26 + i * 10, -40, -26 + i * 10, 0, stroke("#c9c2b8", 1))
    cv.drawPath(poly([(-32, -40), (0, -58), (32, -40)]), fill("#8a5530"))
    cv.drawRect(skia.Rect.MakeLTRB(-26, -40, 26, 0), stroke(c["line"], 1.6))
    for k in range(3):
        cv.drawPath(ellipse(-14 + k * 14, -62 - (k % 2) * 4, 6, 4), fill("#d8dbe6"))
    cv.restore()


@lru_cache(maxsize=160)
def _tile(band_i, idx, time):
    name, par, base_y, sc, tw = BANDS[band_i]
    c = PAL_T[time]
    rng = K.rng(band_i * 100003 + idx * 7919 + 17)
    TW = tw
    TH = 900

    def paint(cv):
        cv.translate(40, MT)
        x = 0
        while x < TW:
            w = rng.uniform(150, 260)
            if x + w > TW:
                w = TW - x
            if w < 40:
                break
            d = rng.uniform(70, 120)
            y = rng.uniform(-30, 50)
            h = TH
            spots = _block(cv, x, y + 120, w, d, h, rng, c)
            # props
            for (sx, sy) in spots:
                r = rng.random()
                if r < 0.22:
                    T.water_tank(cv, sx, sy, r=16, h=26, lw=1.2, line=c["line"], col=c["tank"])
                elif r < 0.36:
                    _coop(cv, sx, sy, 0.7, c)
                elif r < 0.52 and w > 150:
                    _sleepers(cv, sx, sy + 6, 0.6, c, rng)
                elif r < 0.68 and w > 170:
                    T.chhatri(cv, sx, sy + 10, 30, "#d6c3a6", line=c["line"], lw=1.2)
                elif r < 0.62:
                    for k in range(3):
                        px = sx - 16 + k * 16
                        cv.drawPath(poly([(px - 6, sy), (px + 6, sy), (px + 4, sy + 9), (px - 4, sy + 9)]), fill("#8a4a34"))
                        cv.drawCircle(px, sy - 6, 7, fill("#3f6b3a"))
            if rng.random() < 0.3:
                T.laundry(cv, x + 14, y + 120 + 10, x + w - 14, y + 120 + 14, rng, sag=10, lw=1.2, line=c["line"], n=4)
            x += w + rng.uniform(4, 22)
        special = None
        if name == "mid" and idx % 9 == 3:
            special = "clock"
        if name == "mid" and idx % 13 == 7:
            special = "temple"
        if special == "clock":
            T.clock_tower(cv, TW / 2, 150, h=260, col="#c9b08e", line=c["line"])
            cv.drawRect(skia.Rect.MakeLTRB(TW / 2 - 39, 150, TW / 2 + 39, TH), fill(c["face"]))
        elif special == "temple":
            T.shikhara(cv, TW / 2, 160, h=230, w=110, col="#d9b896", line=c["line"])
            cv.drawRect(skia.Rect.MakeLTRB(TW / 2 - 90, 160, TW / 2 + 90, TH), fill(c["face"]))
        # wires + a kite on some tiles
        if rng.random() < 0.45:
            y0 = rng.uniform(40, 120)
            T.wire(cv, -40, y0, TW + 40, y0 + rng.uniform(-20, 20), sag=24, col=c["line"], w=1.4)
            if rng.random() < 0.5:
                kx, ky = T.wire_point(-40, y0, TW + 40, y0, 24, rng.uniform(0.3, 0.7))
                T.kite(cv, kx, ky + 18, 0.7, col=rng.choice(["#ff6fa5", "#ffd23f", "#9bdc6b", "#5f8fb7"]), line=c["line"])

    def full(cv):
        with K.lit(cv, "neutral"):
            paint(cv)
        # atmospheric haze for distant bands
        hz = {"far": 0.55, "mid": 0.25, "near": 0.0}[name]
        if hz:
            p = fill(c["haze"], hz)
            p.setBlendMode(skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeWH(TW + 80, TH + MT), p)
    return K.render_to_image(TW + 80, TH + MT, full)


@lru_cache(maxsize=4)
def _sky(time):
    def paint(cv):
        if time == "night":
            cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, HORIZON_Y + 120),
                                                      ["#050720", "#111743", "#2a3570", "#3c4a8a"], [0, 0.5, 0.85, 1]))
            T.draw_moon(cv, 1560, 150, 58)
            T.clouds(cv, K.rng(3), W, 80, 300, "#4a5592", a=0.2, n=5)
        else:
            cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, HORIZON_Y + 120),
                                                      ["#34477f", "#9a86b6", "#f2a6a0", "#ffdca6"], [0, 0.45, 0.8, 1]))
            T.draw_sun(cv, 1500, HORIZON_Y + 40, 70, col="#fff1cf", glow="#ffb09a")
            T.clouds(cv, K.rng(4), W, 120, 300, "#ffd0c0", a=0.35, n=6)
        # distant ground haze below horizon
        g = PAL_T[time]
        cv.drawRect(skia.Rect.MakeLTRB(0, HORIZON_Y, W, H), K.lin((0, HORIZON_Y), (0, H), [g["haze"], g["ground"]]))
    return K.render_to_image(W, H, paint)


def draw_aerial(cv, t, scroll=0.0, time="night", altitude=1.0, moon=True):
    cv.drawImage(_sky(time), 0, 0)
    if time == "night":
        K.stars(cv, W, H, t, n=200, seed=21, bottom=HORIZON_Y, alpha=0.9)
    cv.save()
    if altitude != 1.0:
        a = 1 / max(0.3, altitude)
        cv.translate(W / 2, HORIZON_Y); cv.scale(a, a); cv.translate(-W / 2, -HORIZON_Y)
    for bi, (name, par, base_y, sc, tw) in enumerate(BANDS):
        off = scroll * par
        tile_w = tw * sc
        span = W / altitude if altitude > 1 else W
        x_left = -(span - W) / 2 - 40 * sc
        i0 = math.floor((off + x_left) / tile_w) - 1
        i1 = math.floor((off + x_left + span + 80) / tile_w) + 1
        for i in range(i0, i1 + 1):
            img = _tile(bi, i, time)
            x = i * tile_w - off - 40 * sc
            cv.save()
            cv.translate(x, base_y - (120 + MT) * sc)
            cv.scale(sc, sc)
            cv.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
            cv.restore()
    cv.restore()
    # moonlight wash from the upper right
    if time == "night":
        p = K.rad_a((1560, 150), 1400, [("#9fb3ff", 0.10), ("#9fb3ff", 0.0)])
        p.setBlendMode(skia.BlendMode.kPlus)
        cv.drawRect(skia.Rect.MakeWH(W, H), p)


@lru_cache(maxsize=2)
def _moon_static(time, r):
    def paint(cv):
        cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#050720", "#0f1540", "#1c2560"]))
        x, y = MOON_CENTER
        cv.drawCircle(x, y, r * 2.6, K.rad_a((x, y), r * 2.6, [("moonglow", 0.35), ("moonglow", 0.1), ("moonglow", 0)],
                                             [0, 0.45, 1]))
        cv.drawCircle(x, y, r, K.rad((x - r * 0.3, y - r * 0.35), r * 1.35, ["#fffdf0", "moon", "#dccfa6"]))
        rng = K.rng(12)
        for _ in range(14):
            a, d = rng.uniform(0, 6.28), rng.uniform(0, r * 0.8)
            cr = rng.uniform(r * 0.04, r * 0.16)
            cx, cy = x + math.cos(a) * d, y + math.sin(a) * d
            cv.drawCircle(cx, cy, cr, fill("#d4c79c", 0.45))
            cv.drawCircle(cx + cr * 0.15, cy + cr * 0.15, cr * 0.8, fill("#e8dcb8", 0.35))
        cv.drawCircle(x, y, r, stroke("#fffbe8", 3, 0.6))
    return K.render_to_image(W, H, paint)


def draw_moon_sky(cv, t, time="night", r=300):
    cv.drawImage(_moon_static(time, r), 0, 0)
    K.stars(cv, W, H, t, n=220, seed=33, bottom=H, alpha=0.9)
    # drifting cloud wisps (some cross in front of the moon)
    rng = K.rng(8)
    for i in range(7):
        y = rng.uniform(150, 950)
        L = rng.uniform(300, 700)
        sp = rng.uniform(8, 22)
        x = ((rng.uniform(0, W + L) + t * sp) % (W + L * 2)) - L
        a = rng.uniform(0.10, 0.25)
        for k in range(6):
            cv.drawOval(skia.Rect.MakeXYWH(x + k * L / 6, y + math.sin(k) * 6, L / 3, 18 + (k % 3) * 6),
                        fill("#8d98d6", a))
