"""Inside the Midnight Sweet Shop: the warmest, most saturated place in the film.

draw_shop(cv, t, view='wide'|'counter'|'shelves'|'high_shelf'|'door', fullness=1.0, fade=0.0,
          blaze=0.0, jalebi_jar=True, cam=None)
    fullness 0..1  jars vanish in a fixed order, leaving dust rings on bare shelves
    fade     0..1  desaturates and dims everything, lanterns gutter, grey dust hangs (Amma fading)
    blaze    0..1  brighter, more saturated, extra bloom and sparkles (climax)
    jalebi_jar     False = the violet wish-jalebi jar is gone from the top shelf
    cam      None or (cx, cy, zoom). For view='shelves' the world is 3840 px wide: pan cx 960..2880.

draw_counter_front(cv, t, view='counter'|'wide', fade=0.0, blaze=0.0, cam=None)
    The counter (top surface + carved front). Layer order for counter shots:
        draw_shop -> Amma -> draw_counter_front -> Tola -> Meher/customer

Anchors (x, y, s): rig scale for anim.rig.chars / animals (Tola: draw_scale s)
    ANCHORS[view] dict with keys:
      'counter': amma (1240, 700, 1.9), tola (720, 668, 0.95), customer (330, 1150, 1.9), dog (520, 1130, 1.3)
      'wide':    amma (1240, 735, 1.15), tola (900, 712, 0.55), customer (560, 1000, 1.35), dog (380, 1010, 0.95),
                 door (130, 930, 1.1) (standing in the doorway)
      'door':    doorway (960, 1000, 1.45) (figure stepping in, silhouetted), inside (560, 1080, 1.9)
      'high_shelf': see JALEBI_JAR_POS, CLIMB
    SHELF_JARS: list of dicts {id, x, y(base), w, h, col, kind} for view='shelves' (world coords, 3840 wide)
    FLOAT_JAR: the jar of floating laddoos in view='shelves' (bobbing laddoos drawn live)
    JALEBI_JAR_POS: (x, y_base, w, h) on screen in view='high_shelf'
    CLIMB: list of (x, y) screen points (shelf edges, bottom -> top) Kabir's hands/feet can use
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import C, fill, stroke, lerp, clamp, smooth_path, poly, ellipse
from .gali import bloom, overlay, W, H
from .wall import jar, lantern, sparkle, quad_matrix

WOOD, WOOD_D, WOOD_L = "#6a3418", "#3e1d0c", "#b0682a"
WALL_C = "#d9893a"
KINDS = [("saffron", "laddoo"), ("rose", "barfi"), ("pistachio", "barfi"), ("silver", "barfi"),
         ("rose", "candy"), ("saffron", "jalebi"), ("pistachio", "candy"), ("silver", "candy"), ("saffron", "candy")]

ANCHORS = {
    "counter": dict(amma=(1240, 700, 1.9), tola=(720, 668, 0.95), customer=(330, 1150, 1.9), dog=(520, 1130, 1.3)),
    "wide": dict(amma=(1240, 735, 1.15), tola=(900, 712, 0.55), customer=(560, 1000, 1.35), dog=(380, 1010, 0.95),
                 door=(130, 930, 1.1)),
    "door": dict(doorway=(960, 1000, 1.45), inside=(560, 1080, 1.9)),
}
COUNTER_TOP = {"counter": (600, 668), "wide": (686, 712)}   # (back edge y, front edge y)


# ------------------------------------------------------------------ pieces
def _back_wall(c, x0, y0, x1, y1):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), K.lin((0, y0), (0, y1), ["#e39a48", WALL_C, "#b8652a"]))
    rng = K.rng(int(x0) + 3)
    for _ in range(int((x1 - x0) * (y1 - y0) / 40000)):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.drawPath(ellipse(x, y, rng.uniform(20, 60), rng.uniform(10, 30)), fill(K.shade(WALL_C, rng.uniform(-0.1, 0.08)), 0.35))
    # painted frieze along the top
    fy = y0 + 18
    c.drawRect(skia.Rect.MakeLTRB(x0, fy, x1, fy + 34), fill("#a83a2a"))
    for k in range(int((x1 - x0) // 46)):
        x = x0 + 23 + k * 46
        col = ["#ffd36b", "#9bdc6b", "#ff8fb8"][k % 3]
        for a in range(5):
            ang = a * 2 * math.pi / 5
            c.drawCircle(x + math.cos(ang) * 7, fy + 17 + math.sin(ang) * 7, 5, fill(col))
        c.drawCircle(x, fy + 17, 4, fill("#fff1c2"))
    c.drawLine(x0, fy, x1, fy, stroke("#ffd36b", 2.4)); c.drawLine(x0, fy + 34, x1, fy + 34, stroke("#ffd36b", 2.4))


def _plate_sweets(c, x, y, w, kind, rng):
    """A brass thali with a pile of sweets, base at y."""
    c.drawPath(ellipse(x, y - 4, w / 2, w * 0.1), fill("brass"))
    c.drawPath(ellipse(x, y - 4, w / 2, w * 0.1), stroke("#3a2a24", 1.6))
    if kind == "laddoo":
        r = w * 0.09
        for row, n in enumerate((5, 4, 3, 2, 1)):
            for k in range(n):
                cx = x + (k - (n - 1) / 2) * r * 2.02
                cy = y - 8 - r - row * r * 1.72
                c.drawCircle(cx, cy, r, K.rad((cx - r * 0.3, cy - r * 0.35), r * 1.3, ["#ffe08a", "saffron", "#c97a12"]))
                c.drawCircle(cx, cy, r, stroke("#7a3f12", 1.0))
    elif kind == "barfi":
        s = w * 0.15
        for row in range(3):
            for k in range(4 - row):
                cx = x + (k - (3 - row) / 2) * s * 1.05
                cy = y - 10 - row * s * 0.55
                d = poly([(cx - s / 2, cy), (cx, cy - s * 0.28), (cx + s / 2, cy), (cx, cy + s * 0.28)])
                c.drawPath(d, fill(["#e9f5df", "#ffd9e8", "#fff6dc"][(k + row) % 3]))
                c.drawPath(d, stroke("#c9c9d9", 1.0))
                c.drawCircle(cx, cy, s * 0.06, fill("#ffffff"))
    else:  # jalebi heap
        for k in range(7):
            cx, cy = x + rng.uniform(-w * 0.3, w * 0.3), y - 10 - rng.uniform(0, w * 0.18)
            pts = [(cx + math.cos(a) * (1 + a * w * 0.012), cy + math.sin(a) * (1 + a * w * 0.012) * 0.55)
                   for a in [i * 0.3 for i in range(36)]]
            c.drawPath(poly(pts, close=False), stroke("#ff9a1a", max(2, w * 0.035)))
            c.drawPath(poly(pts, close=False), stroke("#ffd36b", max(1, w * 0.012)))


def _bay(c, x0, x1, ytop, ybot, rows, jw, seed, fullness, out, jalebi=None, posts=True):
    """A shelf bay. Appends visible jar dicts (for glow) to out."""
    rng = K.rng(seed)
    c.drawRect(skia.Rect.MakeLTRB(x0, ytop, x1, ybot), K.lin((x0, 0), (x1, 0), ["#4a2210", "#7a3a16", "#4a2210"]))
    gap = (ybot - ytop) / rows
    for r in range(rows):
        y = ytop + gap * (r + 1) - 6
        # contents
        x = x0 + 14
        while x < x1 - jw * 0.6:
            roll = rng.random()
            if roll < 0.18 and x + jw * 2.2 < x1:
                w_ = jw * 2.0
                rank = rng.random()
                pkind = rng.choice(["laddoo", "barfi", "jalebi"])   # always drawn: keeps the stream stable
                if rank < fullness:
                    _plate_sweets(c, x + w_ / 2, y, w_, pkind, K.rng(int(x * 13 + y * 7)))
                else:
                    c.drawPath(ellipse(x + w_ / 2, y - 3, w_ / 2, w_ * 0.08), stroke("#a07858", 1.6, 0.6))
                x += w_ + 10
                continue
            col, kind = KINDS[rng.randrange(len(KINDS))]
            h = jw * rng.uniform(1.25, 1.6)
            w_ = jw * rng.uniform(0.85, 1.05)
            rank = rng.random()
            cx = x + w_ / 2
            if jalebi is not None and r == 0 and abs(cx - jalebi[0]) < jw * 1.2:
                x += jw * 1.6
                continue
            if rank < fullness:
                jar(c, cx, y, w_, h, col, kind, lit=1.0, seed=int(cx * 7 + y))
                out.append(dict(x=cx, y=y, w=w_, h=h, col=col, kind=kind))
            else:
                c.drawPath(ellipse(cx, y - 3, w_ * 0.45, w_ * 0.09), stroke("#a07858", 1.6, 0.6))
                c.drawPath(ellipse(cx, y - 3, w_ * 0.45, w_ * 0.09), fill("#8a6a4a", 0.18))
            x += w_ + rng.uniform(6, 14)
        # shelf board in front of the contents
        c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + gap * 0.09), K.lin((0, y), (0, y + gap * 0.09), [WOOD_L, WOOD]))
        c.drawLine(x0, y, x1, y, stroke("#ffd9a0", 1.6, 0.6))
        c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + gap * 0.09), stroke("#2a1208", 1.6))
        # scalloped paper edging
        for k in range(int((x1 - x0) // 18)):
            xx = x0 + k * 18
            c.drawPath(smooth_path([(xx, y + gap * 0.09), (xx + 9, y + gap * 0.09 + 8), (xx + 18, y + gap * 0.09)], close=False),
                       stroke(["#ff6fa5", "#ffd36b", "#9bdc6b"][k % 3], 2))
    if jalebi is not None:
        jx, jy = jalebi
        out.append(dict(x=jx, y=jy, w=jw * 1.4, h=jw * 2.0, col="violet", kind="jalebi", special=True))
    if posts:
        for x in (x0 - 14, x1 - 6):
            c.drawPath(K.rrect(x, ytop - 10, 20, ybot - ytop + 10, 5), K.lin((x, 0), (x + 20, 0), [WOOD_D, WOOD_L, WOOD]))
            c.drawPath(K.rrect(x, ytop - 10, 20, ybot - ytop + 10, 5), stroke("#2a1208", 2))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 20, ytop - 26, x1 + 20, ytop), K.lin((0, ytop - 26), (0, ytop), [WOOD_L, WOOD]))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 20, ytop - 26, x1 + 20, ytop), stroke("#2a1208", 2))


def jalebi_jar_draw(c, x, y, w, h, lit=1.0, t=0.0):
    """The forbidden jar: tall, violet glow, coiled jalebis, tiny brass padlock."""
    jar(c, x, y, w, h, "violet", "jalebi", lit=lit, t=t, seed=999)
    # padlock on the lid
    px, py = x + w * 0.05, y - h - h * 0.02
    c.drawPath(K.rrect(px - w * 0.11, py, w * 0.22, w * 0.18, w * 0.04), fill("brass"))
    c.drawPath(K.rrect(px - w * 0.11, py, w * 0.22, w * 0.18, w * 0.04), stroke("#3a2a24", 1.6))
    c.drawArc(skia.Rect.MakeLTRB(px - w * 0.07, py - w * 0.1, px + w * 0.07, py + w * 0.05), 180, 180, False, stroke("brass_dark", 2.2))
    c.drawCircle(px, py + w * 0.08, w * 0.025, fill("#3a2a24"))
    # warning ribbon tied around the neck
    c.drawLine(x - w * 0.42, y - h * 0.92, x + w * 0.42, y - h * 0.92, stroke("#d8333d", 3))


def _garland(c, x0, x1, y, sag, n=22):
    for j in range(n):
        s = j / (n - 1)
        x = lerp(x0, x1, s); yy = y + sag * 4 * s * (1 - s)
        r = 9
        c.drawCircle(x, yy, r, fill("#ff9a1a" if j % 2 else "#ffc21a"))
        c.drawCircle(x - 2, yy - 2, r * 0.4, fill("#ffe08a"))
        c.drawCircle(x, yy, r, stroke("#a8541a", 1.2))
    for x in (x0, x1):
        for k in range(4):
            c.drawCircle(x, y + 12 + k * 16, 7, fill("#ff9a1a" if k % 2 else "#ffc21a"))


def _ceiling(c, w, y1):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, w, y1), K.lin((0, 0), (0, y1), ["#2a1206", "#5a2a10"]))
    for k in range(int(w // 300) + 1):
        x = k * 300 + 40
        c.drawPath(K.rrect(x, 0, 36, y1, 4), fill(WOOD_D))
    c.drawRect(skia.Rect.MakeLTRB(0, y1 - 20, w, y1), fill(WOOD))
    c.drawLine(0, y1, w, y1, stroke("#2a1208", 2))


def _tiles(c, x0, x1, y0, y1, vpx=960, vpy=300):
    """Checker floor in perspective below y0."""
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fill("#8a3a1e"))
    rows = 7
    for i in range(rows):
        # rows get taller toward camera
        a = (i / rows) ** 1.6; b = ((i + 1) / rows) ** 1.6
        ya, yb = lerp(y0, y1 + 80, a), lerp(y0, y1 + 80, b)
        fa, fb = (ya - vpy) / (y0 - vpy), (yb - vpy) / (y0 - vpy)
        for j in range(-16, 17):
            xa0 = vpx + (j * 110) * fa; xa1 = vpx + ((j + 1) * 110) * fa
            xb0 = vpx + (j * 110) * fb; xb1 = vpx + ((j + 1) * 110) * fb
            col = "#e8cfa0" if (i + j) % 2 == 0 else "#b4532a"
            c.drawPath(poly([(xa0, ya), (xa1, ya), (xb1, yb), (xb0, yb)]), fill(col))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), K.lin_a((0, y0), (0, y1), [("#2a1006", 0.35), ("#2a1006", 0.0)]))


def _night_doorway(c, l, t, r, b, glimpse="gali"):
    """Rectangle/arch showing the dark gali outside."""
    door = smooth_path([(l, b), (l, t + (r - l) * 0.35), ((l + r) / 2, t), (r, t + (r - l) * 0.35), (r, b)], tension=0.4)
    c.save(); c.clipPath(door, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, b), K.lin((0, t), (0, b), ["#141a44", "#1f2a63", "#0e1230"]))
    K.stars(c, r, t + (b - t) * 0.3, 1.0, n=30, seed=4, top=t)
    # lane outside: two dark house silhouettes and moonlit floor
    c.drawPath(poly([(l, t + (b - t) * 0.15), (l + (r - l) * 0.32, t + (b - t) * 0.35), (l + (r - l) * 0.32, b - (b - t) * 0.22), (l, b)]), fill("#262d5e"))
    c.drawPath(poly([(r, t + (b - t) * 0.12), (r - (r - l) * 0.3, t + (b - t) * 0.33), (r - (r - l) * 0.3, b - (b - t) * 0.22), (r, b)]), fill("#1e2552"))
    c.drawPath(poly([(l + (r - l) * 0.32, b - (b - t) * 0.22), (r - (r - l) * 0.3, b - (b - t) * 0.22), (r, b), (l, b)]), fill("#3a4278"))
    for k in range(4):
        x = l + (r - l) * (0.1 + k * 0.25)
        c.drawPath(smooth_path([(l, t + (b - t) * (0.25 + k * 0.03)), (x, t + (b - t) * (0.32 + k * 0.03)), (r, t + (b - t) * (0.24 + k * 0.04))], close=False),
                   stroke("#0a0b1c", 2))
    c.restore()
    c.drawPath(door, stroke("#2a1208", 4))
    return door


# ------------------------------------------------------------------ static compositions
@lru_cache(maxsize=24)
def _static(view, full_q, jalebi):
    fullness = full_q / 40
    jars = []
    if view == "shelves":
        surf = skia.Surface(3840, H)
    else:
        surf = skia.Surface(W, H)
    c = surf.getCanvas()
    meta = {}
    if view == "wide":
        _back_wall(c, 0, 0, W, 760)
        _ceiling(c, W, 70)
        _bay(c, 330, 760, 120, 740, 5, 34, 11, fullness, jars, jalebi=(545, 120 + 124 - 6) if jalebi else None)
        if jalebi:
            jalebi_jar_draw(c, 545, 120 + 124 - 6, 46, 66)
        _bay(c, 840, 1340, 120, 740, 5, 34, 12, fullness, jars)
        _bay(c, 1420, 1840, 120, 740, 5, 34, 13, fullness, jars)
        _tiles(c, 0, W, 760, H, 1000, 330)
        # left side wall with the doorway (in perspective)
        side = poly([(0, 0), (250, 70), (250, 760), (0, 900)])
        c.drawPath(side, K.lin((0, 0), (250, 0), ["#a85a24", "#c97a32"]))
        c.save(); c.concat(quad_matrix(400, 800, [(30, 140), (220, 190), (220, 790), (30, 890)]))
        _night_doorway(c, 40, 60, 360, 800)
        c.restore()
        c.drawPath(side, stroke("#2a1208", 3))
        _garland(c, 300, 1880, 86, 60, 40)
    elif view == "counter":
        _back_wall(c, 0, 0, W, H)
        _bay(c, 110, 860, 40, 600, 4, 52, 21, fullness, jars)
        _bay(c, 1000, 1810, 40, 600, 4, 52, 22, fullness, jars)
        _garland(c, 60, 1860, 20, 70, 44)
    elif view == "shelves":
        _back_wall(c, 0, 0, 3840, H)
        _bay(c, 60, 1250, 70, 1080, 5, 92, 31, fullness, jars, posts=True)
        _bay(c, 1350, 2490, 70, 1080, 5, 92, 32, fullness, jars, posts=True)
        _bay(c, 2590, 3780, 70, 1080, 5, 92, 33, fullness, jars, posts=True)
    elif view == "high_shelf":
        # elevation 1400x1700 mapped to an upward-converging trapezoid (low angle)
        ew, eh = 1400, 1700
        _back_wall(c, 0, 0, W, H)
        c.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#2a1206", "#5a2a10"]))
        m = quad_matrix(ew, eh, [(150, -60), (1770, -60), (2060, 1160), (-140, 1160)])
        c.save(); c.concat(m)
        _back_wall(c, 0, 0, ew, eh)
        jx = 760
        _bay(c, 160, 1240, 130, eh, 6, 70, 41, fullness, jars, jalebi=(jx, 130 + (eh - 130) / 6 - 6) if jalebi else None)
        if jalebi:
            jalebi_jar_draw(c, jx, 130 + (eh - 130) / 6 - 6, 96, 140)
        c.restore()
        # map jar dicts to screen
        gap = (eh - 130) / 6
        meta["climb"] = [m.mapXY(160 + 30, 130 + gap * (r + 1) - 6) for r in range(5, -1, -1)]
        meta["climb"] = [(p.x(), p.y()) for p in meta["climb"]]
        jy = 130 + gap - 6
        p0 = m.mapXY(jx, jy); p1 = m.mapXY(jx + 48, jy - 140)
        meta["jalebi"] = (p0.x(), p0.y(), abs(p1.x() - p0.x()) * 2, abs(p0.y() - p1.y()))
        sj = []
        for j in jars:
            p = m.mapXY(j["x"], j["y"]); q = m.mapXY(j["x"] + j["w"] / 2, j["y"] - j["h"])
            sj.append(dict(j, x=p.x(), y=p.y(), w=abs(q.x() - p.x()) * 2, h=abs(p.y() - q.y())))
        jars = sj
        # ceiling beams overhead
        for k in range(5):
            x = 200 + k * 380
            c.drawPath(poly([(x, 0), (x + 60, 0), (x + 40, 60), (x + 10, 60)]), fill(WOOD_D))
    elif view == "door":
        _back_wall(c, 0, 0, W, 800)
        _ceiling(c, W, 60)
        _tiles(c, 0, W, 800, H, 960, 320)
        # thick doorway frame
        c.drawPath(K.rrect(640, 110, 640, 720, 30), K.lin((640, 0), (1280, 0), [WOOD, WOOD_L, WOOD]))
        _night_doorway(c, 700, 150, 1220, 800)
        for k in range(10):
            for x in (668, 1252):
                c.drawCircle(x, 180 + k * 64, 6, fill("#ffd36b"))
        # shelf bays at the edges of frame
        _bay(c, 40, 540, 90, 780, 5, 44, 51, fullness, jars)
        _bay(c, 1380, 1880, 90, 780, 5, 44, 52, fullness, jars)
        _garland(c, 640, 1280, 120, 50, 26)
    return surf.makeImageSnapshot(), tuple(tuple(sorted(j.items())) for j in jars), tuple(sorted(meta.items(), key=lambda kv: kv[0])) if meta else ()


@lru_cache(maxsize=4)
def _counter_img(view):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    yb, yf = COUNTER_TOP[view]
    x0, x1 = (-40, W + 40) if view == "counter" else (420, 1700)
    k = 1.0 if view == "counter" else 0.6
    # top surface (slightly in perspective)
    top = poly([(x0 + 30 * k, yb), (x1 - 30 * k, yb), (x1, yf), (x0, yf)])
    c.drawPath(top, K.lin((0, yb), (0, yf), ["#8a4a1c", "#b86a2a"]))
    c.drawLine(x0, yf, x1, yf, stroke("#ffd9a0", 2.5, 0.8))
    c.drawPath(top, stroke("#2a1208", 2.5))
    # front face
    fb = H + 10 if view == "counter" else 930
    c.drawRect(skia.Rect.MakeLTRB(x0, yf, x1, fb), K.lin((0, yf), (0, fb), ["#7a3a16", "#4a200c"]))
    c.drawRect(skia.Rect.MakeLTRB(x0, yf, x1, yf + 22 * k), fill("brass"))
    c.drawRect(skia.Rect.MakeLTRB(x0, yf, x1, yf + 22 * k), stroke("#2a1208", 1.6))
    # carved panels with painted flowers
    n = 6 if view == "counter" else 7
    pw = (x1 - x0) / n
    for i in range(n):
        px = x0 + i * pw
        r = K.rrect(px + 20 * k, yf + 44 * k, pw - 40 * k, (fb - yf) - 80 * k, 14 * k)
        c.drawPath(r, fill("#5a2810"))
        c.drawPath(r, stroke("#e3a72f", 3 * k))
        cx, cy = px + pw / 2, yf + 44 * k + ((fb - yf) - 80 * k) / 2
        for a in range(8):
            ang = a * math.pi / 4
            c.drawCircle(cx + math.cos(ang) * 22 * k, cy + math.sin(ang) * 22 * k, 11 * k, fill(["#ff6fa5", "#ffb02e"][a % 2]))
        c.drawCircle(cx, cy, 12 * k, fill("#ffd36b"))
        c.drawCircle(cx, cy, 44 * k, stroke("#9bdc6b", 3 * k))
    c.drawRect(skia.Rect.MakeLTRB(x0, yf, x1, fb), stroke("#2a1208", 3))
    # sweets on the counter: laddoo pyramid + barfi tray (kept to the sides; Tola sits left-centre)
    rng = K.rng(3)
    if view == "counter":
        _plate_sweets(c, 1580, yf - 18, 200, "laddoo", rng)
        _plate_sweets(c, 180, yf - 14, 180, "barfi", rng)
    else:
        _plate_sweets(c, 1560, yf - 10, 110, "laddoo", rng)
        _plate_sweets(c, 560, yf - 8, 90, "jalebi", rng)
    return surf.makeImageSnapshot()


# ------------------------------------------------------------------ grade
def _grade_filter(fade, blaze):
    sat = 1.0 + 0.35 * blaze - 0.85 * fade
    br = 1.0 + 0.1 * blaze - 0.5 * fade
    tint = (1.0 - 0.1 * fade, 1.0 - 0.06 * fade, 1.0 + 0.08 * fade)
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    s = sat
    sm = [lr * (1 - s) + s, lg * (1 - s), lb * (1 - s), lr * (1 - s), lg * (1 - s) + s, lb * (1 - s),
          lr * (1 - s), lg * (1 - s), lb * (1 - s) + s]
    m = []
    for row in range(3):
        k = br * tint[row]
        m += [sm[row * 3] * k, sm[row * 3 + 1] * k, sm[row * 3 + 2] * k, 0, 0.03 * blaze]
    m += [0, 0, 0, 1, 0]
    return K.matrix_filter(m)


def _draw_img(cv, img, fade, blaze, w=W, h=H):
    p = skia.Paint()
    if fade > 0.001 or blaze > 0.001:
        p.setColorFilter(_grade_filter(fade, blaze))
    cv.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)


LANTERNS = {
    "wide": [(520, 70, 0.9), (1090, 70, 0.9), (1630, 70, 0.9)],
    "counter": [(980, -10, 1.4), (300, -20, 1.2)],
    "shelves": [(700, -10, 1.6), (1900, -10, 1.6), (3100, -10, 1.6)],
    "high_shelf": [(330, 20, 1.3), (1600, 20, 1.3)],
    "door": [(960, 60, 1.2)],
}


def _motes(cv, t, n, w, col, alpha, seed=6, spark=0.0):
    rng = K.rng(seed)
    for i in range(n):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, H)
        sp = rng.uniform(6, 22)
        x = (x0 + 30 * math.sin(t * 0.4 + i)) % w
        y = (y0 - t * sp) % H
        tw = 0.5 + 0.5 * math.sin(t * rng.uniform(1.5, 4) + i)
        if spark > 0 and i % 4 == 0:
            sparkle(cv, x, y, rng.uniform(4, 9), alpha * tw * spark, rng.choice(["#ffe08a", "#ff9fc4", "#c8f0a0", "#ffffff"]))
        else:
            cv.drawCircle(x, y, rng.uniform(1.2, 3.0), fill(col, alpha * tw))


# floating-laddoo jar (view='shelves'): bobbing laddoos drawn live
FLOAT_JAR = dict(x=1660, y=0, w=120, h=170)   # y filled after the static is built


def _float_jar(cv, t, lit):
    x, y, w, h = FLOAT_JAR["x"], FLOAT_JAR["y"], FLOAT_JAR["w"], FLOAT_JAR["h"]
    body = K.rrect(x - w / 2, y - h, w, h, w * 0.22)
    cv.drawCircle(x, y - h * 0.5, w * 1.6, K.rad_a((x, y - h * 0.5), w * 1.6, [("gold", 0.35 * lit), ("gold", 0)]))
    cv.drawPath(body, fill("#dfe9f5", 0.25))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    for k in range(6):
        r = w * 0.15
        cx = x + (k % 3 - 1) * w * 0.27
        cy = y - h + r + 6 + abs(math.sin(t * 2.2 + k * 1.3)) * h * 0.18 + (k // 3) * r * 1.8
        cv.drawCircle(cx, cy, r, K.rad((cx - r * 0.3, cy - r * 0.3), r * 1.2, ["#ffe08a", "saffron", "#c97a12"]))
        cv.drawCircle(cx, cy, r, stroke("#7a3f12", 1.2))
    cv.drawRect(skia.Rect.MakeLTRB(x - w, y - h, x + w, y), K.rad_a((x, y - h * 0.6), h * 0.8, [("gold", 0.45 * lit), ("gold", 0)]))
    cv.restore()
    cv.drawPath(K.rrect(x - w * 0.36, y - h * 0.88, w * 0.12, h * 0.6, w * 0.06), fill("#ffffff", 0.45))
    cv.drawPath(body, stroke("#3a2a24", 3))
    lid = K.rrect(x - w * 0.42, y - h - h * 0.12, w * 0.84, h * 0.14, h * 0.04)
    cv.drawPath(lid, K.lin((x - w / 2, 0), (x + w / 2, 0), ["brass_dark", "brass_light", "brass"]))
    cv.drawPath(lid, stroke("#3a2a24", 2.4))
    # lid lifts a hair as the laddoos bump it
    bump = max(0.0, math.sin(t * 2.2 * 2)) ** 8 * 4
    cv.drawCircle(x, y - h - h * 0.15 - bump, w * 0.08, fill("brass"))


def _apply_cam(cv, cam):
    cv.save()
    if cam is not None:
        cx, cy, z = cam
        cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-cx, -cy)


def draw_shop(cv, t, view="wide", fullness=1.0, fade=0.0, blaze=0.0, jalebi_jar=True, cam=None):
    fq = int(round(clamp(fullness) * 40))
    img, jars, meta = _static(view, fq, bool(jalebi_jar))
    jars = [dict(j) for j in jars]
    ww = 3840 if view == "shelves" else W
    if view == "shelves" and cam is None:
        cam = (960, H / 2, 1.0)
    _apply_cam(cv, cam)
    _draw_img(cv, img, fade, blaze, ww, H)
    if view == "shelves":
        FLOAT_JAR["y"] = 70 + (1080 - 70) / 5 * 2 - 6
        _float_jar(cv, t, 1 - 0.8 * fade)
    life = (1 - 0.75 * fade) * (1 + 0.5 * blaze)
    # lanterns (guttering when fading)
    lan = LANTERNS[view]
    gut = []
    for i, (x, y, s) in enumerate(lan):
        g = 1.0
        if fade > 0:
            n = K.noise1(t * 6 + i * 5, 3)
            g = clamp(1 - fade * (0.55 + 0.45 * (n > 0.2)))
        gut.append(g * (1 + 0.3 * blaze))
        lantern(cv, x, y, s=s, lit=clamp(g), t=t, seed=i)
    # dust ring shimmer / jar pulses + bloom
    def glows(c):
        for i, j in enumerate(jars):
            pulse = 0.75 + 0.25 * math.sin(t * 1.7 + i * 0.9)
            col = K.hexrgb(K.PAL.get(j["col"], j["col"]))
            a = (0.85 if j.get("special") else (0.32 if view == "shelves" else 0.5)) * pulse * life
            c.drawCircle(j["x"], j["y"] - j["h"] * 0.45, j["w"] * 0.55, fill(col, clamp(a)))
        for i, (x, y, s) in enumerate(lan):
            c.drawCircle(x, y + 54 * s, 28 * s, fill("#ffcf6e", clamp(gut[i])))
        if view == "shelves":
            c.drawCircle(FLOAT_JAR["x"], FLOAT_JAR["y"] - 90, 70, fill("gold", 0.8 * life))
        if view in ("door",):
            c.drawRect(skia.Rect.MakeLTRB(600, 820, 1320, H), fill("#ffb02e", 0.15 * life))
    bloom(cv, glows, radius=36 if view != "shelves" else 50, strength=clamp(0.75 * life + 0.35 * blaze))
    # warm air: motes & sparkles; grey dust when fading
    if fade < 0.95:
        _motes(cv, t, 40 + int(40 * blaze), ww, "#ffe7a8", 0.55 * (1 - fade), spark=0.6 + blaze)
    if fade > 0.05:
        _motes(cv, t * 0.35, 80, ww, "#c8c0b4", 0.45 * fade, seed=13)
        cv.drawRect(skia.Rect.MakeWH(ww, H), fill("#20222e", 0.18 * fade))
    if blaze > 0:
        overlay(cv, ("shop_blaze", ww), lambda cc: cc.drawRect(skia.Rect.MakeWH(ww, H), K.rad_a((ww / 2, H * 0.45), ww * 0.7,
                [("#ffd36b", 0.1), ("#ffd36b", 0.0)])), alpha=blaze, w=ww)
    # warm vignette (shop is a cosy box)
    overlay(cv, ("shop_vig", ww), lambda cc: cc.drawRect(skia.Rect.MakeWH(ww, H), K.rad_a((ww / 2, H / 2), max(ww, W) * 0.7,
            [("#000000", 0), ("#000000", 0), ("#1a0802", 0.65)], [0, 0.55, 1])), alpha=(0.45 + 0.2 * fade) / 0.65, w=ww)
    cv.restore()


def draw_counter_front(cv, t, view="counter", fade=0.0, blaze=0.0, cam=None):
    _apply_cam(cv, cam)
    _draw_img(cv, _counter_img(view if view in COUNTER_TOP else "counter"), fade, blaze)
    cv.restore()


def _meta(view, fq=40, jalebi=True):
    return dict(_static(view, fq, jalebi)[2])


def shelf_jars():
    return [dict(j) for j in _static("shelves", 40, True)[1]]


def __getattr__(name):     # lazily computed anchors (need the static layouts)
    if name == "SHELF_JARS":
        return shelf_jars()
    if name == "JALEBI_JAR_POS":
        return _meta("high_shelf")["jalebi"]
    if name == "CLIMB":
        return _meta("high_shelf")["climb"]
    raise AttributeError(name)
