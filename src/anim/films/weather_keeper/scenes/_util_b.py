"""Helpers for WK sc04/sc05 (fork B): rig-space -> world positions, beds, small drawn props."""
from __future__ import annotations

import math

import skia

from .... import core as K
from ....core import fill, stroke, ellipse, smooth_path, poly, lerp, clamp
from ....rig.human import Pose
from ..rig import CAST

BEDS = {"heat_bed", "night_bed_delhi", "workshop_ambience", "rain_roar", "crickets_bed", "night_bed", "day_bed"}


def bed(name, dur=10.0, gain=-14):
    from ....timeline import Sfx
    return Sfx(name, 0.0, gain, dur=dur)


def finalize(shots, scene):
    """Sequential ids S{scene}_SH{n}; beds stretched to each shot's resolved length."""
    for i, s in enumerate(shots):
        s.id = f"S{scene:02d}_SH{i + 1:02d}"
        if s.duration is None:
            s.resolve()
        for x in s.sfx:
            if x.name in BEDS:
                x.dur = s.duration + 0.6
    return shots


# ------------------------------------------------------------------ rig-space helpers
def _sit_off(rig, sit):
    return (-rig.hip_y - 4) if sit else 0.0


def head_world(who, x, y, s, flip=False, turn=0.35, sit=False):
    """World centre of the character's head."""
    rig = CAST[who]
    hx, hy = rig.head_anchor(Pose(turn=turn))
    sx = -1 if flip else 1
    return (x + hx * s * sx, y + (hy + _sit_off(rig, sit)) * s)


def head_top(who, x, y, s, flip=False, turn=0.35, sit=False):
    hx, hy = head_world(who, x, y, s, flip, turn, sit)
    return (hx, hy - CAST[who].head_r * s)


def hand_world(who, x, y, s, side, arms, flip=False, sit=False):
    """Forward kinematics matching rig.human.Human.draw_arm (no lean)."""
    rig = CAST[who]
    sh_deg, el_deg = arms
    sgn = -1 if side == "l" else 1
    sx, sy = sgn * (rig.shoulder_w + 4), rig.neck_y + 16
    a1 = math.radians(sh_deg) * sgn
    ex, ey = sx + math.sin(a1) * rig.upper_arm, sy + math.cos(a1) * rig.upper_arm
    a2 = a1 - math.radians(el_deg) * sgn
    hx, hy = ex + math.sin(a2) * rig.fore_arm, ey + math.cos(a2) * rig.fore_arm
    fx = -1 if flip else 1
    return (x + hx * s * fx, y + (hy + _sit_off(rig, sit)) * s)


def cam(cv, cx, cy, z=1.0, t=0.0, shake=0.0):
    """Clamped camera (never shows past the 1920x1080 world edges)."""
    hw, hh = K.W / (2 * z), K.H / (2 * z)
    cx = clamp(cx, hw, K.W - hw) if z >= 1 else K.W / 2
    cy = clamp(cy, hh, K.H - hh) if z >= 1 else K.H / 2
    return K.camera(cv, cx, cy, z, t=t, shake=shake)


def clamp_view(cx, cy, z):
    hw, hh = K.W / (2 * z), K.H / (2 * z)
    return (clamp(cx, hw, K.W - hw), clamp(cy, hh, K.H - hh), z)


# ------------------------------------------------------------------ drawn bits
def breeze_ribbon(cv, p0, p1, t, color="#bfe0ff", a=1.0, n=3, bend=120, width=5):
    """Swirling ribbons of wind travelling from p0 to p1 (dash phase animates)."""
    for k in range(n):
        off = (k - (n - 1) / 2) * 26
        mx, my = (p0[0] + p1[0]) / 2 + off, (p0[1] + p1[1]) / 2 - bend + off * 0.4
        path = skia.Path()
        path.moveTo(p0[0], p0[1] + off * 0.3)
        path.quadTo(mx, my + math.sin(t * 3 + k) * 20, p1[0], p1[1])
        p = stroke(color, width - k, a * (0.85 - k * 0.2))
        p.setPathEffect(skia.DashPathEffect.Make([60, 34], -t * 260 - k * 40))
        cv.drawPath(path, p)
    # little curls along the way
    for k in range(4):
        u = ((t * 0.7 + k / 4) % 1.0)
        x, y = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - math.sin(u * math.pi) * bend * 0.7
        cv.drawArc(skia.Rect.MakeXYWH(x - 14, y - 14, 28, 28), t * 400 + k * 90, 260, False,
                   stroke(color, 3, a * math.sin(u * math.pi)))


def dark_cloud(cv, x, y, s, t, rattle=1.0, dark=1.0, a=1.0):
    """Rehan's over-spun cloud: dark, hard, lumpy, rattling like a box of marbles."""
    jx = rattle * 4 * math.sin(t * 47)
    jy = rattle * 3 * math.cos(t * 53)
    cv.save()
    cv.translate(x + jx, y + jy)
    cv.scale(s, s)
    base = K.mix("#e8edf2", "#2b2d3a", dark)
    hi = K.mix("#ffffff", "#4a4d5e", dark)
    lumps = [(0, 0, 54), (-52, 10, 38), (52, 8, 40), (-26, -32, 36), (28, -34, 34), (0, 22, 40), (-70, 26, 24),
             (72, 24, 26)]
    for (dx, dy, r) in lumps:
        cv.drawCircle(dx, dy + 4, r + 3, fill("#14141c", 0.9 * a))
    for i, (dx, dy, r) in enumerate(lumps):
        wob = 1 + 0.05 * math.sin(t * 30 + i * 1.7) * rattle
        cv.drawCircle(dx, dy, r * wob, fill(base, a))
        cv.drawCircle(dx - r * 0.3, dy - r * 0.35, r * 0.35, fill(hi, 0.5 * a))
    # angry knot eyes
    for ex in (-18, 18):
        cv.drawLine(ex - 9, -6 + (3 if ex < 0 else -3) * dark, ex + 9, -6 - (3 if ex < 0 else -3) * dark,
                    stroke("#0b0b10", 4, a * dark))
        cv.drawCircle(ex, 2, 4.5, fill("#f4f4f8" if dark > 0.5 else "#14141c", a))
    # rattling marbles inside (little hail balls flicking)
    r = K.rng(7)
    for i in range(10):
        ph = t * r.uniform(8, 14) + i
        bx, by = r.uniform(-50, 50) + math.sin(ph) * 6, r.uniform(-20, 30) + math.cos(ph * 1.3) * 6
        cv.drawCircle(bx, by, 4, fill("#dfe8f2", 0.6 * a * dark))
    cv.restore()


def notebook_page(cv, x, y, s, t, reveal=1.0, underline=0.0, variant="cloud", a=1.0):
    """Open spiral notebook seen from above with pencil doodles (no words).
    variant 'cloud': arrows + a cloud + wavy 'warm & slow' squiggle + sun with a check.
    variant 'nofast': a fast spiral crossed out + a slow spiral with a tick; underline 0..3 strokes."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    w, h = 620, 420
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 10, -h / 2 + 14, w, h), fill("#000000", 0.25 * a))
    for side in (-1, 1):
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2 if side < 0 else 0, -h / 2, w / 2, h), fill("#fbf6e8", a))
        for k in range(1, 9):
            yy = -h / 2 + k * h / 9
            cv.drawLine(-w / 2 + 20 if side < 0 else 20, yy, -20 if side < 0 else w / 2 - 20, yy,
                        stroke("#b8cfe6", 1.6, a * 0.8))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), stroke("#2a1a1c", 3, a))
    for k in range(10):
        cv.drawCircle(0, -h / 2 + 22 + k * 40, 7, stroke("#6a6f7a", 3, a))
    pen = stroke("#3a3a4a", 4, a)
    pen.setStrokeCap(skia.Paint.kRound_Cap)
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, -w / 2 + w * clamp(reveal), h / 2))
    if variant == "cloud":
        # left page: sun -> arrow -> cloud ; wavy 'warm' lines ; snail = slow
        cv.drawCircle(-230, -100, 26, pen)
        for i in range(8):
            ang = i * math.pi / 4
            cv.drawLine(-230 + math.cos(ang) * 34, -100 + math.sin(ang) * 34, -230 + math.cos(ang) * 48,
                        -100 + math.sin(ang) * 48, pen)
        cv.drawLine(-180, -100, -110, -100, pen)
        cv.drawPath(poly([(-110, -100), (-126, -110), (-126, -90)]), fill("#3a3a4a", a))
        cv.drawPath(smooth_path([(-100, -80), (-90, -118), (-55, -128), (-30, -105), (-5, -110), (5, -80)],
                                close=True), pen)
        for k in range(3):
            yy = 10 + k * 26
            path = skia.Path(); path.moveTo(-250, yy)
            for i in range(8):
                path.quadTo(-235 + i * 30, yy - 12 * (1 if i % 2 else -1), -220 + i * 30, yy)
            cv.drawPath(path, pen)
        # a snail (slow)
        cv.drawCircle(-90, 120, 22, pen)
        cv.drawArc(skia.Rect.MakeXYWH(-102, 108, 24, 24), 0, 300, False, pen)
        cv.drawLine(-120, 142, -50, 142, pen)
        cv.drawLine(-58, 142, -50, 118, pen)
        # right page: loom diagram, spiral with arrows going round slowly
        cv.drawRect(skia.Rect.MakeXYWH(60, -150, 200, 160), pen)
        path = skia.Path()
        for i in range(60):
            ang = i * 0.3
            rr = 6 + i * 1.2
            px, py = 160 + math.cos(ang) * rr, -70 + math.sin(ang) * rr * 0.8
            path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
        cv.drawPath(path, pen)
        cv.drawPath(smooth_path([(90, 80), (110, 50), (160, 44), (200, 60), (240, 50), (260, 90)], close=True), pen)
        cv.drawPath(poly([(150, 130), (165, 150), (200, 105)], close=False), stroke("#2f8f5a", 5, a))
    else:
        # crossed-out fast spiral ; tick on a slow spiral
        for (cx, fast) in ((-160, True), (150, False)):
            path = skia.Path()
            for i in range(80 if fast else 30):
                ang = i * (0.55 if fast else 0.3)
                rr = 4 + i * (1.1 if fast else 2.2)
                px, py = cx + math.cos(ang) * rr, -40 + math.sin(ang) * rr * 0.8
                path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
            cv.drawPath(path, pen)
            if fast:
                for k in range(4):
                    cv.drawLine(cx - 30 + k * 18, -10, cx - 40 + k * 18, -20, stroke("#3a3a4a", 3, a))
        red = stroke("#d23a35", 7, a)
        cv.drawLine(-250, -140, -70, 60, red)
        cv.drawLine(-70, -140, -250, 60, red)
        cv.drawPath(poly([(110, 80), (140, 110), (200, 30)], close=False), stroke("#2f8f5a", 7, a))
    cv.restore()
    # underline strokes (drawn fresh, each one a pencil swipe)
    for k in range(3):
        u = clamp(underline - k)
        if u > 0:
            yy = 120 + k * 22
            cv.drawLine(-260, yy, lerp(-260, -60, K.ease_out(u)), yy + 3 * math.sin(k), stroke("#3a3a4a", 6, a))
    cv.restore()


def pencil(cv, x, y, s=1.0, ang=-35):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-6, -110, 12, 100), fill("#f2c230"))
    cv.drawRect(skia.Rect.MakeXYWH(-6, -110, 12, 100), stroke("#2a1a1c", 2))
    cv.drawPath(poly([(-6, -10), (6, -10), (0, 8)]), fill("#e8c89a"))
    cv.drawPath(poly([(-2, 2), (2, 2), (0, 8)]), fill("#2a2a2a"))
    cv.drawRect(skia.Rect.MakeXYWH(-6, -122, 12, 12), fill("#e88a9a"))
    cv.restore()


def smog_puff(cv, x, y, r, a=1.0, t=0.0):
    for k, (dx, dy, rr) in enumerate(((0, 0, 1.0), (-0.6, 0.2, 0.7), (0.6, 0.15, 0.75), (0.1, -0.5, 0.65))):
        cv.drawCircle(x + dx * r + math.sin(t * 2 + k) * 2, y + dy * r, rr * r, fill("#8a8c90", 0.75 * a))
    cv.drawCircle(x - r * 0.25, y - r * 0.3, r * 0.3, fill("#a8aaae", 0.5 * a))


def sleeve_cuff(cv, x, y, s=1.0, ang=0.0):
    """Meghnath's brown cardigan cuff + left hand, coming in from frame edge (for close-ups)."""
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawPath(K.limb(-420, 60, 0, 0, 110, 90), fill("cardigan"))
    cv.drawPath(K.limb(-420, 60, 0, 0, 110, 90), stroke("#2a1a1c", 4))
    for k in range(5):
        cv.drawLine(-30 + k * 7, -38, -40 + k * 7, 38, stroke("#6a4224", 3))
    cv.drawPath(ellipse(36, 0, 46, 40), fill("megh_skin"))
    cv.drawPath(ellipse(36, 0, 46, 40), stroke("#2a1a1c", 4))
    cv.restore()


def toe_ouch(cv, x, y, t, a=1.0):
    """Little cartoon pain star by a stubbed toe."""
    for k in range(5):
        ang = k * 2 * math.pi / 5 + t * 2
        cv.drawLine(x + math.cos(ang) * 12, y + math.sin(ang) * 12, x + math.cos(ang) * 28,
                    y + math.sin(ang) * 28, stroke("#ffd23f", 4, a))
