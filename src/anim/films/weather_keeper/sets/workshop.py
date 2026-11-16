"""THE TANK WORKSHOP: inside the oldest tank, impossibly huge, a dim cool silver-blue cathedral.

draw_workshop(cv, t, view='wide', light='day'|'night', cloth=1.0, keys=(1,1,1), torches=None,
              rattle=1.0, trunk_lid=0.0, trunk_keys=(0,0,0), photo_spot=True, cam=None, pan=0.0)
  Shelves spiral up the curved wall crowded with glass jars, each holding a little swirling breeze
  (pale-blue morning, green evening, dusty-yellow loo wind that rattles its lid). Kites hang from the
  ceiling like sleeping bats; wooden looms hold half-woven clouds; picture-labelled tins (sun, snowflake,
  swirl) are stacked; the sealed tin trunk sits in the corner; the MONSOON TRUNK sits in the middle under
  a dusty cloth (cloth 1 covered .. 0 pulled away to the right with a dust puff). A sky-picture calendar
  hangs on the wall (thirty suns + one cloud sticker weeks back). A light shaft falls from the round
  opening in the tank's roof.
  light='night': dark; pass torches=[(x, y, angle_deg), ...] for torch cones (world coords).
  keys: which of the three iron keys still hang on the hook (1 = hanging, 0 = taken).
  views: 'wide' | 'trunk' | 'calendar' | 'shelves' (pan 0..1 climbs the spiral, bottom -> top) | 'photo'
  The cast draws Varsha's photo itself at PHOTO_POS (bottom-centre of the frame on its shelf).

Anchors (world = 'wide' frame): FLOOR_Y = 980 (people at the trunk: s≈1.25; at the back wall: s≈0.9),
  TRUNK = (960, 930, 0.62) (draw_monsoon_trunk args), TIN_TRUNK = (300, 940, 0.6), PHOTO_POS = (1380, 523),
  KEYS_HOOK = (1120, 430) (three keys at x-30, x, x+30), CALENDAR = (430, 260, 220, 250),
  HATCH_IN = (960, 0) light-shaft origin; VIEWS[name] = (cx, cy, zoom); shelves_cam(pan) -> (cx, cy, zoom).
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import roof as R

FLOOR_Y = 980
TRUNK = (960, 930, 0.62)
TIN_TRUNK = (300, 940, 0.6)
PHOTO_POS = (1380, 523)
KEYS_HOOK = (1120, 430)
CALENDAR = (430, 260, 220, 250)
HATCH_IN = (960, 0)
VIEWS = {"wide": (960, 540, 1.0), "trunk": (960, 770, 1.75), "calendar": (540, 385, 2.6),
         "photo": (1370, 470, 3.0), "shelves": (960, 700, 2.0)}

WS = {
    "day": dict(wall="#3c5a7a", wall_hi="#5a7fa2", wall_dk="#24384f", shelf="#8a6a4a", shelf_dk="#5a4430",
                floor="#4a6684", floor_hi="#6a88a6", glass="#cfe6f4", shaft="#e6f2ff", metal="#b9c6d2",
                line="#14202e"),
    "night": dict(wall="#1c2a3c", wall_hi="#2c4058", wall_dk="#101a28", shelf="#4a3a2c", shelf_dk="#2c221a",
                  floor="#22324a", floor_hi="#30445e", glass="#8aa6bc", shaft="#8aa0c0", metal="#6a7a8a",
                  line="#0a1018"),
}
BREEZES = [("#bfe0ff", "#7fb8f0"), ("#bfe8b0", "#5fb07a"), ("#f2dc8a", "#c9a23a"), ("#e8d0f0", "#a888c8")]
ROWS = [(150, 0.9), (270, 0.95), (390, 1.0), (510, 1.05), (630, 1.1)]   # (y at centre, jar scale)


def shelves_cam(pan):
    return (960, lerp(760, 230, K.ease_in_out(clamp(pan))), 2.0)


def _row_y(row_y, x):
    """Shelf rows curve like rings inside a cylinder (eye line ~ 600), with a slight spiral climb."""
    eye = 600
    k = (row_y - eye) / 600.0
    dx = (x - 960) / 960.0
    return row_y + k * 120 * dx * dx - 40 * dx * 0.5


def _static(light):
    q = WS[light]

    def draw(c):
        # curved wall: vertical cylinder bands (flat tones)
        c.drawRect(skia.Rect.MakeWH(W, H), fill(q["wall"]))
        for k in range(12):
            x0 = k * W / 12
            f = abs((k + 0.5) / 12 - 0.5) * 2
            col = K.mix(q["wall_hi"], q["wall_dk"], f)
            c.drawRect(skia.Rect.MakeXYWH(x0, 0, W / 12 + 1, H), fill(col))
        # riveted seams of the tank wall
        for row in range(1, 8):
            y = row * 120
            path = skia.Path()
            for i in range(41):
                x = i * W / 40
                yy = _row_y(y, x)
                (path.moveTo if i == 0 else path.lineTo)(x, yy + 40)
            c.drawPath(path, stroke(q["wall_dk"], 3, 0.6))
        # ceiling dome edge + the round opening (light source)
        c.drawPath(ellipse(960, -40, 1100, 110), fill(q["wall_dk"]))
        c.drawPath(ellipse(960, -10, 140, 40), fill(q["shaft"]))
        # floor (circular tank floor)
        c.drawPath(ellipse(960, FLOOR_Y + 120, 1300, 260), fill(q["floor"]))
        c.drawPath(ellipse(960, FLOOR_Y + 160, 900, 170), fill(q["floor_hi"], 0.5))
        c.drawPath(ellipse(960, FLOOR_Y + 120, 1300, 260), stroke(q["line"], 3))
        # spiral shelves (planks) - jars are drawn live
        for (ry, js) in ROWS:
            path = skia.Path()
            pts = [(x, _row_y(ry, x)) for x in range(0, W + 1, 48)]
            for i, (x, y) in enumerate(pts):
                (path.moveTo if i == 0 else path.lineTo)(x, y)
            for (x, y) in reversed(pts):
                path.lineTo(x, y + 16)
            path.close()
            c.drawPath(path, fill(q["shelf"]))
            c.drawPath(path, stroke(q["line"], 2.2))
            for x in range(60, W, 240):   # brackets
                y = _row_y(ry, x)
                c.drawPath(poly([(x, y + 16), (x + 16, y + 16), (x, y + 46)]), fill(q["shelf_dk"]))
        # calendar
        x, y, w, h = CALENDAR
        C.rect_line(c, x, y, w, h, "#efe7d2", q["line"], 3)
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, 34), fill("#c9564a"))
        cw, ch = (w - 20) / 6, (h - 54) / 6
        for i in range(36):
            cx = x + 10 + (i % 6) * cw + cw / 2
            cy = y + 44 + (i // 6) * ch + ch / 2
            c.drawRect(skia.Rect.MakeXYWH(cx - cw / 2 + 2, cy - ch / 2 + 2, cw - 4, ch - 4), fill("#dfeaf2"))
            if i == 5:     # the cloud sticker, weeks ago
                for (dx, dy, rr) in ((-6, 2, 8), (5, 0, 9), (0, -5, 8)):
                    c.drawCircle(cx + dx, cy + dy, rr * 0.8, fill("#ffffff"))
                c.drawCircle(cx, cy, 13, stroke("#7fa6c0", 1.6))
            else:          # suns
                c.drawCircle(cx, cy, 7, fill("#f2b33a"))
                for a in range(8):
                    aa = a * math.pi / 4
                    c.drawLine(cx + math.cos(aa) * 9, cy + math.sin(aa) * 9, cx + math.cos(aa) * 13,
                               cy + math.sin(aa) * 13, stroke("#f2b33a", 1.6))
        c.drawCircle(x + w / 2, y - 8, 5, fill(q["metal"]))
        # photo shelf (empty spot for Varsha's photo, drawn by the cast) + keys hook board
        C.rect_line(c, PHOTO_POS[0] - 90, PHOTO_POS[1], 180, 14, q["shelf"], q["line"], 2)
        kx, ky = KEYS_HOOK
        C.rect_line(c, kx - 60, ky - 30, 120, 24, q["shelf"], q["line"], 2)
        for dx in (-30, 0, 30):
            c.drawPath(smooth_path([(kx + dx, ky - 6), (kx + dx, ky + 4), (kx + dx + 6, ky + 8)], close=False),
                       stroke(q["metal"], 3))
        # looms with half-woven clouds (left and right)
        for (lx, ly, flip) in ((170, 640, 1), (1760, 660, -1)):
            frame = rrect(lx - 90, ly - 220, 180, 260, 6)
            c.drawPath(frame, stroke(q["shelf"], 12))
            c.drawPath(frame, stroke(q["line"], 2.4))
            for k in range(1, 9):
                c.drawLine(lx - 90 + k * 20, ly - 220, lx - 90 + k * 20, ly + 40, stroke("#d8e2ea", 1.4, 0.8))
            puff = None
            for (dx, dy, rr) in ((-30, 0, 40), (10, -20, 46), (40, 10, 34), (-10, 26, 30)):
                q2 = skia.Path(); q2.addCircle(lx + dx * flip, ly - 80 + dy, rr)
                puff = q2 if puff is None else skia.Op(puff, q2, skia.PathOp.kUnion_PathOp)
            clip = skia.Path(); clip.addRect(skia.Rect.MakeLTRB(lx - 100, ly - 180, lx + 100, ly - 60))
            half = skia.Op(puff, clip, skia.PathOp.kIntersect_PathOp)
            c.drawPath(half, fill("#ffffff", 0.95))
            c.drawPath(half, stroke("#9fb8cc", 2))
            C.rect_line(c, lx - 100, ly + 40, 200, 20, q["shelf_dk"], q["line"], 2)
        # stacked picture-labelled tins (sun, snowflake, swirl)
        tins = [(1500, 900, "sun"), (1580, 900, "snow"), (1660, 900, "swirl"), (1540, 830, "swirl"),
                (1620, 830, "sun"), (1580, 760, "snow")]
        for (tx, ty, kind) in tins:
            C.rect_line(c, tx - 36, ty - 66, 72, 66, "#c8d2da", q["line"], 2.4)
            c.drawPath(ellipse(tx, ty - 66, 36, 8), fill("#e2e8ec"))
            c.drawRect(skia.Rect.MakeXYWH(tx - 24, ty - 50, 48, 34), fill("#f4f0e2"))
            cx, cy = tx, ty - 33
            if kind == "sun":
                c.drawCircle(cx, cy, 8, fill("#f2b33a"))
            elif kind == "snow":
                for a in range(3):
                    aa = a * math.pi / 3
                    c.drawLine(cx - math.cos(aa) * 12, cy - math.sin(aa) * 12, cx + math.cos(aa) * 12,
                               cy + math.sin(aa) * 12, stroke("#5f9ad0", 2.4))
            else:
                R._swirl(c, cx, cy, 0.5, "#8a6aa8")
    return C.cached(("workshop", light), draw)


def _jars(cv, t, light, rattle):
    q = WS[light]
    r = K.rng(5)
    for ri, (ry, js) in enumerate(ROWS):
        x = 40 + r.uniform(0, 30)
        while x < W - 40:
            if 400 < x < 690 and 200 < ry < 560:      # calendar gap
                x += 60
                continue
            if 1260 < x < 1500 and ry in (510,):      # photo shelf gap
                x += 60
                continue
            w_ = 36 * js * r.uniform(0.85, 1.15)
            h_ = 52 * js * r.uniform(0.85, 1.2)
            by = _row_y(ry, x)
            col, col2 = BREEZES[r.randrange(len(BREEZES))]
            loo = col == "#f2dc8a"
            jit = (math.sin(t * 40 + x) * 2.2 * rattle) if loo else 0.0
            jar = rrect(x - w_ / 2 + jit, by - h_, w_, h_, 7 * js)
            cv.drawPath(jar, fill(q["glass"], 0.35))
            # swirling breeze inside
            ph = t * r.uniform(1.5, 3.0) + x
            path = skia.Path()
            for i in range(18):
                a = ph + i * 0.55
                rr = (w_ * 0.12 + i * w_ * 0.016)
                px = x + jit + math.cos(a) * rr
                py = by - h_ * 0.5 + math.sin(a) * rr * 0.8 + (i - 9) * h_ * 0.02
                (path.moveTo if i == 0 else path.lineTo)(px, py)
            cv.drawPath(path, stroke(col2 if light == "day" else col, 2.4, 0.9))
            cv.drawPath(jar, stroke(q["line"], 1.8))
            cv.drawRect(skia.Rect.MakeXYWH(x - w_ * 0.45 + jit, by - h_ - 7 * js + (jit * 0.6 if loo else 0),
                                           w_ * 0.9, 8 * js), fill(q["metal"]))
            cv.drawLine(x - w_ * 0.3 + jit, by - h_ + 6, x - w_ * 0.3 + jit, by - 8, stroke("#ffffff", 2, 0.45))
            x += w_ + r.uniform(8, 26)


def _kites(cv, t, light):
    cols = ["#e88a86", "#7fb0e0", "#f2c45a", "#9bc59a", "#c99ad0", "#f4f0e6"]
    r = K.rng(8)
    for i in range(11):
        x = 180 + i * 150 + r.uniform(-40, 40)
        y = 90 + r.uniform(0, 70)
        sw = math.sin(t * 0.8 + i) * 5
        col = cols[i % len(cols)] if light == "day" else K.shade(cols[i % len(cols)], -0.45)
        cv.drawLine(x, -20, x, y - 50, stroke("#c8d2da", 1.2, 0.6))
        cv.save(); cv.translate(x, y); cv.rotate(180 + sw); cv.scale(1.7, 1.7)   # hanging upside-down like sleeping bats
        k = poly([(0, -30), (16, 0), (0, 22), (-16, 0)])
        cv.drawPath(k, fill(col)); cv.drawPath(k, stroke("#14202e", 1.8))
        cv.drawLine(0, -30, 0, 22, stroke("#14202e", 1))
        cv.drawPath(smooth_path([(0, 22), (5 + sw, 36), (-3, 50)], close=False), stroke(col, 2))
        cv.restore()


def _cloth(cv, t, cloth):
    """Dusty cloth over the Monsoon Trunk; cloth 1 covering .. 0 pulled off to the right."""
    x, y, s = TRUNK
    if cloth <= 0.001:
        return
    pull = 1 - cloth
    w, h = 560 * s, 420 * s
    off = K.ease_in(pull) * 900
    drop = K.ease_in(clamp(pull * 1.5 - 0.3)) * 260
    cv.save(); cv.translate(x + off, y + drop); cv.rotate(pull * 25)
    shape_ = smooth_path([(-w / 2 - 20, 0), (-w / 2, -h * 0.75), (-w * 0.25, -h), (w * 0.2, -h * 0.98),
                          (w / 2, -h * 0.74), (w / 2 + 24, 0), (w * 0.2, 12), (-w * 0.2, 10)], tension=0.45)
    cv.drawPath(shape_, fill("#b8b0a0"))
    for k in range(5):
        xx = -w / 2 + 40 + k * w / 5
        cv.drawLine(xx, -h * 0.7, xx + 12, -10, stroke("#9a9282", 3))
    cv.drawPath(shape_, stroke("#14202e", 3))
    cv.restore()
    if 0.02 < pull < 0.6:   # dust puff where it was
        u = pull / 0.6
        for k in range(8):
            a = k / 8 * 2 * math.pi
            cv.drawCircle(x + math.cos(a) * 200 * s * u, y - 120 * s + math.sin(a) * 90 * s * u, 40 * s * (1 - u) + 6,
                          fill("#c8c0b0", 0.6 * (1 - u)))


def _torches(cv, torches, darkness=0.82):
    """Darken everything except soft torch cones (positions/angles in the current world coords)."""
    cv.saveLayer(None, None)
    cv.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 4000, 4000), fill("#060a12", darkness))
    for (x, y, ang) in torches:
        a = math.radians(ang)
        L = 900
        cone = poly([(x, y), (x + math.cos(a - 0.32) * L, y + math.sin(a - 0.32) * L),
                     (x + math.cos(a + 0.32) * L, y + math.sin(a + 0.32) * L)])
        p = K.rad_a((x, y), L, [("#000000", 0.95), ("#000000", 0.45), ("#000000", 0.0)], [0, 0.45, 1])
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
        p.setBlendMode(skia.BlendMode.kDstOut)
        cv.drawPath(cone, p)
        p2 = K.rad_a((x, y), 160, [("#000000", 0.9), ("#000000", 0.0)])
        p2.setBlendMode(skia.BlendMode.kDstOut)
        cv.drawCircle(x, y, 160, p2)
    cv.restore()
    for (x, y, ang) in torches:   # warm tint inside the cone
        a = math.radians(ang)
        cone = poly([(x, y), (x + math.cos(a - 0.32) * 900, y + math.sin(a - 0.32) * 900),
                     (x + math.cos(a + 0.32) * 900, y + math.sin(a + 0.32) * 900)])
        cv.drawPath(cone, K.rad_a((x, y), 900, [("#ffe6a8", 0.10), ("#ffe6a8", 0.0)]))


def draw_workshop(cv, t, view="wide", light="day", cloth=1.0, keys=(1, 1, 1), torches=None, rattle=1.0,
                  trunk_lid=0.0, trunk_keys=(0, 0, 0), photo_spot=True, cam=None, pan=0.0):
    q = WS[light]
    if cam is None:
        cam = shelves_cam(pan) if view == "shelves" else VIEWS.get(view, VIEWS["wide"])
    with K.camera(cv, *cam):
        C.blit(cv, _static(light))
        # light shaft from the opening
        if light == "day":
            cv.drawPath(poly([(880, -20), (1040, -20), (1360, FLOOR_Y + 60), (560, FLOOR_Y + 60)]),
                        K.lin_a((960, 0), (960, FLOOR_Y), [(q["shaft"], 0.35), (q["shaft"], 0.06)]))
            r = K.rng(3)
            for i in range(40):
                mx = r.uniform(600, 1320)
                my = (r.uniform(0, FLOOR_Y) + t * r.uniform(6, 16)) % FLOOR_Y
                cv.drawCircle(mx + math.sin(t + i) * 8, my, 1.8, fill("#ffffff", 0.5))
        _kites(cv, t, light)
        _jars(cv, t, light, rattle)
        # three iron keys on the hook
        kx, ky = KEYS_HOOK
        for i, dx in enumerate((-30, 0, 30)):
            if i < len(keys) and keys[i] > 0.5:
                sw = math.sin(t * 1.2 + i) * 3
                cv.save(); cv.translate(kx + dx, ky + 6); cv.rotate(sw)
                cv.drawCircle(0, 10, 9, stroke(q["metal"], 4))
                cv.drawRect(skia.Rect.MakeXYWH(-2.5, 18, 5, 40), fill(q["metal"]))
                cv.drawRect(skia.Rect.MakeXYWH(0, 50, 10, 4), fill(q["metal"]))
                cv.drawRect(skia.Rect.MakeXYWH(0, 42, 7, 4), fill(q["metal"]))
                cv.restore()
        # tin trunk in the corner, Monsoon Trunk in the middle (+ cloth)
        R.draw_tin_trunk(cv, *TIN_TRUNK, t, open=0.0, chains=1.0, weather="night")
        x, y, s = TRUNK
        R.draw_monsoon_trunk(cv, x, y, s, t, lid=trunk_lid, keys=trunk_keys, glow=1.0 if trunk_lid > 0 else 0.0)
        _cloth(cv, t, cloth)
        if light == "night" and torches:
            _torches(cv, torches)
        elif light == "night":
            cv.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 4000, 4000), fill("#060a12", 0.35))
