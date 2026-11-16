"""THE ROOF of Block C: the film's main set.

draw_roof(cv, t, weather='heat', view='wide', steam_on=0.0, spin=0.0, rain=0.0, puddles=None,
          tin_drops=None, smog=0.0, swept=0.0)
  weather: heat | evening | night | dust | monsoon | monsoon_night | dawn_wet
  view 'wide' (whole roof), 'loom' (medium on Meghnath's bucket + stove + loom), 'hatch' (the big rusty
      tank and its iron hatch), 'parapet' (Ishaan's spot at the back wall looking out over the city),
      'trunk' (open sky centre where the Monsoon Trunk is dragged).
  steam_on 0..1: pressure-cooker steam rising; spin 0..1: steam curls into the loom (cloud spinning).
  rain 0..1 (wet weathers), puddles (default: on for dawn_wet/monsoon*), tin_drops: list of times (s) at
      which a fat raindrop lands on the stair-hut TIN roof (splash + ring) - the "tunk" shots.
  smog 0..1 grey smog blanket over the city beyond; swept 0..1 clears it (kids sweeping).

Anchors (all in the 'wide' view; the other views are camera framings of the same world, see VIEWS):
  ANCHORS = {
    'bucket_seat': (x, y, s)  Meghnath sitting (legs='sit', seat point),
    'loom': (cx, cy, r)       centre/radius of the antenna-wire loom where steam is spun,
    'cooker': (x, y)          pressure-cooker valve (steam origin),
    'hatch': HATCH_RECT       (x, y, w, h) the small iron hatch in the big tank,
    'parapet_sit': (x, y, s)  Ishaan sitting on the back parapet, seen from behind, legs over the far side,
    'runup': ((x0, y0), (x1, y1))  Rehan's long run-up line across the roof, ending at the trunk,
    'trunk': (x, y, s)        where to draw the Monsoon Trunk under open sky,
    'stair_door': (x, y, s)   the stair-hut door (gap) where kids come out,
    'tin_roof': (x0, y0, x1, y1)  the stair-hut tin roof.
  }
  roof_scale(y) -> character scale for a figure standing at floor y (perspective: back ~0.8, front ~1.9).
  VIEWS[name] = (cx, cy, zoom) camera to pass to K.camera() for that framing (draw_roof does it itself).
  trunk_keyholes(x, y, s) -> [(x,y)]*3 screen positions of the 3 keyholes on the trunk lid.

draw_monsoon_trunk(cv, x, y, s, t, lid=0, keys=(0,0,0), glow=0, weather='night')
  The huge black-green riveted iron trunk carved with clouds and peacocks; three keyholes in a wide triangle
  on the lid. keys[i]: 0 none, 0..0.5 key sliding in, 0.5..1 key turning (CLACK at 1). lid 0..1 opens
  (hinged at the back), light spills out, a slate cloud wells up (glow 0..1 brightness).
draw_tin_trunk(cv, x, y, s, t, open=0, chains=1)
  The sealed tin dust-storm trunk: chains (1 wrapped .. 0 unwound and slack on the floor), padlock, a
  painted swirling brown cloud; open 0..1 lifts the lid a crack with brown dust jets roaring out.
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF
from . import skyline as SKY

PARAPET_Y = 560        # top edge of the back parapet
FLOOR_TOP = 600
HATCH_RECT = (1420, 640, 110, 130)
ANCHORS = {
    "bucket_seat": (690, 840, 1.55),
    "loom": (930, 560, 150),
    "cooker": (830, 790),
    "hatch": HATCH_RECT,
    "parapet_sit": (1190, PARAPET_Y + 4, 0.95),
    "runup": ((360, 1010), (1140, 820)),
    "trunk": (1160, 860, 1.0),
    "stair_door": (300, 720, 1.05),
    "tin_roof": (90, 330, 470, 400),
}
VIEWS = {
    "wide": (960, 540, 1.0),
    "loom": (820, 640, 1.7),
    "hatch": (1405, 640, 1.9),
    "parapet": (1150, 440, 1.8),
    "trunk": (1160, 735, 1.6),
}


def roof_scale(y):
    return lerp(0.8, 1.9, clamp((y - FLOOR_TOP) / (H - FLOOR_TOP)))


# ------------------------------------------------------------------ static layers
def _back(weather):
    p = C.pal(weather)

    def draw(c):
        C.sky(c, weather, W, H, H)
        if weather == "heat":
            c.drawCircle(1500, 170, 66, fill("#fffdf6"))
            c.drawCircle(1500, 170, 120, fill("#ffffff", 0.25))
        elif weather == "evening":
            c.drawCircle(300, 470, 110, fill("#ffd8a0", 0.9))
        elif C.is_night(weather):
            K.stars(c, W, 480, 0.0, n=160, seed=5, alpha=0.75)
            if weather == "night":
                c.drawCircle(1580, 160, 44, fill("#f4f0dc"))
                c.drawCircle(1580, 160, 90, fill("#f4f0dc", 0.12))
        elif weather == "dawn_wet":
            c.drawCircle(320, 520, 120, fill("#ffe3b8", 0.8))
        # the city beyond the parapet: skyline layers scaled down
        far, mid, near = SKY._layers(weather if weather != "monsoon_night" else "monsoon_night")
        c.save(); c.translate(0, -230); c.scale(0.8, 0.8)
        C.blit(c, far)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, WORLD := SKY.WORLD_W, H), fill(p["haze"], 0.35))
        C.blit(c, mid)
        c.restore()
        c.drawRect(skia.Rect.MakeXYWH(0, 300, W, 300),
                   K.lin_a((0, 300), (0, 600), [(p["haze"], 0.0), (p["haze"], 0.55)]))
        # back parapet wall
        c.drawRect(skia.Rect.MakeLTRB(0, PARAPET_Y, W, FLOOR_TOP + 10), fill(p["wall"]))
        c.drawRect(skia.Rect.MakeLTRB(0, PARAPET_Y, W, PARAPET_Y + 12), fill(p["near_lit"]))
        c.drawLine(0, PARAPET_Y, W, PARAPET_Y, stroke(p["line"], 2.6))
        c.drawLine(0, PARAPET_Y + 12, W, PARAPET_Y + 12, stroke(p["line"], 1.8))
        # roof floor (concrete): flat bands + seams in perspective
        c.drawRect(skia.Rect.MakeLTRB(0, FLOOR_TOP, W, H), fill(p["ground"]))
        C.bands(c, 0, FLOOR_TOP, W, H - FLOOR_TOP, [p["ground_shade"], p["ground"], K.shade(p["ground"], 0.04)])
        c.drawLine(0, FLOOR_TOP, W, FLOOR_TOP, stroke(p["line"], 2.6))
        for k in range(-6, 14):
            x0 = 960 + k * 150
            c.drawLine(960 + k * 60, FLOOR_TOP, x0 + k * 40, H, stroke(p["ground_shade"], 2, 0.6))
        for yy in (680, 790, 940):
            c.drawLine(0, yy, W, yy, stroke(p["ground_shade"], 2, 0.5))
        r = K.rng(4)
        for i in range(12):   # stains
            c.drawPath(ellipse(r.uniform(0, W), r.uniform(650, H), r.uniform(30, 90), r.uniform(8, 20)),
                       fill(p["ground_shade"], 0.35))
        # dried flowerpots along the parapet
        for k, x in enumerate((140, 560, 610, 1260, 1840)):
            C.flowerpot(c, x, FLOOR_TOP + 6, 0.9, p, dry=weather not in ("dawn_wet",), seed=k)
        # back row of tanks (the forest)
        for i, (x, s) in enumerate(((620, 0.95), (720, 1.05), (1660, 1.0), (1780, 0.9), (1880, 1.05))):
            C.water_tank(c, x, FLOOR_TOP + 4, s, p)
        # antennas + wire tangle
        ant = [(560, FLOOR_TOP, 300), (1240, FLOOR_TOP, 340), (1720, FLOOR_TOP - 90, 260)]
        for i, (x, y, h) in enumerate(ant):
            C.antenna(c, x, y, h, 1.3, p, seed=i + 3)
        C.wire(c, 560, FLOOR_TOP - 290, 1240, FLOOR_TOP - 330, 70, p["line"], 2)
        C.wire(c, 1240, FLOOR_TOP - 330, 1720, FLOOR_TOP - 340, 50, p["line"], 2)
        C.wire(c, 560, FLOOR_TOP - 250, 1720, FLOOR_TOP - 300, 120, p["line"], 1.6)
        # stair hut (mumty) with its tin roof
        hx0, hy0, hx1 = 90, 400, 470
        c.drawRect(skia.Rect.MakeLTRB(hx0 + 10, hy0, hx1 - 10, 800), fill(p["wall"]))
        c.drawRect(skia.Rect.MakeLTRB(hx1 - 90, hy0, hx1 - 10, 800), fill(p["wall_shade"]))
        c.drawRect(skia.Rect.MakeLTRB(hx0 + 10, hy0, hx1 - 10, 800), stroke(p["line"], 2.8))
        tin = poly([(hx0 - 20, hy0), (hx1 + 20, hy0), (hx1 + 6, 330), (hx0 - 6, 330)])
        c.drawPath(tin, fill(p["metal"]))
        for k in range(16):
            x = lerp(hx0 - 14, hx1 + 14, k / 15)
            c.drawLine(x, hy0, lerp(hx0 - 2, hx1 + 2, k / 15), 330, stroke(K.shade(p["metal"], -0.25), 3))
        c.drawPath(tin, stroke(p["line"], 2.8))
        # the stair door (scraped steel) + the gap
        C.rect_line(c, 230, 560, 140, 240, "#5f7486", p["line"], 2.8)
        c.drawRect(skia.Rect.MakeXYWH(370, 560, 14, 240), fill(p["wall_dark"]))
    return C.cached(("roof_back", weather), draw)


def _big_tank(c, p, weather):
    """The oldest, biggest, rustiest tank, with the iron hatch (static)."""
    x, y, w, h = 1330, 790, 420, 470
    rust = K.mix(p["tank"], "#7a3e1e", 0.45)
    body = rrect(x, y - h, w, h, 30)
    c.drawPath(body, fill(rust))
    c.drawRect(skia.Rect.MakeXYWH(x + 40, y - h + 20, 46, h - 40), fill(K.shade(rust, 0.18)))
    for k in range(1, 6):
        yy = y - h + h * k / 6
        c.drawLine(x + 4, yy, x + w - 4, yy, stroke(K.shade(rust, -0.25), 6))
        for j in range(8):   # rivets
            c.drawCircle(x + 20 + j * (w - 40) / 7, yy, 4, fill(K.shade(rust, 0.25)))
    r = K.rng(12)
    for i in range(10):   # rust streaks
        rx = x + r.uniform(20, w - 20)
        ry = y - h + r.uniform(20, h - 120)
        c.drawRect(skia.Rect.MakeXYWH(rx, ry, r.uniform(6, 14), r.uniform(40, 120)), fill("#9a4e22", 0.55))
    c.drawPath(ellipse(x + w / 2, y - h, w / 2 - 10, 28), fill(K.shade(rust, 0.1)))
    c.drawPath(ellipse(x + w / 2, y - h, w * 0.18, 12), fill(K.shade(rust, -0.2)))
    c.drawPath(body, stroke(p["line"], 3.4))
    # iron hatch
    hx, hy, hw, hh = HATCH_RECT
    C.rect_line(c, hx - 8, hy - 8, hw + 16, hh + 16, K.shade(rust, -0.3), p["line"], 2.8)
    C.rect_line(c, hx, hy, hw, hh, "#3e4a4c", p["line"], 3)
    for (bx, by) in ((hx + 10, hy + 10), (hx + hw - 10, hy + 10), (hx + 10, hy + hh - 10), (hx + hw - 10, hy + hh - 10)):
        c.drawCircle(bx, by, 6, fill("#6a7a7c"))
    c.drawRect(skia.Rect.MakeXYWH(hx + hw - 30, hy + hh / 2 - 8, 24, 16), fill("#8a9496"))
    # a small ladder up its side
    for k in range(6):
        c.drawLine(x - 30, y - 30 - k * 60, x - 4, y - 30 - k * 60, stroke(p["metal"], 5))
    c.drawLine(x - 30, y, x - 30, y - 360, stroke(p["metal"], 5))


def _mid(weather):
    p = C.pal(weather)

    def draw(c):
        _big_tank(c, p, weather)
        # a mid-row cluster of tanks left of centre
        for (x, s) in ((470, 1.05), (560, 1.25)):
            C.water_tank(c, x, 800, s, p)
        # the LOOM: a frame of bent TV-antenna wire strung like a weaving loom
        lx, ly, lr = ANCHORS["loom"]
        frame = poly([(lx - 170, ly + 190), (lx - 150, ly - 160), (lx + 160, ly - 175), (lx + 175, ly + 180)])
        c.drawPath(frame, stroke(p["metal"], 8))
        c.drawPath(frame, stroke(p["line"], 3))
        for k in range(1, 10):   # warp threads
            f = k / 10
            c.drawLine(lerp(lx - 150, lx + 160, f), lerp(ly - 160, ly - 175, f),
                       lerp(lx - 170, lx + 175, f), lerp(ly + 190, ly + 180, f), stroke(p["metal"], 2.2))
        for k in range(1, 6):    # cross wires, a bit crooked
            f = k / 6
            c.drawLine(lerp(lx - 150, lx - 170, f), lerp(ly - 160, ly + 190, f),
                       lerp(lx + 160, lx + 175, f), lerp(ly - 175, ly + 180, f) + (6 if k % 2 else -4),
                       stroke(p["metal"], 1.8))
        for (fx, fy) in ((lx - 170, ly + 190), (lx + 175, ly + 180)):   # feet in bricks
            C.rect_line(c, fx - 26, fy - 6, 52, 30, "#b0603f", p["line"], 2)
        # stove + pressure cooker + upturned bucket
        sx, sy = 790, 840
        C.rect_line(c, sx - 10, sy - 40, 120, 40, "#3a3a44", p["line"], 2.6)        # stove
        c.drawPath(ellipse(sx + 50, sy - 44, 40, 8), fill("#555"))
        ck = rrect(sx + 6, sy - 120, 90, 78, 16)                                      # cooker body
        c.drawPath(ck, fill("#c8ccd2")); c.drawRect(skia.Rect.MakeXYWH(sx + 20, sy - 116, 14, 70), fill("#e8ecf0"))
        c.drawPath(ck, stroke(p["line"], 2.6))
        c.drawPath(ellipse(sx + 51, sy - 122, 50, 10), fill("#b4b8be"))
        c.drawPath(ellipse(sx + 51, sy - 122, 50, 10), stroke(p["line"], 2))
        c.drawLine(sx + 95, sy - 120, sx + 170, sy - 136, stroke("#2a2a2a", 8))      # handle
        c.drawRect(skia.Rect.MakeXYWH(sx + 44, sy - 150, 14, 26), fill("#3a3a3a"))   # whistle weight
        bx, by, bs = ANCHORS["bucket_seat"]
        bucket = poly([(bx - 50, by), (bx + 50, by), (bx + 40, by + 90), (bx - 40, by + 90)])
        c.drawPath(bucket, fill("#3b78c4")); c.drawPath(bucket, stroke(p["line"], 2.8))
        c.drawRect(skia.Rect.MakeXYWH(bx - 54, by - 8, 108, 12), fill("#2f62a4"))
        c.drawRect(skia.Rect.MakeXYWH(bx - 54, by - 8, 108, 12), stroke(p["line"], 2))
        # laundry line strung from the stair hut to the antenna
        C.laundry_line(c, 470, 420, 1240, 330, 0, 77, ["#e8a3a0", "#6f9ac0", "#f2e2a8", "#f4f0e6"], sag=40,
                       s=1.0, line_col=p["line"])
        # foreground: cropped tanks at the corners + a dry pot (frames the maze)
        C.water_tank(c, 40, 1150, 2.6, p)
        C.water_tank(c, 1930, 1180, 2.9, p)
        C.antenna(c, 1780, 1080, 520, 2.0, p, seed=21)
        C.flowerpot(c, 300, 1070, 1.6, p, dry=weather not in ("dawn_wet",), seed=10)
    return C.cached(("roof_mid", weather), draw)


# ------------------------------------------------------------------ live bits
def _tin_drop(cv, t, t0, p):
    k = t - t0
    if k < -0.3 or k > 1.2:
        return
    x0, y0, x1, y1 = ANCHORS["tin_roof"]
    x = lerp(x0, x1, 0.55)
    if k < 0:
        u = (k + 0.3) / 0.3
        y = lerp(y0 - 300, y0 + 20, u * u)
        cv.drawPath(ellipse(x, y, 8, 14), fill("#cfe6f4"))
        cv.drawPath(ellipse(x, y, 8, 14), stroke(p["line"], 1.6))
    else:
        u = clamp(k / 0.9)
        rr = 20 + 90 * u
        cv.drawPath(ellipse(x, y0 + 24, rr, rr * 0.25), stroke("#e6f4fc", 4 * (1 - u), 1 - u))
        for d in (-1, 1):
            cv.drawCircle(x + d * (14 + 40 * u), y0 + 20 - 50 * math.sin(u * math.pi), 6 * (1 - u), fill("#cfe6f4"))


def draw_roof(cv, t, weather="heat", view="wide", steam_on=0.0, spin=0.0, rain=0.0, puddles=None, tin_drops=None,
              smog=0.0, swept=0.0, cam=None):
    p = C.pal(weather)
    vx, vy, vz = cam or VIEWS.get(view, VIEWS["wide"])
    with K.camera(cv, vx, vy, vz):
        C.blit(cv, _back(weather))
        if smog > 0:
            WF.smog_blanket(cv, t, smog, top=330, bottom=560, swept=swept)
        C.blit(cv, _mid(weather))
        if puddles or (puddles is None and C.is_wet(weather)):
            for (x, y, rx) in ((520, 960, 150), (1240, 900, 110), (880, 1010, 90), (1700, 1000, 130)):
                C.puddle(cv, x, y, rx, rx * 0.18, p, t)
        if steam_on > 0:
            ox, oy = ANCHORS["cooker"]
            lx, ly, lr = ANCHORS["loom"]
            WF.steam(cv, t, ox + 10, oy - 60, steam_on, spin=spin, loom=(lx, ly, lr * 0.7))
        for td in (tin_drops or []):
            _tin_drop(cv, t, td, p)
        if rain > 0:
            WF.rain(cv, t, rain, wind=0.15, rect=(0, 0, W, H),
                    splash_y=lambda x: 700 + (x * 37 % 340))
        if weather == "heat":
            WF.heat_shimmer(cv, t, (0, 260, W, 600), 0.6)


def trunk_keyholes(x, y, s):
    """Screen positions of the 3 keyholes on the Monsoon Trunk lid (wide triangle)."""
    return [(x - 230 * s, y - 250 * s), (x + 230 * s, y - 250 * s), (x, y - 325 * s)]


def _peacock(c, x, y, s, col, col2):
    for k in range(7):
        a = math.radians(-150 + k * 20)
        c.drawCircle(x + math.cos(a) * 34 * s, y + math.sin(a) * 34 * s, 9 * s, fill(col2))
        c.drawCircle(x + math.cos(a) * 34 * s, y + math.sin(a) * 34 * s, 4 * s, fill(col))
    c.drawPath(ellipse(x, y, 10 * s, 16 * s), fill(col))
    c.drawCircle(x + 6 * s, y - 20 * s, 6 * s, fill(col))
    c.drawLine(x + 6 * s, y - 26 * s, x + 6 * s, y - 34 * s, stroke(col, 2 * s))


def _swirl(c, x, y, s, col):
    path = skia.Path()
    for i in range(40):
        a = i * 0.35
        rr = (4 + i * 0.9) * s
        (path.moveTo if i == 0 else path.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7)
    c.drawPath(path, stroke(col, 4 * s))


def draw_monsoon_trunk(cv, x, y, s, t, lid=0.0, keys=(0.0, 0.0, 0.0), glow=0.0, weather="night"):
    p = C.pal(weather)
    iron, iron_hi, iron_dk = "#1f3a32", "#2f5648", "#12221d"
    carve = "#3f6e5c"
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    w, h, d = 520, 230, 120         # front face width/height, top depth (3/4 view)
    # shadow
    cv.drawPath(ellipse(0, 0, w * 0.6, 26), fill("#000000", 0.25))
    # body front face
    front = rrect(-w / 2, -h, w, h, 14)
    cv.drawPath(front, fill(iron))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 20, -h + 14, w - 40, 18), fill(iron_hi))
    # carvings: clouds + peacocks
    for k in range(3):
        _swirl(cv, -150 + k * 150, -h * 0.55, 1.2, carve)
    _peacock(cv, -190, -60, 1.1, carve, iron_hi)
    _peacock(cv, 190, -60, 1.1, carve, iron_hi)
    # iron bands + rivets
    for bx in (-w / 2 + 40, 0, w / 2 - 40):
        cv.drawRect(skia.Rect.MakeXYWH(bx - 10, -h, 20, h), fill(iron_dk))
        for k in range(5):
            cv.drawCircle(bx, -h + 20 + k * 46, 4.5, fill(iron_hi))
    cv.drawPath(front, stroke(p["line"], 4))
    # light spilling from the open lid
    open_k = K.ease_out(clamp(lid))
    top_y = -h
    if open_k > 0.01:
        mouth = poly([(-w / 2 + 6, top_y), (w / 2 - 6, top_y), (w / 2 - 26, top_y - d * 0.9),
                      (-w / 2 + 26, top_y - d * 0.9)])
        cv.drawPath(mouth, fill("#a8c6ff", 0.7 + 0.3 * glow))
        cv.drawCircle(0, top_y - d * 0.4, 360 * open_k, K.rad_a((0, top_y - d * 0.4), 360 * open_k,
                                                                    [("#cfe0ff", 0.5 * glow + 0.25), ("#cfe0ff", 0)]))
        # slate cloud welling up out of the trunk: one merged billowing silhouette
        cpath = None
        for k in range(8):
            u = clamp(open_k * 1.4 - k * 0.07)
            if u <= 0:
                continue
            cx = math.sin(k * 2.1 + t * 0.6) * 150 * u
            cy = top_y - d * 0.4 - u * (80 + k * 50)
            rr = (60 + k * 16) * u
            q = skia.Path(); q.addCircle(cx, cy, rr)
            cpath = q if cpath is None else (skia.Op(cpath, q, skia.PathOp.kUnion_PathOp) or cpath)
        if cpath is not None:
            sh = skia.Path(cpath); sh.offset(8, 12)
            cv.drawPath(sh, fill("#141c2c"))
            cv.drawPath(cpath, fill("#3d4e66"))
            inner = skia.Path(cpath); inner.offset(-12, 16)
            rim = skia.Op(cpath, inner, skia.PathOp.kDifference_PathOp)
            if rim is not None:
                cv.drawPath(rim, fill("#9bb4d4", 0.9))
    # lid: hinged at the back; closed = top face parallelogram; opening = rotates up/back
    ang = open_k * 100
    cv.save()
    cv.translate(0, top_y - d * 0.9)
    lid_h = d * math.cos(math.radians(ang)) * 0.9 + 1
    lid_rise = d * math.sin(math.radians(ang)) * 1.6
    lid_face = poly([(-w / 2 + 26, 0), (w / 2 - 26, 0), (w / 2 - 4, lid_h - lid_rise * 0.0),
                     (-w / 2 + 4, lid_h)])
    if open_k > 0.02:
        lid_face = poly([(-w / 2 + 26, 0), (w / 2 - 26, 0), (w / 2 - 20, -lid_rise), (-w / 2 + 20, -lid_rise)])
    cv.drawPath(lid_face, fill(iron_hi if open_k < 0.02 else iron))
    if open_k >= 0.02:
        # underside of the open lid: iron bands, rivets, a carved cloud
        for bx in (-w / 2 + 60, 0, w / 2 - 60):
            cv.drawPath(poly([(bx - 9, 0), (bx + 9, 0), (bx + 9, -lid_rise), (bx - 9, -lid_rise)]), fill(iron_dk))
        _swirl(cv, -120, -lid_rise * 0.5, 0.9, carve)
        _swirl(cv, 120, -lid_rise * 0.5, 0.9, carve)
        cv.drawLine(-w / 2 + 30, -lid_rise * 0.08, w / 2 - 30, -lid_rise * 0.08, stroke("#a8c6ff", 3, 0.6 * glow))
    cv.drawPath(lid_face, stroke(p["line"], 4))
    if open_k < 0.02:
        _swirl(cv, 0, lid_h * 0.55, 1.0, carve)
    cv.restore()
    # keyholes + keys (only meaningful while the lid is closed)
    for i, (kx, ky) in enumerate(trunk_keyholes(0, 0, 1)):
        kx, ky = kx * 0.9, ky * 0.62 - 12   # project onto the lid face
        cv.drawCircle(kx, ky, 18, fill("#c9a24a"))
        cv.drawCircle(kx, ky, 18, stroke(p["line"], 3))
        cv.drawCircle(kx, ky - 3, 5, fill("#111"))
        cv.drawRect(skia.Rect.MakeXYWH(kx - 2.5, ky, 5, 9), fill("#111"))
        kv = keys[i] if i < len(keys) else 0
        if kv > 0:
            slide = clamp(kv / 0.5)
            turn = clamp((kv - 0.5) / 0.5) * 90
            cv.save(); cv.translate(kx, ky - 40 * (1 - slide)); cv.rotate(turn)
            cv.drawRect(skia.Rect.MakeXYWH(-4, -70, 8, 70), fill("#5a5e66"))
            cv.drawCircle(0, -82, 18, stroke("#5a5e66", 7))
            cv.drawRect(skia.Rect.MakeXYWH(-4, -70, 8, 70), stroke(p["line"], 2))
            cv.restore()
            if kv >= 1:
                cv.drawCircle(kx, ky, 26, stroke("#cfe0ff", 3, 0.8))
    cv.restore()


def draw_tin_trunk(cv, x, y, s, t, open=0.0, chains=1.0, weather="night"):
    p = C.pal(weather)
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    w, h = 300, 160
    cv.drawPath(ellipse(0, 0, w * 0.6, 16), fill("#000000", 0.25))
    tin, tin_hi, tin_dk = "#a9aeb4", "#d4d8dc", "#7a8088"
    body = rrect(-w / 2, -h, w, h, 10)
    cv.drawPath(body, fill(tin))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, -h + 12, w - 28, 12), fill(tin_hi))
    for bx in (-w / 2 + 30, w / 2 - 30):
        cv.drawRect(skia.Rect.MakeXYWH(bx - 8, -h, 16, h), fill(tin_dk))
    _swirl(cv, 0, -h * 0.5, 1.4, "#8a4a22")          # painted swirling brown cloud
    _swirl(cv, 30, -h * 0.45, 0.9, "#b8692f")
    cv.drawPath(body, stroke(p["line"], 3.4))
    # lid lifting a crack + dust roaring out
    lift = K.ease_out(clamp(open)) * 26
    lidp = rrect(-w / 2 - 8, -h - 30 - lift, w + 16, 34, 8)
    if open > 0:
        r = K.rng(int(t * 30))
        for k in range(14):
            a = math.radians(-160 + k * 10 + r.uniform(-5, 5))
            L = (120 + r.uniform(0, 200)) * open
            sx, sy = r.uniform(-w / 2, w / 2), -h - 4
            for j in range(5):
                f = (j + 1) / 5
                px, py = sx + math.cos(a) * L * f, sy + math.sin(a) * L * 0.6 * f - 30 * open * f
                rr = (10 + 26 * f) * (0.6 + 0.4 * open)
                cv.drawCircle(px + 4, py + 5, rr, fill("#7a3e1c", 0.5))
                cv.drawCircle(px, py, rr, fill("#b8692f", 0.75))
    cv.drawPath(lidp, fill(tin_hi)); cv.drawPath(lidp, stroke(p["line"], 3))
    # chains: wrapped (1) .. slack on the floor (0)
    if chains > 0.02:
        for k in range(2):
            x0 = -w / 2 + 70 + k * 160
            for j in range(9):
                yy = lerp(-h - 34, 0, j / 8)
                cy = yy + (1 - chains) * (0 - yy) * 0.9
                cx = x0 + (1 - chains) * (j * 14 - 60)
                cv.drawPath(ellipse(cx, cy, 8, 12), stroke("#6a6e76", 4, chains * 0.6 + 0.4))
        # padlock
        if chains > 0.5:
            lk = rrect(-22, -h - 12, 44, 40, 6)
            cv.drawPath(lk, fill("#d8b04a")); cv.drawPath(lk, stroke(p["line"], 2.6))
            cv.drawPath(smooth_path([(-12, -h - 10), (-12, -h - 32), (12, -h - 32), (12, -h - 10)], close=False,
                                    tension=0.4), stroke("#9aa0aa", 6))
    else:
        for j in range(16):   # slack heap on the floor
            cv.drawPath(ellipse(-w / 2 - 30 + j * 10, 4 + (j % 3) * 4, 8, 6), stroke("#6a6e76", 4))
    cv.restore()
