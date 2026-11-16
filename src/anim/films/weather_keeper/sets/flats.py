"""Interiors: Tara's flat and Meghnath's flat.

draw_tara_flat(cv, t, weather='heat'|'night', fan=0.0, door=1.0, cam=None)
  Shutters closed, harsh white light stripes through the slats across the cool floor tiles (Ishaan lies on
  them), a windowsill at right (Captain the pigeon's perch), a low table + stool (Tara writing), and at the
  back a HALF-OPEN DOOR through which Dadi's bed and a ceiling fan that isn't turning are seen.
  fan: speed of the ceiling fans (0 = power cut). door 0..1 how far Dadi's door is open.
  weather='night': a dim blue room, a candle/lantern glow on the table.
  Anchors: FLOOR_Y = 1010; ISHAAN_FLOOR = (x, y, s) for lying on the tiles; SILL_POS = (x, y) pigeon perch;
    TABLE_SEAT = (x, y, s) Tara sitting (legs='sit') at the table; DADI_DOOR = (x, y, w, h) the door gap;
    DADI_BED = (x, y, s) bed surface point visible through the door (the cast draws Dadi);
    BEDSIDE_SEAT = (x, y, s) for Tara sitting beside Dadi in the night scene (view='dadi').
  view: 'room' (default) | 'dadi' (a medium inside Dadi's room: bed, still fan, window, for sc6 night).
draw_meghnath_flat(cv, t, weather='night'|'monsoon_night'|'dawn_wet', curtain=0.0, rain_glass=0.0, cam=None)
  Bedroom: bed with blanket, bedside table (PHOTO_SPOT for Varsha's photo, drawn by the cast), window with
  a curtain that blows in (curtain 0..1), drops on the glass (rain_glass 0..1).
  Anchors: BED = (x, y, s) bed-surface point for him lying (head end at left); PHOTO_SPOT = (x, y);
    WINDOW = (x, y, w, h); STAND_WINDOW = (x, y, s) where he stands to lean out.
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF

FLOOR_Y = 1010
ISHAAN_FLOOR = (980, 960, 1.5)
SILL_POS = (1650, 520)
TABLE_SEAT = (545, 830, 1.45)
DADI_DOOR = (1060, 230, 240, 470)
DADI_BED = (1180, 610, 0.65)
BEDSIDE_SEAT = (1130, 860, 1.5)

BED = (900, 700, 1.4)
PHOTO_SPOT = (1490, 660)
WINDOW = (380, 160, 520, 520)
STAND_WINDOW = (640, 1000, 1.7)


def _fan(c, x, y, r, t, speed, col, line):
    c.drawLine(x, y - 90, x, y, stroke(col, 6))
    ang = t * 600 * speed
    c.save(); c.translate(x, y); c.scale(1, 0.28); c.rotate(ang)
    for k in range(3):
        c.rotate(120)
        c.drawPath(rrect(0, -14, r, 28, 12), fill(col))
        c.drawPath(rrect(0, -14, r, 28, 12), stroke(line, 2))
    c.restore()
    c.drawPath(ellipse(x, y, 26, 12), fill(K.shade(col, -0.2)))
    c.drawPath(ellipse(x, y, 26, 12), stroke(line, 2))


def _tara_static(weather):
    p = C.pal(weather)
    night = C.is_night(weather)
    wall = "#d8cdb6" if not night else "#3c4466"
    wall_lo = "#b9c9c0" if not night else "#2e3a52"

    def draw(c):
        c.drawRect(skia.Rect.MakeWH(W, H), fill(wall))
        c.drawRect(skia.Rect.MakeLTRB(0, 620, W, FLOOR_Y), fill(wall_lo))
        c.drawLine(0, 620, W, 620, stroke(p["line"], 2))
        # tiled floor in perspective
        c.drawRect(skia.Rect.MakeLTRB(0, FLOOR_Y - 120, W, H), fill("#cfd8d4" if not night else "#2c364c"))
        for k in range(-8, 20):
            c.drawLine(960 + k * 70, FLOOR_Y - 120, 960 + k * 160, H, stroke("#aebcb8" if not night else "#232c40", 2))
        for yy in (FLOOR_Y - 80, FLOOR_Y - 20, FLOOR_Y + 50):
            c.drawLine(0, yy, W, yy, stroke("#aebcb8" if not night else "#232c40", 2))
        # Dadi's room through the half-open door
        x, y, w, h = DADI_DOOR
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill("#c4b49a" if not night else "#232a40"))
        c.drawRect(skia.Rect.MakeXYWH(x + 40, y + 300, w - 60, 90), fill("#e8e0d0" if not night else "#3a4460"))  # bed
        c.drawRect(skia.Rect.MakeXYWH(x + 30, y + 390, w - 40, 14), fill("#7a5a3a"))
        _fan(c, x + w * 0.55, y + 60, 70, 0, 0, "#9a948a", p["line"])
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), stroke(p["line"], 3))
        # the door leaf, half open
        c.drawPath(poly([(x + w, y), (x + w + 90, y + 30), (x + w + 90, y + h - 10), (x + w, y + h)]), fill("#8a5a3a"))
        c.drawPath(poly([(x + w, y), (x + w + 90, y + 30), (x + w + 90, y + h - 10), (x + w, y + h)]),
                   stroke(p["line"], 3))
        # shuttered window (right) + sill
        wx, wy, ww, wh = 1480, 200, 360, 320
        C.rect_line(c, wx - 20, wy - 20, ww + 40, wh + 40, "#e8e0cc" if not night else "#4a5478", p["line"], 3)
        for k in range(12):
            c.drawRect(skia.Rect.MakeXYWH(wx, wy + k * wh / 12, ww, wh / 12 - 6), fill("#6e8a7a" if not night else "#2a3a4a"))
            if not night:
                c.drawRect(skia.Rect.MakeXYWH(wx, wy + k * wh / 12 + wh / 12 - 6, ww, 6), fill("#fffbe8"))
        c.drawRect(skia.Rect.MakeXYWH(wx - 40, wy + wh + 20, ww + 80, 24), fill("#d8cdb6" if not night else "#3c4466"))
        c.drawRect(skia.Rect.MakeXYWH(wx - 40, wy + wh + 20, ww + 80, 24), stroke(p["line"], 2.6))
        # light stripes from the slats across wall and floor
        if not night:
            for k in range(8):
                y0 = 640 + k * 46
                c.drawPath(poly([(1480, wy + 40 + k * 26), (1480, wy + 52 + k * 26), (200, y0 + 26 + k * 10),
                                 (200, y0 + k * 10)]), fill("#fffbe8", 0.28))
        # low table + stool, notebook stand-in shapes
        C.rect_line(c, 380, 760, 300, 26, "#9a6a40", p["line"], 2.6)
        for lx in (400, 650):
            c.drawRect(skia.Rect.MakeXYWH(lx, 786, 14, 110), fill("#7a5030"))
        C.rect_line(c, 470, 820, 150, 18, "#7a5030", p["line"], 2)   # stool
        # ceiling fan (still) in this room + a calendar shape + a framed print
        C.rect_line(c, 200, 240, 160, 200, "#f2ecd8", p["line"], 2.4)
        c.drawCircle(280, 330, 40, fill("#f2b33a"))
    return C.cached(("tara_flat", weather), draw)


def _dadi_static(weather):
    p = C.pal(weather)
    night = C.is_night(weather)

    def draw(c):
        c.drawRect(skia.Rect.MakeWH(W, H), fill("#c4b49a" if not night else "#28304a"))
        c.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), fill("#b0a080" if not night else "#20283c"))
        # window with moonlight / heat light
        C.rect_line(c, 1300, 160, 380, 340, "#1c2440" if night else "#fff6dc", p["line"], 3)
        for k in range(1, 4):
            c.drawLine(1300 + k * 95, 160, 1300 + k * 95, 500, stroke(p["line"], 4))
        # bed
        C.rect_line(c, 300, 640, 1000, 140, "#e8e0d0" if not night else "#4a5478", p["line"], 3)
        C.rect_line(c, 280, 780, 1040, 30, "#7a5a3a", p["line"], 2.6)
        C.rect_line(c, 240, 540, 60, 280, "#7a5a3a", p["line"], 2.6)
        c.drawPath(ellipse(400, 640, 90, 34), fill("#f4f0e6" if not night else "#6a7494"))   # pillow
    return C.cached(("dadi_room", weather), draw)


def draw_tara_flat(cv, t, weather="heat", fan=0.0, door=1.0, view="room", cam=None):
    p = C.pal(weather)
    with C.apply_cam(cv, cam):
        if view == "dadi":
            C.blit(cv, _dadi_static(weather))
            _fan(cv, 800, 160, 210, t, fan, "#9a948a", p["line"])
            if C.is_night(weather):
                cv.drawRect(skia.Rect.MakeWH(W, H), fill("#0a0e1c", 0.25))
            return
        C.blit(cv, _tara_static(weather))
        _fan(cv, 600, 120, 190, t, fan, "#9a948a", p["line"])
        if C.is_night(weather):
            cv.drawCircle(520, 740, 220, K.rad_a((520, 740), 220, [("#ffcf80", 0.35), ("#ffcf80", 0)]))
        else:
            WF.heat_shimmer(cv, t, (0, 0, W, 600), 0.25)


def _megh_static(weather):
    p = C.pal(weather)
    night = C.is_night(weather)
    wall = "#3a4462" if night else ("#c8d2cc" if weather == "dawn_wet" else "#d8cdb6")

    def draw(c):
        c.drawRect(skia.Rect.MakeWH(W, H), fill(wall))
        c.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), fill(K.shade(wall, -0.15)))
        c.drawLine(0, 900, W, 900, stroke(p["line"], 2.4))
        x, y, w, h = WINDOW
        sky = "#1c2638" if night else ("#a9bfd0" if weather == "dawn_wet" else "#f4ecd8")
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(sky))
        if weather == "dawn_wet":
            for k in range(5):
                C.flat_building(c, x + k * 110, y + h, 100, 160 + (k % 3) * 40, "#8fa3a8", "#66787a", seed=k)
        for k in range(1, 3):
            c.drawLine(x + k * w / 3, y, x + k * w / 3, y + h, stroke(p["line"], 5))
        c.drawLine(x, y + h / 2, x + w, y + h / 2, stroke(p["line"], 5))
        C.rect_line(c, x - 24, y - 24, w + 48, 24, K.shade(wall, -0.2), p["line"], 2.4)
        C.rect_line(c, x - 30, y + h, w + 60, 26, K.shade(wall, -0.2), p["line"], 2.4)
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), stroke(p["line"], 4))
        # bed (head at left) + blanket + pillow
        C.rect_line(c, 560, 700, 820, 130, "#e8e0d0" if not night else "#59628a", p["line"], 3)
        C.rect_line(c, 540, 830, 860, 30, "#6a4a30", p["line"], 2.6)
        C.rect_line(c, 520, 560, 60, 300, "#6a4a30", p["line"], 2.6)
        c.drawPath(ellipse(670, 700, 100, 36), fill("#f4f0e6" if not night else "#7a84a8"))
        c.drawPath(ellipse(670, 700, 100, 36), stroke(p["line"], 2.2))
        # bedside table
        C.rect_line(c, PHOTO_SPOT[0] - 110, PHOTO_SPOT[1], 220, 24, "#7a5030", p["line"], 2.6)
        C.rect_line(c, PHOTO_SPOT[0] - 96, PHOTO_SPOT[1] + 24, 192, 210, "#8a5a38", p["line"], 2.6)
        c.drawCircle(PHOTO_SPOT[0], PHOTO_SPOT[1] + 120, 6, fill("#d8b04a"))
        # brown cardigan hanging on a hook (body + two hanging sleeves + buttons) + walking stick
        c.drawCircle(1740, 290, 8, fill(p["metal"]))
        cardi = poly([(1700, 300), (1780, 300), (1810, 330), (1800, 560), (1680, 560), (1670, 330)])
        c.drawPath(cardi, fill("#8a5a38")); c.drawPath(cardi, stroke(p["line"], 2.4))
        for sx in (1655, 1800):
            sl = poly([(sx, 330), (sx + 26, 330), (sx + 22, 520), (sx - 2, 520)])
            c.drawPath(sl, fill("#7a4e30")); c.drawPath(sl, stroke(p["line"], 2.2))
        c.drawLine(1740, 300, 1740, 560, stroke(p["line"], 2))
        for k in range(4):
            c.drawCircle(1748, 340 + k * 50, 5, fill("#d8c8a0"))
        c.drawLine(1820, 880, 1860, 560, stroke("#6a4a30", 8))
    return C.cached(("megh_flat", weather), draw)


def draw_meghnath_flat(cv, t, weather="night", curtain=0.0, rain_glass=0.0, cam=None):
    p = C.pal(weather)
    with C.apply_cam(cv, cam):
        C.blit(cv, _megh_static(weather))
        x, y, w, h = WINDOW
        if rain_glass > 0:
            cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
            WF.rain(cv, t, rain_glass, wind=0.2, rect=(x, y, x + w, y + h), n=int(120 * rain_glass), splash=False)
            cv.restore()
            WF.drops_on_glass(cv, t, (x, y, x + w, y + h), rain_glass)
        # curtain: a drape hanging at the window's right edge; its bottom swings into the room (curtain>0)
        blow = clamp(curtain)
        wave = math.sin(t * 3) * 24 * blow
        tl, tr = (x + w - 150, y - 20), (x + w + 30, y - 20)
        br = (x + w + 30 + 360 * blow + wave, y + h + 40 - 140 * blow)
        bl = (x + w - 150 + 280 * blow + wave * 0.6, y + h + 40 - 70 * blow)
        cpath = skia.Path()
        cpath.moveTo(*tl); cpath.lineTo(*tr)
        cpath.cubicTo(tr[0] + 40 * blow, tr[1] + h * 0.4, br[0] - 60 * blow, br[1] - h * 0.3, *br)
        cpath.quadTo((br[0] + bl[0]) / 2, (br[1] + bl[1]) / 2 + 30, *bl)
        cpath.cubicTo(bl[0] - 80 * blow, bl[1] - h * 0.3, tl[0] + 10 * blow, tl[1] + h * 0.4, *tl)
        cpath.close()
        cv.drawPath(cpath, fill("#d9897a" if not C.is_night(weather) else "#8a5a6a"))
        for k in range(1, 6):
            f = k / 6
            top = (lerp(tl[0], tr[0], f), tl[1])
            bot = (lerp(bl[0], br[0], f), lerp(bl[1], br[1], f))
            cv.drawLine(*top, *bot, stroke("#b06a5e" if not C.is_night(weather) else "#6a4252", 2.4))
        cv.drawPath(cpath, stroke(p["line"], 2.6))
        cv.drawLine(x - 40, y - 24, x + w + 60, y - 24, stroke("#6a4a30", 6))   # curtain rod
        if C.is_night(weather):
            cv.drawRect(skia.Rect.MakeWH(W, H), fill("#0a0e1c", 0.2))
