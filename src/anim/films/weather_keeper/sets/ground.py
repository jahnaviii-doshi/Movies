"""Colony cricket ground, seen from ABOVE (high oblique, as if from the roof).

draw_ground(cv, t, weather='heat', hail=0.0, stumps_fall=0.0, batsman_run=0.0, players=True, cam=None)
  Dusty pitch strip in a parched field, stumps at both ends, tiny flat player figures (simple shapes),
  a boundary of round flat tree canopies and the edges of neighbouring blocks.
  hail 0..1: a bedsheet-sized hailstorm patch over the near stumps (the black cloud itself is drawn by
      the parent at CLOUD_POS); stumps_fall 0..1 knocks the near stumps over; batsman_run 0..1 makes
      the batsman run in panicked circles; the fielders scatter as hail rises.
Anchors: STUMPS = (x, y) near stumps; FAR_STUMPS; PITCH = (x, y, w, h); CLOUD_POS = (x, y) where the
  hail cloud hangs (just above the hail patch); HAIL_RECT = (x0, y0, x1, y1).
  draw_player(cv, x, y, s, t, run=0..1, col, helmet=False, facing=1) tiny top-ish figure, for reuse.
"""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import W, H, fill, stroke, poly, rrect, ellipse, smooth_path, lerp, clamp
from . import _common as C
from . import weather_fx as WF

PITCH = (860, 300, 200, 640)
STUMPS = (960, 830)
FAR_STUMPS = (960, 360)
CLOUD_POS = (960, 560)
HAIL_RECT = (760, 640, 1160, 900)


def _static(weather):
    p = C.pal(weather)

    def draw(c):
        c.drawRect(skia.Rect.MakeWH(W, H), fill("#d9b77e" if weather == "heat" else p["ground"]))
        C.bands(c, 0, 0, W, H, ["#d2ad70", "#dcbb84", "#e3c492"] if weather == "heat" else
                [p["ground_shade"], p["ground"], K.shade(p["ground"], 0.05)])
        r = K.rng(6)
        for i in range(30):   # dry grass tufts + bald patches
            x, y = r.uniform(0, W), r.uniform(0, H)
            c.drawPath(ellipse(x, y, r.uniform(30, 90), r.uniform(12, 30)), fill("#c9a36a", 0.6))
            c.drawLine(x, y, x + 6, y - 12, stroke("#9aa46a", 2))
        # boundary rope (oval)
        c.drawPath(ellipse(960, 620, 820, 420), stroke("#f4f0e6", 4, 0.7))
        # pitch strip
        x, y, w, h = PITCH
        C.rect_line(c, x, y, w, h, "#ead6a8", p["line"], 2.4)
        for yy in (y + 90, y + h - 90):
            c.drawLine(x - 30, yy, x + w + 30, yy, stroke("#ffffff", 4))
        # far stumps (static)
        fx, fy = FAR_STUMPS
        for dx in (-10, 0, 10):
            c.drawLine(fx + dx, fy, fx + dx, fy - 34, stroke("#f4ecd2", 5))
        # boundary: trees + block edges
        for i in range(14):
            tx = i * 150 + r.uniform(-30, 30)
            ty = r.choice([40, 1060])
            for (dx, dy, rr) in ((0, 0, 70), (-50, 20, 50), (50, 16, 55)):
                c.drawCircle(tx + dx + 6, ty + dy + 8, rr, fill("#5a6a3a"))
                c.drawCircle(tx + dx, ty + dy, rr, fill("#7c8a4a" if weather == "heat" else p["green"]))
        for (bx, by, bw, bh) in ((-60, 200, 230, 520), (1750, 160, 260, 600)):
            c.drawRect(skia.Rect.MakeXYWH(bx, by, bw, bh), fill(p["wall"]))
            c.drawRect(skia.Rect.MakeXYWH(bx, by, bw, bh), stroke(p["line"], 2.6))
            for k in range(8):
                c.drawRect(skia.Rect.MakeXYWH(bx + 40, by + 30 + k * 60, bw - 80, 26), fill(p["window"], 0.6))
    return C.cached(("ground", weather), draw)


def draw_player(cv, x, y, s, t, run=0.0, col="#f4f4f0", helmet=False, facing=1):
    """Tiny figure seen from above-ish: shadow, legs, body, head (+ helmet)."""
    ph = t * 10
    cv.drawPath(ellipse(x + 4 * s, y + 4 * s, 12 * s, 5 * s), fill("#000000", 0.2))
    for d in (-1, 1):
        sw = math.sin(ph + (d > 0) * math.pi) * 6 * s * run
        cv.drawLine(x + d * 4 * s, y - 8 * s, x + d * 4 * s + sw, y, stroke("#3a3a44", 4 * s))
    cv.drawPath(rrect(x - 8 * s, y - 30 * s, 16 * s, 24 * s, 6 * s), fill(col))
    cv.drawPath(rrect(x - 8 * s, y - 30 * s, 16 * s, 24 * s, 6 * s), stroke("#2a1e22", 1.6 * s))
    cv.drawCircle(x, y - 38 * s, 8 * s, fill("#b77b55"))
    if helmet:
        cv.drawPath(ellipse(x, y - 41 * s, 9 * s, 7 * s), fill("#2f5fa8"))
        cv.drawLine(x - 8 * s, y - 37 * s, x + 8 * s, y - 37 * s, stroke("#d8dce2", 1.6 * s))
    else:
        cv.drawCircle(x, y - 42 * s, 6 * s, fill("#2a1e22"))


def draw_ground(cv, t, weather="heat", hail=0.0, stumps_fall=0.0, batsman_run=0.0, players=True, cam=None):
    with C.apply_cam(cv, cam):
        C.blit(cv, _static(weather))
        sx, sy = STUMPS
        # near stumps (can fall)
        for i, dx in enumerate((-12, 0, 12)):
            ang = K.ease_out(clamp(stumps_fall * 1.5 - i * 0.2)) * (70 + i * 20) * (1 if dx >= 0 else -1)
            cv.save(); cv.translate(sx + dx, sy); cv.rotate(ang)
            cv.drawLine(0, 0, 0, -40, stroke("#f4ecd2", 6))
            cv.drawLine(0, 0, 0, -40, stroke("#2a1e22", 1.2))
            cv.restore()
        if players:
            scatter = clamp(hail * 1.5)
            fielders = [(560, 420, "#f4f4f0"), (1380, 460, "#f4f4f0"), (700, 760, "#f4f4f0"), (1300, 780, "#f4f4f0"),
                        (960, 250, "#f4f4f0"), (430, 610, "#e8a3a0"), (1500, 650, "#6f9ac0")]
            for i, (fx, fy, col) in enumerate(fielders):
                dx, dy = fx - sx, fy - sy
                dist = math.hypot(dx, dy) + 1
                runk = scatter * (0.6 + 0.4 * math.sin(i))
                px = fx + dx / dist * 260 * runk + math.sin(t * 2 + i) * 4
                py = fy + dy / dist * 160 * runk
                draw_player(cv, px, py, 1.2, t, run=scatter + 0.1, col=col)
            # bowler at the far end, batsman at the near crease
            draw_player(cv, 960, 420, 1.25, t, run=0.2, col="#f4f4f0")
            if batsman_run > 0:
                a = t * 7
                bx, by = sx + math.cos(a) * 80 * batsman_run, sy - 20 + math.sin(a) * 40 * batsman_run
            else:
                bx, by = sx - 26, sy - 10
            draw_player(cv, bx, by, 1.35, t, run=batsman_run, col="#f4f4f0", helmet=True)
            cv.drawLine(bx + 10, by - 26, bx + 26, by - 6, stroke("#c9a46a", 5))   # bat
        if hail > 0:
            x0, y0, x1, y1 = HAIL_RECT
            # shadow of the cloud on the ground
            cv.drawPath(ellipse((x0 + x1) / 2, (y0 + y1) / 2 + 30, (x1 - x0) / 2, (y1 - y0) / 3),
                        fill("#000000", 0.18 * hail))
            WF.hail(cv, t, (x0, y0 - 200, x1, y1), hail)
